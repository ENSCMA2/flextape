import torch
import os
import torch.nn as nn
import copy
from pytorch_lightning import LightningModule
from pytorch_lightning.core.optimizer import LightningOptimizer

from argparse import ArgumentParser
from torch.utils.data import DataLoader
from torchmetrics import Accuracy
from transformers import (
    GPT2Tokenizer, GPTJForCausalLM, get_linear_schedule_with_warmup, GPTJConfig
)
from torch.optim.lr_scheduler import ReduceLROnPlateau
from .patch import ModifyLinearOutput, ModuleDetector, ModifyLinearInput
# from deepspeed.ops.adam import DeepSpeedCPUAdam, FusedAdam
# from pytorch_lightning.strategies import DeepSpeedStrategy
from ..dataset.zsre_dataloader import Seq2SeqData
from ..utils import label_smoothed_nll_loss, get_kl_diver_loss, NUM_BEAMS, patch_related_args


class GPTJSeq2Seq(LightningModule):
    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)

        parser.add_argument(
            "--train_data_path", type=str,
            # default='data/zsre_data/zsre-train.jsonl',
            default='data/counterfact_data/counterfact-train.jsonl'
        )
        parser.add_argument(
            "--dev_data_path", type=str,
            # default='data/zsre_data/zsre-val.jsonl'
            default='data/counterfact_data/counterfact-val.jsonl'
        )
        # For Edit
        parser.add_argument("--num_beams", type=int, default=NUM_BEAMS)
        parser.add_argument("--batch_size", type=int, default=32)
        parser.add_argument("--lr", type=float, default=3e-5)
        parser.add_argument("--max_length", type=int, default=32)
        parser.add_argument("--weight_decay", type=int, default=0.01)
        parser.add_argument("--total_num_updates", type=int, default=50000)
        parser.add_argument("--warmup_updates", type=int, default=500)
        parser.add_argument("--num_workers", type=int, default=0)
        parser.add_argument("--model_name", type=str, default="EleutherAI/gpt-j-6b")
        parser.add_argument("--eps", type=float, default=0.1)

        # parser.add_argument("--num_beams", type=int, default=NUM_BEAMS)
        # parser.add_argument("--batch_size", type=int, default=24)
        # parser.add_argument("--lr", type=float, default=3e-5)
        # parser.add_argument("--max_length", type=int, default=32)
        # parser.add_argument("--weight_decay", type=int, default=0.01)
        # parser.add_argument("--total_num_updates", type=int, default=50000)
        # parser.add_argument("--warmup_updates", type=int, default=500)
        # parser.add_argument("--num_workers", type=int, default=0)
        # parser.add_argument("--model_name", type=str, default="gpt-j-6B")
        # parser.add_argument("--eps", type=float, default=0.1)
        return parser

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.save_hyperparameters()
        model_dir = os.path.join(self.hparams.cache_dir, self.hparams.model_name) \
            if "cache_dir" in self.hparams else self.hparams.model_name
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            self.tokenizer.padding_side = 'left'
            # self.model = GPTJForCausalLM.from_pretrained(model_dir, device_map='auto', torch_dtype=torch.float16)
            self.model = GPTJForCausalLM.from_pretrained(model_dir)

            # self.config = T5Config.from_json_file(os.path.join(model_dir, 'config.json'))
            # self.model = T5ForConditionalGeneration(config=self.config)
            # state_dict = torch.load(os.path.join(model_dir, 'pytorch_model.bin'))
            # new_state_dict = dict()
            # for key in state_dict.keys():
            #     assert '_forward_module.model.' in key or 'model.' in key
            #     if '_forward_module.model.' in key:
            #         replaced_subkey = '_forward_module.model.'
            #     else:
            #         replaced_subkey = 'model.'
            #     new_state_dict[key.replace(replaced_subkey, '')] = state_dict[key]
            # self.model.load_state_dict(new_state_dict, strict=False)
            # self.device_map = {
            #     0: [_ for _ in range(0, 6)],
            #     1: [_ for _ in range(6, 12)],
            #     2: [_ for _ in range(12, 18)],
            #     3: [_ for _ in range(18, 24)]
            # }
            # self.model.parallelize(device_map=self.device_map)
        except:
            print("The cache can not be used")
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.hparams.model_name, cache_dir=self.hparams.cache_dir)  # have internet
            self.model = GPTJForCausalLM.from_pretrained(self.hparams.model_name, cache_dir=self.hparams.cache_dir)  # have internet
        # self.train_acc = Accuracy()
        # self.valid_acc = Accuracy()
        self.train_acc = Accuracy(task='binary')
        self.valid_acc = Accuracy(task='binary')

    def train_dataloader(self, shuffle=True):
        if not hasattr(self, "train_dataset"):
            self.train_dataset = Seq2SeqData(
                tokenizer=self.tokenizer,
                data_path=self.hparams.train_data_path,
                max_length=self.hparams.max_length,
            )
        return DataLoader(
            self.train_dataset, batch_size=self.hparams.batch_size,
            collate_fn=self.train_dataset.collate_gpt_fn,
            num_workers=self.hparams.num_workers, shuffle=shuffle,drop_last=True
        )

    def val_dataloader(self):
        if not hasattr(self, "val_dataset"):
            self.val_dataset = Seq2SeqData(
                tokenizer=self.tokenizer,
                data_path=self.hparams.dev_data_path,
                max_length=self.hparams.max_length,
                validation=True,
            )
        return DataLoader(
            self.val_dataset,
            batch_size=16,
            collate_fn=self.val_dataset.collate_gpt_fn,
            num_workers=self.hparams.num_workers,drop_last=True
        )

    def forward(self, input_ids, attention_mask, labels=None):
        # batch_size x trg_len x vocab_size
        return self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            use_cache=False,
        )

    def training_step(self, batch, batch_idx=None):
        input_ids = batch["src_input_ids"]
        attention_mask = batch["src_attention_mask"]
        logits = self.forward(input_ids, attention_mask, input_ids).logits

        loss, nll_loss = label_smoothed_nll_loss(
            logits.log_softmax(-1), batch["src_input_ids"],
            epsilon=self.hparams.eps, ignore_index=self.tokenizer.pad_token_id,
        )

        ntokens = batch["src_attention_mask"][:, :].sum()
        loss, nll_loss = loss / ntokens, nll_loss / ntokens
        self.log("nll_loss", nll_loss, on_step=True, on_epoch=False, prog_bar=True, rank_zero_only=True)
        return {"loss": loss}

    def validation_step(self, batch, batch_idx=None):
        # self.model.parallelize(device_map=self.device_map)
        trg = [b["trg"] for b in batch["raw"]]
        # batch["src_input_ids"] = batch["src_input_ids"].to(torch.device(self.hparams.device))
        # batch["src_attention_mask"] = batch["src_attention_mask"].to(torch.device(self.hparams.device))
        pred = self.tokenizer.batch_decode(
            self.model.generate(
                input_ids=batch["src_input_ids"], attention_mask=batch["src_attention_mask"],
                min_length=0, num_beams=self.hparams.num_beams, num_return_sequences=1, use_cache=True
            ),
            skip_special_tokens=True
        )
        acc = torch.tensor(
            [
                p.lower().strip() in [t_.lower().strip() for t_ in t]
                for t, p in zip(trg, pred)
            ]
        ).long()
        self.valid_acc(acc, torch.ones_like(acc))
        self.log("valid_acc", self.valid_acc, on_step=False, on_epoch=True, prog_bar=True, batch_size=len(trg), rank_zero_only=True)
    #
    # def test_step(self, batch, batch_idx=None):
    #     trg = [b["trg"] for b in batch["raw"]]
    #     pred = self.tokenizer.batch_decode(
    #         self.model.generate(
    #             input_ids=batch["src_input_ids"], attention_mask=batch["src_attention_mask"],
    #             min_length=0, num_beams=self.hparams.num_beams, num_return_sequences=1, use_cache=True
    #         ),
    #         skip_special_tokens=True
    #     )
    #     acc = [
    #             p.lower().strip() in [t_.lower().strip() for t_ in t]
    #             for t, p in zip(trg, pred)
    #     ]
    #     acc = torch.tensor(acc).long()
    #     self.valid_acc(acc, torch.ones_like(acc))
    #     self.log("test_acc", self.valid_acc, on_step=False, on_epoch=True, prog_bar=True)

    def configure_optimizers(self):
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p
                    for n, p in self.model.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [
                    p
                    for n, p in self.model.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]

        optimizer = torch.optim.AdamW(
            optimizer_grouped_parameters,
            lr=self.hparams.lr,
            weight_decay=self.hparams.weight_decay,
        )

        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.hparams.warmup_updates,
            num_training_steps=self.hparams.total_num_updates,
        )

        return [optimizer], [
            {"scheduler": scheduler, "interval": "step", "frequency": 1}
        ]
    #     if self.deepspeed_offload:
    #         return DeepSpeedCPUAdam(optimizer_grouped_parameters,
    #                                 lr=self.hparams.lr,
    #                                 weight_decay=self.hparams.weight_decay)
    #     return FusedAdam(optimizer_grouped_parameters,
    #                      lr=self.hparams.lr,
    #                      weight_decay=self.hparams.weight_decay)
    #
    # @property
    # def deepspeed_offload(self) -> bool:
    #     strategy = self.trainer.strategy
    #     if isinstance(strategy, DeepSpeedStrategy):
    #         config = strategy.config['zero_optimization']
    #         return config.get('offload_optimizer') or config.get('offload_param')
    #     return False


class GPTJEditor(nn.Module):

    def __init__(self,
                 model, hidden_size=4096, device=None,
                 max_add_neuron_num=1,
                 activate_loss='non_use', memory_loss='non_use',
                 freeze_model=True, freeze_k=False, freeze_a=False,
                 memory_size=50000,
                 amplify_v=False, amplify_con=10.0,
                 drop_num=0, drop_rate=0.5,
                 act_margin_val=0.0, margin_val1=0.0, margin_val2=0.0,args=None
                 ):
        super().__init__()
        self.model = copy.deepcopy(model)
        self.args=args
        if(len(args.gpus) == 2):
            device_map = {
                0: [_ for _ in range(0, 14)],
                1: [_ for _ in range(14, 28)],
            }
        elif(len(args.gpus) == 3):
            device_map = {
                0: [_ for _ in range(0, 9)],
                1: [_ for _ in range(9, 18)],
                2: [_ for _ in range(18, 28)],
            }
        elif(len(args.gpus) == 4):
            device_map = {
                0: [_ for _ in range(0, 7)],
                1: [_ for _ in range(7, 14)],
                2: [_ for _ in range(14, 21)],
                3: [_ for _ in range(21, 28)]
            }
        else:
            raise ValueError('Device is not enough!')
        self.model.model.parallelize(device_map=device_map)
        self.original_model = copy.deepcopy(model)
        self.hidden_size = hidden_size
        self.device = device
        self.max_add_neuron_num = max_add_neuron_num
        self.memory_size = memory_size
        self.activate_loss = activate_loss
        self.memory_loss = memory_loss
        self.freeze_model = freeze_model
        self.freeze_a = freeze_a
        self.amplify_con = amplify_con
        if self.freeze_model:
            for p in self.model.parameters():
                p.requires_grad = False

        # initialization, may be re-initialized after every edit
        self.model_named_modules = None
        self.get_named_modules()

        self.editors = []
        self.detectors = []

        self.train_memories = {}
        self.val_memories = {}

        self.amplify_v = amplify_v
        self.freeze_k = freeze_k

        self.drop_num = drop_num
        self.drop_rate = drop_rate

        self.act_margin_val = act_margin_val
        self.margin_val1 = margin_val1
        self.margin_val2 = margin_val2
        self.device_distribution = None

        self.detected_modules=[
            ('model.transformer.h.27.mlp', 'fc_in'),
        ]

        self.name_edit_type = {
            'model.transformer.h.27.mlp.fc_in': 'output',
            'model.transformer.h.27.mlp.fc_out': 'input'
        }

    def reset_model(self, model, clear_memory):
        self.model = copy.deepcopy(model)
        if self.freeze_model:
            for p in self.model.parameters():
                p.requires_grad = False
        self.model_named_modules = None
        self.get_named_modules()
        self.editors = []
        for ms in [self.train_memories, self.val_memories]:
            for m in ms.values():
                del m[-1 * clear_memory:]

    def clear_memory(self):
        # clear all memories
        self.memories = {}

    def clear_detectors(self):
        for d in self.detectors:
            self.model_named_modules[d['module']]._modules[d['child']] = d['original_module']
        self.detectors = []
        # self.get_named_modules()

    def clear_editors(self):
        for e in self.editors:
            self.model_named_modules[e['module']]._modules[e['child']] = e['original_module']
        self.editors = []
        # self.get_named_modules()

    def set_device_distribution(self, device_distribution):
        self.device_distribution = device_distribution

    def set_editors(self, batch=None, init_weights=None, error_count=1, select_index=0):
        # before every turn, we call this function to set the editors
        self.get_editors(
            batch,
            init_weights=dict() if init_weights is None else init_weights,
            error_count=error_count, select_index=select_index
        )
        for e in self.editors:
            # TODO
            # e['editor'] = e['editor'].to(self.model_named_modules[e['module']]._modules[e['child']].weight.device)
            # self.model_named_modules[e['module']]._modules[e['child']] = e['editor'].to(torch.float16)
            self.model_named_modules[e['module']]._modules[e['child']] = e['editor']

    def set_detectors(self):
        for d in self.detectors:
            # TODO
            # d['detector'] = d['detector'].to(self.model_named_modules[d['module']]._modules[d['child']].weight.device)
            # self.model_named_modules[d['module']]._modules[d['child']] = d['detector'].to(torch.float16)
            self.model_named_modules[d['module']]._modules[d['child']] = d['detector']

    def step(self):
        # we assign the trained linear layer to the edit target
        for e in self.editors:
            self.model_named_modules[e['module']]._modules[e['child']] = e['editor'].assign_layer()
        self.editors = []
        self.get_named_modules()

    def lock_hidden_detectors(self):
        for d in self.detectors:
            d['detector'].turn_off_hidden()

    def unlock_hidden_detectors(self):
        for d in self.detectors:
            d['detector'].turn_on_hidden()

    def lock_memory_detectors(self):
        for d in self.detectors:
            d['detector'].turn_off_memory()

    def unlock_memory_detectors(self):
        for d in self.detectors:
            d['detector'].turn_on_memory()

    def insert_hidden_detector(self):
        self.get_detectors(
            detected_modules=self.detected_modules,
            memory_loc='bart_seq', hidden_loc='bart_seq'
        )
        self.set_detectors()

    def get_hidden(self, index=None):
        res = dict()
        for d in self.detectors:
            k = d['module'] + '.' + d['child']
            v = d['detector'].get_hidden()
            res[k] = v[index] if index is not None else v
        return res

    def feed_one_memory(self, m):
        for k, v in m.items():
            assert k in self.train_memories
            self.train_memories[k] += [v]
            self.val_memories[k] += [v]
            print("This is a update and now we have {} train memories and {} val_memories for module {}".format(
                len(self.train_memories[k]), len(self.val_memories[k]), k
            ))

    def construct_memory(self, data: DataLoader, memory_size, device, update=False, memory_use='train'):
        self.detectors = []
        self.model.eval()
        self.model.model.parallelize(device_map = {
                0: [_ for _ in range(0, 14)],
                1: [_ for _ in range(14, 28)],
            })
        self.get_detectors(
            detected_modules=self.detected_modules,
            memory_loc='bart_seq', hidden_loc='bart_seq'
        )
        self.set_detectors()
        for d in self.detectors:
            if not update:
                d['detector'].turn_on_memory()
            else:
                d['detector'].turn_on_hidden()
        # bar = tqdm(enumerate(data), total=len(data.dataset) // data.batch_size)
        from tqdm import tqdm
        for _, batch in tqdm(enumerate(data), total=len(data), desc='Building Memory!!'):
            input_ids = batch["src_trg_input_ids"].to(device)
            attention_mask = batch["src_trg_attention_mask"].to(device)
            # decoder_input_ids = batch["trg_input_ids"].to(device)
            # decoder_attention_mask = batch["trg_attention_mask"].to(device)
            for d in self.detectors:
                d['detector'].feed_memory_mask(attention_mask)
            # self.model(
            #     input_ids, attention_mask,
            #     decoder_input_ids[:, :-1], decoder_attention_mask[:, :-1]
            # )
            self.model(
                input_ids, attention_mask
            )

        for d in self.detectors:
            name = d['module']+'.'+d['child']
            if not update:
                # this is for construction
                if memory_use == 'train':
                    self.train_memories[name] = d['detector'].get_memory()
                else:
                    self.val_memories[name] = d['detector'].get_memory()
            else:
                assert name in self.train_memories
                # print(len(list(torch.split(d['detector'].get_hidden(), 1))))
                self.train_memories[name] += list(torch.split(d['detector'].get_hidden(), 1))[1:-1]
                self.val_memories[name] += list(torch.split(d['detector'].get_hidden(), 1))[1:-1]
                print("This is a update and now we have {} train memories and {} val_memories".format(
                    len(self.train_memories[name]), len(self.val_memories[name])
                ))
            self.model_named_modules[d['module']]._modules[d['child']] = d['original_module']
        self.detectors = []
        # self.get_named_modules()

    def get_named_modules(self):
        # For now we just edit one linear layer once
        self.model_named_modules = None
        self.model_named_modules = {x[0]: x[1] for x in self.model.named_modules()}

    def get_editors(self, batch, init_weights=None, error_count=None, select_index=None):
        name_edit_type = self.name_edit_type
        for name, edit_type in name_edit_type.items():
            e_tmp = dict()
            n = name.rsplit('.', 1)
            e_tmp['module'], e_tmp['child'] = n[0], n[-1]
            if edit_type == 'input':
                e_tmp['editor'] = ModifyLinearInput(
                    self.model_named_modules[n[0]].__getattr__(n[-1]),
                    amplify=self.amplify_v, freeze_a=self.freeze_a,
                    amplify_con=self.amplify_con,
                    add_neuron_num=self.max_add_neuron_num if error_count is None else error_count,
                )
            else:
                init_weight = init_weights[name] if name in init_weights.keys() else None
                train_memo, val_memo = None, None
                if name in self.train_memories.keys():
                    train_memo = self.train_memories[name]
                    val_memo = self.val_memories[name]
                e_tmp['editor'] = ModifyLinearOutput(
                    self.model_named_modules[n[0]].__getattr__(n[-1]),
                    init_weight=init_weight,  freeze=self.freeze_k,
                    activate_loss=self.activate_loss, memory_loss=self.memory_loss,
                    train_memories=train_memo, val_memories=val_memo,
                    drop_num=self.drop_num, drop_rate=self.drop_rate,
                    act_loc=0 if select_index is None else select_index,
                    add_neuron_num=self.max_add_neuron_num if error_count is None else error_count
                )
            e_tmp['original_module'] = self.model_named_modules[n[0]].__getattr__(n[-1])
            self.editors.append(e_tmp)

    def get_detectors(self, *args, **kwargs):
        detected_modules = kwargs.get("detected_modules")
        memory_loc = kwargs.get("memory_loc") if "memory_loc" in kwargs else 0
        hidden_loc = kwargs.get("hidden_loc") if "hidden_loc" in kwargs else 0
        mode = kwargs.get("mode") if "mode" in kwargs else "input"
        for (module_name, child) in detected_modules:
            detector = ModuleDetector(
                model=self.model_named_modules[module_name]._modules[child],
                memory_size=self.memory_size, mode=mode,
                memory_loc=memory_loc, hidden_loc=hidden_loc
            )
            self.detectors.append({
                'module': module_name, 'child': child,
                'detector': detector, 'original_module': self.model_named_modules[module_name]._modules[child]
            })

    def get_act_loss(self):
        act_loss = 0
        for e in self.editors:
            if isinstance(e['editor'], ModifyLinearOutput):
                act_loss_ = e['editor'].get_act_loss()
                if act_loss_ is not None:
                    act_loss += act_loss_
        return act_loss

    def get_memo_loss(self):
        memo_loss = 0
        for e in self.editors:
            if isinstance(e['editor'], ModifyLinearOutput):
                memo_loss_ = e['editor'].get_memo_loss()
                if memo_loss_ is not None:
                    memo_loss += memo_loss_
        return memo_loss

    def repeat_tensor(self, t):
        return torch.repeat_interleave(t, self.drop_num + 1, dim=0)

    def feed_kl_input(self, memo_loader, his_edit_data, total_loc_num):
        self.memo_loader = memo_loader
        self.total_loc_num = total_loc_num
        self.his_edit_data = his_edit_data

    def do_not_act_val(self):
        for e in self.editors:
            e['editor'].activate_loss = 'non_use'

    def do_act_val(self):
        for e in self.editors:
            e['editor'].activate_loss = self.activate_loss

    def forward(self, input_ids, attention_mask, target_length, return_loss=False):
        # gen = self.drop_num > 0 and self.training
        # target_for_loss = self.repeat_tensor(decoder_input_ids[:, 1:]) if gen else decoder_input_ids[:, 1:]
        # target_for_loss = decoder_input_ids[:, 1:].to(self.device)
        res = dict()
        input_ids = input_ids.to(self.device)
        attention_mask = attention_mask.to(self.device)
        if(len(self.args.gpus) == 2):
            device_map = {
                0: [_ for _ in range(0, 14)],
                1: [_ for _ in range(14, 28)],
            }
        elif(len(self.args.gpus) == 3):
            device_map = {
                0: [_ for _ in range(0, 9)],
                1: [_ for _ in range(9, 18)],
                2: [_ for _ in range(18, 28)],
            }
        elif(len(self.args.gpus) == 4):
            device_map = {
                0: [_ for _ in range(0, 7)],
                1: [_ for _ in range(7, 14)],
                2: [_ for _ in range(14, 21)],
                3: [_ for _ in range(21, 28)]
            }
        else:
            raise ValueError('Device is not enough!')
        self.model.model.parallelize(device_map=device_map)
        # model_named_modules = {x[0]:x[1] for x in self.model.model.transformer.named_modules()}
        # for key, value in self.device_distribution.items():
        #
        #     key = key.rpartition('.')[0]
        #     assert key in model_named_modules
        #     model_named_modules[key].to(value)

        # inputs_embeds = self.model.model.model.embed_tokens(input_ids)
        # batch_size, seq_length = input_ids.shape
        # past_key_values_length = 0
        # device = input_ids.device if input_ids is not None else inputs_embeds.device
        # position_ids = torch.arange(past_key_values_length, seq_length + past_key_values_length, dtype=torch.long,
        #                             device=device)
        # position_ids = position_ids.unsqueeze(0).view(-1, seq_length)
        # attention_mask = self.model.model.model._prepare_decoder_attention_mask(attention_mask,
        #                                                                         (batch_size, seq_length), inputs_embeds,
        #                                                                         past_key_values_length)
        # hidden_states = inputs_embeds
        # hidden_states = hidden_states.to('cuda:2')
        # attention_mask = attention_mask.to('cuda:2')
        # position_ids = position_ids.to('cuda:2')
        # decoder_layer = self.model.model.model.layers[31]
        #
        # layer_outputs = decoder_layer.forward(hidden_states, attention_mask=attention_mask,position_ids=position_ids,use_cache=True)


        if return_loss:
            loss = self.model(
                input_ids, attention_mask, labels=input_ids
            ).loss
            return loss
        output = self.model(
            input_ids, attention_mask
        )
        logits = output.logits[:, -target_length:, :]
        loss, nll_loss = label_smoothed_nll_loss(
            lprobs=logits.log_softmax(-1), target=input_ids[:,-target_length:],
            epsilon=self.model.hparams.eps, ignore_index=self.model.tokenizer.pad_token_id,
        )
        ntokens = attention_mask[:, -target_length:].sum()
        loss, nll_loss = loss / ntokens, nll_loss / ntokens
        res['logtis'] = logits
        res['loss'] = loss
        if self.activate_loss != 'non_use':
            res['act_loss'] = self.get_act_loss()
        if self.memory_loss != 'non_use':
            if self.memory_loss.startswith('kl'):
                self.do_not_act_val()
                res['memo_loss'] = get_kl_diver_loss(
                    original_model=self.original_model, post_model=self.model, memo_loader=self.memo_loader,
                    device=self.device, total_loc_num=self.total_loc_num, his_edit_data=self.his_edit_data
                )
                if self.training:
                    self.do_act_val()
            else:
                res['memo_loss'] = self.get_memo_loss()
        return res

class GPTJSeq2SeqEditor(LightningModule):

    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        return patch_related_args(parser)

    def __init__(self, *args, **kwargs):
        super().__init__()
        add_neuron_num = kwargs.get('add_neuron_num')
        self.save_hyperparameters()
        self.current_device = torch.device('cuda', self.hparams.gpus[0])
        self.editor = GPTJEditor(
            # model=T5Seq2Seq.load_from_checkpoint(self.hparams.model_path, strict=False),
            model=GPTJSeq2Seq(**vars(self.hparams)),
            max_add_neuron_num=self.hparams.max_add_neuron_num,
            freeze_model=self.hparams.freeze_model, freeze_k=self.hparams.freeze_k, freeze_a=self.hparams.freeze_a,
            memory_size=self.hparams.memory_size, memory_loss=self.hparams.memory_loss,
            amplify_v=self.hparams.amplify_v, activate_loss=self.hparams.activate_loss,
            act_margin_val=self.hparams.act_margin_val, margin_val1=self.hparams.margin_val1,
            margin_val2=self.hparams.margin_val2, device=self.current_device,args=self.hparams
        )
        # if this is a continuation of previous experiments, we need extend the size of the edited layer
        if add_neuron_num is not None:
            for _ in range(add_neuron_num):
                self.editor.set_editors()
                self.editor.step()
        # self.edit_acc = Accuracy()
        self.edit_acc = Accuracy(task='binary')
        self.val_loader = None
        self.valid_memory_loss = []
        self.valid_metric = []
        self.save_ckpt = 0
        self.stop_editing = False
        self.start_example_editing = False
        self.BIG_CONSTANT = 10000
        self.has_stepped = False

    def on_train_start(self):
        self.valid_memory_loss = []
        self.valid_metric = []
        self.save_ckpt = 0
        self.start_example_editing = False
        self.stop_editing = False
        self.has_stepped = False

    @staticmethod
    def early_stop_editing(metrics, mode='min', thd=0.0, patience=1):
        best_step = 0
        for step, vm in enumerate(metrics):
            if mode == 'min':
                if vm < metrics[best_step] - thd:
                    best_step = step
            else:
                if vm > metrics[best_step] + thd:
                    best_step = step

        if best_step < len(metrics) - patience:
            return True
        else:
            return False

    @staticmethod
    def save_editing_ckpt(metrics, mode='min'):
        # save the model if new val metric is attained
        return (mode == 'min' and min(metrics) == metrics[-1]) or (mode == 'max' and max(metrics) == metrics[-1])

    def fed_val_loader(self, dl):
        self.val_loader = dl

    def reset(self, clear_memory):
        self.editor.reset_model(
            GPTJSeq2Seq.load_from_checkpoint(self.hparams.model_path),
            clear_memory=clear_memory
        )

    def joint_training(self, batch, batch_idx=None):
        input_ids = batch["src_trg_input_ids"]
        target_length = batch['trg_input_ids'].size(1)
        res = self.editor(
            input_ids, batch["src_trg_attention_mask"], target_length
        )
        loss = res['loss']
        if self.hparams.activate_loss != "non_use":
            self.log("al", res['act_loss'], on_step=True, on_epoch=False, prog_bar=True, batch_size=input_ids.size(0))
            loss = loss + self.hparams.alc * res['act_loss'].to(loss.device)
        if self.hparams.memory_loss != 'non_use':
            self.log("ml", res['memo_loss'], on_step=True, on_epoch=False, prog_bar=True, batch_size=input_ids.size(0))
            loss = loss + self.hparams.mlc * res['memo_loss'].to(loss.device)
        return {"loss": loss}

    def training_step(self, batch, batch_idx=None, optimizer_idx=None):
        return self.joint_training(batch, batch_idx)

    def joint_validation(self, batch, batch_idx=None):
        stop_editing, save_ckpt = False, False
        batch["src_trg_input_ids"] = batch["src_trg_input_ids"].to(self.current_device)
        batch["src_trg_attention_mask"] = batch["src_trg_attention_mask"].to(self.current_device)
        batch["src_input_ids"] = batch["src_input_ids"].to(self.current_device)
        batch["src_attention_mask"] = batch["src_attention_mask"].to(self.current_device)
        batch["trg_input_ids"] = batch["trg_input_ids"].to(self.current_device)
        batch["trg_attention_mask"] = batch["trg_attention_mask"].to(self.current_device)
        input_ids = batch["src_trg_input_ids"]
        b_size = input_ids.size(0)
        target_length = batch['trg_input_ids'].size(1)
        res = self.editor(
            input_ids, batch["src_trg_attention_mask"], target_length
        )
        self.log("val_loss", res['loss'], on_step=False, on_epoch=True, prog_bar=True, batch_size=b_size)

        if self.current_epoch >= self.hparams.start_val_epoch:
            self.editor.do_not_act_val()
            model_gen = self.editor.model.model.generate(
                input_ids=batch["src_input_ids"], attention_mask=batch["src_attention_mask"],
                min_length=1, num_beams=NUM_BEAMS, num_return_sequences=1, use_cache=True
            )
            self.editor.do_act_val()
            target_len = batch["trg_input_ids"].size(1)
            edit_acc = model_gen[:, :target_len].equal(batch["trg_input_ids"])
            if self.hparams.use_val == 1:
                if edit_acc:
                    self.valid_memory_loss.append(res['memo_loss'])
                    stop_editing = float(self.early_stop_editing(
                        metrics=self.valid_memory_loss, thd=0.001,
                        patience=self.hparams.early_patience, mode='min'
                    ))
                    save_ckpt = float(self.save_editing_ckpt(metrics=self.valid_memory_loss, mode='min') or (stop_editing == 1))
            else:
                stop_editing = float(edit_acc)
                save_ckpt = edit_acc

            if self.hparams.memory_loss != 'non_use' and not self.hparams.memory_loss.startswith('kl'):
                self.log("v_ml", res['memo_loss'], on_step=False, on_epoch=True, prog_bar=True, batch_size=b_size)

        self.save_ckpt += save_ckpt
        self.stop_editing = stop_editing
        if self.stop_editing == 1:
            self.editor.step()
            self.has_stepped = True
        self.log("stop_editing", float(stop_editing), on_step=False, on_epoch=True, prog_bar=True)
        self.log("save_ckpt", self.save_ckpt, on_step=False, on_epoch=True, prog_bar=True)

    def validation_step(self, batch, batch_idx=None):
        self.joint_validation(batch, batch_idx)

    def memorize(self, train_memory_data: DataLoader, device, update, val_memory_data: DataLoader = None):
        self.editor.construct_memory(
            data=train_memory_data, device=device,
            memory_size=self.hparams.memory_size, update=update, memory_use='train'
        )
        if not update:
            self.editor.construct_memory(
                data=val_memory_data, device=device,
                memory_size=self.hparams.memory_size, update=update, memory_use='val'
            )

    def get_optimizer(self, params, lr=None, optim=None):
        if lr is None:
            lr = self.hparams.lr
        if optim is None:
            optim = self.hparams.optim
        if optim == "adam":
            return torch.optim.Adam(params=params, lr=lr, weight_decay=self.hparams.weight_decay)
        if optim == 'rmsprop':
            return torch.optim.RMSprop(params=params, lr=lr)
        if optim == 'sgd':
            return torch.optim.SGD(params=params, lr=lr, weight_decay=self.hparams.weight_decay, momentum=0.9)

    def configure_optimizers(self):
        # for the joint editing style, we just need one parameter
        parameters = [p for p in self.editor.parameters() if p.requires_grad]
        optimizer = self.get_optimizer(parameters)

        lr_scheduler = ReduceLROnPlateau(
            optimizer=optimizer, mode='min',
            factor=self.hparams.lr_scheduler_factor,
            patience=self.hparams.lr_scheduler_patience,
            threshold=0.05
        )

        lr_scheduler_config = {
            "scheduler": lr_scheduler,
            "interval": "epoch", "frequency": self.hparams.check_val_every_n_epoch,
            "monitor": "val_loss", "strict": True
        }
        optimizer_list = [optimizer]
        lr_scheduler_config_list = [lr_scheduler_config]

        return optimizer_list, lr_scheduler_config_list
