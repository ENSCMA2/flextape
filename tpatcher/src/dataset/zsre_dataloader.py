import jsonlines
import logging
import random
import torch
from torch.utils.data import Dataset
# from transformers import LlamaTokenizer, GPT2Tokenizer
from transformers import GPT2Tokenizer

LOG = logging.getLogger(__name__)
LOG.setLevel(level=logging.DEBUG)

def data_split(dataset, ratio, shuffle=True):
    res, start = {}, 0
    offsets = {n: int(len(dataset)*r) for n, r in ratio.items()}
    if shuffle:
        random.shuffle(dataset)
    for n, offset in offsets.items():
        res[n] = dataset[start:start + offset]
        start += offset
    return res


class Seq2SeqData(Dataset):
    def __init__(self, tokenizer, data_path, max_length=32, example_repeat=16,
                 all_views=False, return_view=5, validation=False, edit=False):
        """
        :param tokenizer:
        :param data_path:
        :param max_length:
        :param validation:
        """
        super().__init__()
        self.tokenizer = tokenizer
        self.validation = validation
        self.edit = edit
        self.data = []
        self.example_repeat = example_repeat

        with jsonlines.open(data_path) as f:
            for d in f:
                # we only edit the data with the only one answer
                if validation:
                    self.data.append({
                        "input": d["input"],
                "output": d["output"],
                "rephrases": [d["input"]]
                            })
                else:
                    self.data.append({
                        "input": d["input"],
                "output": d["output"],
                "rephrases": [d["input"]]
                            })
                    break

        self.max_length = max_length
        self.all_views = all_views
        self.return_view = return_view

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        res = {
            "src": self.data[item]["input"],
            "trg": self.data[item]["output"],
            "rephrases": self.data[item]["rephrases"]# random.sample(
                # self.data[item]["rephrases"],
                # k=min(self.return_view, len(self.data[item]["rephrases"]))) if not self.all_views else self.data[item][
                # "rephrases"],
            # 'loc': self.data[item]["loc"] if self.edit else None,
            # 'loc_ans': self.data[item]["loc_ans"] if self.edit else None,
        }
        if 'portability' in self.data[item].keys():
            res['portability'] = self.data[item]["portability"] if self.edit else None
            res['portability_ans'] = self.data[item]["portability_ans"] if self.edit else None
        if 'unrelated_relation' in self.data[item].keys():
            res['unrelated_relation'] = self.data[item]["unrelated_relation"] if self.edit else None
            res['unrelated_relation_ans'] = self.data[item]["unrelated_relation_ans"] if self.edit else None
        if 'distracting_neighborhood' in self.data[item].keys():
            res['distracting_neighborhood'] = self.data[item]["distracting_neighborhood"] if self.edit else None
            res['distracting_neighborhood_ans'] = self.data[item]["distracting_neighborhood_ans"] if self.edit else None
        if 'inverse' in self.data[item].keys():
            res['inverse'] = self.data[item]["inverse"] if self.edit else None
            res['inverse_ans'] = self.data[item]["inverse_ans"] if self.edit else None
        if 'tongyici' in self.data[item].keys():
            res['tongyici'] = self.data[item]["tongyici"] if self.edit else None
            res['tongyici_ans'] = self.data[item]["tongyici_ans"] if self.edit else None

        return res

    def collate_fn(self, batch):
        # if isinstance(self.tokenizer, LlamaTokenizer) or isinstance(self.tokenizer, GPT2Tokenizer):
        if isinstance(self.tokenizer, GPT2Tokenizer):
            return self.collate_gpt_fn(batch)

        batches = {}
        for name in ("src", ) + (() if self.validation else ("trg", )):
            tokenizer_input = [b[name] for b in batch]
            tokenizer_output = self.tokenizer(
                tokenizer_input, return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )
            for k, v in tokenizer_output.items():
                if name == 'src' and self.edit and self.example_repeat > 1:
                    v_ = [v for _ in range(self.example_repeat)]
                    batches["{}_{}".format(name, k)] = torch.cat(v_, dim=0)
                else:
                    batches["{}_{}".format(name, k)] = v
        if self.edit:
            assert len(batch) == 1
            tokenizer_trg = self.tokenizer(
                [b["trg"][0] for b in batch], return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )
            for k, v in tokenizer_trg.items():
                if self.example_repeat == 1:
                    batches["{}_{}".format("trg", k)] = v
                else:
                    v_ = [v for _ in range(self.example_repeat)]
                    batches["{}_{}".format("trg", k)] = torch.cat(v_, dim=0)

            tokenize_rephrases = self.tokenizer(
                batch[0]["rephrases"],
                return_tensors="pt",
                padding=True,
                max_length=self.max_length,
                truncation=True,
            )
            for k, v in tokenize_rephrases.items():
                batches['{}_{}'.format('re_src', k)] = v

            loc_tokenizer_trg = self.tokenizer(
                [b["loc_ans"] for b in batch], return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )
            loc_tokenizer_inp = self.tokenizer(
                [b["loc"] for b in batch], return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )

            portability_tokenizer_inp = self.tokenizer(
                [b["portability"] for b in batch], return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )
            portability_tokenizer_trg = self.tokenizer(
                [b["portability_ans"] for b in batch], return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )
            edit_loc={
                'src_input_ids': loc_tokenizer_inp['input_ids'],
                'src_attention_mask': loc_tokenizer_inp['attention_mask'],
                'trg_input_ids': loc_tokenizer_trg['input_ids'],
                'trg_attention_mask': loc_tokenizer_trg['attention_mask'],
            }

            edit_portability={
                'src_input_ids': portability_tokenizer_inp['input_ids'],
                'src_attention_mask': portability_tokenizer_inp['attention_mask'],
                'trg_input_ids': portability_tokenizer_trg['input_ids'],
                'trg_attention_mask': portability_tokenizer_trg['attention_mask'],
            }
            batches['edit_loc'], batches['edit_portability'] = edit_loc, edit_portability



        if "trg_input_ids" in batches:
            # batches["trg_input_ids"][:, 0] = self.tokenizer.eos_token_id
            b_size = batches["trg_input_ids"].size(0)
            eos = torch.tensor([[self.tokenizer.eos_token_id] for _ in range(b_size)])
            mask = torch.tensor([[1] for _ in range(b_size)])
            batches["trg_input_ids"] = torch.cat((eos, batches["trg_input_ids"]), dim=-1)
            batches["trg_attention_mask"] = torch.cat((mask, batches["trg_attention_mask"]), dim=-1)

        batches["raw"] = batch
        return batches

    def collate_gpt_fn(self, batch):
        batches = {}
        tokenizer_input = [b['src'] for b in batch]

        tokenizer_output = self.tokenizer(
            tokenizer_input, return_tensors="pt",
            padding=True, max_length=self.max_length,
            truncation=True,
        )
        for k, v in tokenizer_output.items():
            if self.edit and self.example_repeat > 1:
                v_ = [v for _ in range(self.example_repeat)]
                batches["{}_{}".format('src', k)] = torch.cat(v_, dim=0)
            else:
                batches["{}_{}".format('src', k)] = v
        input_output = []
        for b in batch:
            if type(b["trg"] == str):
                trgt = b["trg"]
            else:
                trgt = b["trg"]["str"]
            input_output.append(b["src"] + " " + str(trgt))
        tokenized_input_output = self.tokenizer(
            input_output, return_tensors="pt",
            padding=True, max_length=self.max_length,
            truncation=True,
        )
        for k, v in tokenized_input_output.items():
            if self.edit and self.example_repeat > 1:
                v_ = [v for _ in range(self.example_repeat)]
                batches["{}_{}".format('src_trg', k)] = torch.cat(v_, dim=0)
            else:
                batches["{}_{}".format('src_trg', k)] = v
        def stringify(what):
            if type(what) == str:
                return what
            return str(what["str"])
        tokenizer_trg = self.tokenizer(
            [' ' + stringify(b["trg"]) for b in batch], return_tensors="pt",
            padding=True, max_length=self.max_length,
            truncation=True,
        )
        for k, v in tokenizer_trg.items():
            if self.example_repeat == 1:
                batches["{}_{}".format("trg", k)] = v
            else:
                v_ = [v for _ in range(self.example_repeat)]
                batches["{}_{}".format("trg", k)] = torch.cat(v_, dim=0)

        if self.edit:
            rephrase_input_output = [b['rephrases'][0] + ' ' + stringify(b['trg']) for b in batch]
            tokenize_rephrases = self.tokenizer(
                rephrase_input_output,
                return_tensors="pt",
                padding=True,
                max_length=self.max_length,
                truncation=True,
            )
            for k, v in tokenize_rephrases.items():
                batches['{}_{}'.format('re_src_trg', k)] = v

            loc_tokenizer_inp_trg = self.tokenizer(
                [b["loc"] + ' ' + b["loc_ans"] for b in batch], return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )
            loc_tokenizer_trg = self.tokenizer(
                [' ' + b["loc_ans"] for b in batch], return_tensors="pt",
                padding=True, max_length=self.max_length,
                truncation=True,
            )

            if 'portability' in batch[0].keys():
                portability_tokenizer_inp_trg = self.tokenizer(
                    [b["portability"] + ' ' + b["portability_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
                portability_tokenizer_trg = self.tokenizer(
                    [' ' + b["portability_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
            if 'unrelated_relation' in batch[0].keys():
                unrelated_relation_tokenizer_inp_trg = self.tokenizer(
                    [b["unrelated_relation"] + ' ' + b["unrelated_relation_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
                unrelated_relation_tokenizer_trg = self.tokenizer(
                    [' ' + b["unrelated_relation_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
            if 'distracting_neighborhood' in batch[0].keys():
                distracting_tokenizer_inp_trg = self.tokenizer(
                    [b["distracting_neighborhood"] + ' ' + b["distracting_neighborhood_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
                distracting_tokenizer_trg = self.tokenizer(
                    [' ' + b["distracting_neighborhood_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
            if 'inverse' in batch[0].keys():
                inverse_tokenizer_inp_trg = self.tokenizer(
                    [b["inverse"] + ' ' + b["inverse_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
                inverse_tokenizer_trg = self.tokenizer(
                    [' ' + b["inverse_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
            if 'tongyici' in batch[0].keys():
                tongyici_tokenizer_inp_trg = self.tokenizer(
                    [b["tongyici"] + ' ' + b["tongyici_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )
                tongyici_tokenizer_trg = self.tokenizer(
                    [' ' + b["tongyici_ans"] for b in batch], return_tensors="pt",
                    padding=True, max_length=self.max_length,
                    truncation=True,
                )

            edit_loc={
                'src_trg_input_ids': loc_tokenizer_inp_trg['input_ids'],
                'src_trg_attention_mask': loc_tokenizer_inp_trg['attention_mask'],
                'trg_input_ids': loc_tokenizer_trg['input_ids'],
            }
            batches['edit_loc'] = edit_loc

            if 'portability' in batch[0].keys():
                edit_portability={
                    'src_trg_input_ids': portability_tokenizer_inp_trg['input_ids'],
                    'src_trg_attention_mask': portability_tokenizer_inp_trg['attention_mask'],
                    'trg_input_ids': portability_tokenizer_trg['input_ids'],
                }
                batches['edit_portability'] = edit_portability

            if 'unrelated_relation' in batch[0].keys():
                edit_unrelated_relation={
                    'src_trg_input_ids': unrelated_relation_tokenizer_inp_trg['input_ids'],
                    'src_trg_attention_mask': unrelated_relation_tokenizer_inp_trg['attention_mask'],
                    'trg_input_ids': unrelated_relation_tokenizer_trg['input_ids'],
                }
                batches['edit_unrelated_relation'] = edit_unrelated_relation

            if 'distracting_neighborhood' in batch[0].keys():
                edit_distracting={
                    'src_trg_input_ids': distracting_tokenizer_inp_trg['input_ids'],
                    'src_trg_attention_mask': distracting_tokenizer_inp_trg['attention_mask'],
                    'trg_input_ids': distracting_tokenizer_trg['input_ids'],
                }
                batches['edit_distracting'] = edit_distracting

            if 'inverse' in batch[0].keys():
                edit_inverse={
                    'src_trg_input_ids': inverse_tokenizer_inp_trg['input_ids'],
                    'src_trg_attention_mask': inverse_tokenizer_inp_trg['attention_mask'],
                    'trg_input_ids': inverse_tokenizer_trg['input_ids'],
                }
                batches['edit_inverse'] = edit_inverse
            if 'tongyici' in batch[0].keys():
                edit_tongyici={
                    'src_trg_input_ids': tongyici_tokenizer_inp_trg['input_ids'],
                    'src_trg_attention_mask': tongyici_tokenizer_inp_trg['attention_mask'],
                    'trg_input_ids': tongyici_tokenizer_trg['input_ids'],
                }
                batches['edit_tongyici'] = edit_tongyici

        batches["raw"] = batch
        return batches


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--val_ratio", type=float, default=0.075)
    parser.add_argument("--edit_ratio", type=float, default=0.025)
    parser.add_argument("--train_ratio", type=float, default=0.9)
    args = parser.parse_args()
    assert args.val_ratio + args.edit_ratio + args.train_ratio == 1

    p_data_path = "/home/halevy/flextape/data/seesaw_cf_P101_False_100_train.jsonl"
    p_test_data_path = "/home/halevy/flextape/data/seesaw_cf_P101_False_100_test.jsonl"
    train_data_path = '/home/halevy/flextape/data/seesaw101_train.jsonl'
    edit_data_path = '/home/halevy/flextape/data/seesaw101_edit.jsonl'
    val_data_path = '/home/halevy/flextape/data/seesaw101_val.jsonl'
    test_data_path = '/home/halevy/flextape/data/seesaw101_dev_kilt.jsonl'
    paths = {
        "train": train_data_path, "val": val_data_path,
        "edit": edit_data_path, "test": test_data_path
    }
    data, test_data = [], []
    print("Loading data")
    with jsonlines.open(p_data_path) as data_file:
        for d in data_file:
            new_d = {
                "input": d["requested_rewrite"]["prompt"].replace("{}", d["requested_rewrite"]["subject"]),
                "output": d["requested_rewrite"]["target_new"]["str"],
                "rephrases": [d["requested_rewrite"]["prompt"].replace("{}", d["requested_rewrite"]["subject"])]
            }
            data.append(new_d)

    print("Loading test data")
    with jsonlines.open(p_test_data_path) as test_file:
        for d in test_file:
            new_d = {
                "input": d["requested_rewrite"]["prompt"].replace("{}", d["requested_rewrite"]["subject"]),
                "output": d["requested_rewrite"]["target_new"]["str"],
                "rephrases": [d["requested_rewrite"]["prompt"].replace("{}", d["requested_rewrite"]["subject"])]
            }
            test_data.append(new_d)

    print("Splitting the existing data according to the ratios")
    data_splits = data_split(
        data, ratio={"train": args.train_ratio, "val": args.val_ratio, "edit": args.edit_ratio}
    )

    data_splits["test"] = test_data

    for k, v in data_splits.items():
        print("For {} data, we got {} data points".format(k, len(v)))
    for name, path in paths.items():
        with jsonlines.open(path, 'w') as w:
            for t_d in data_splits[name]:
                w.write(t_d)


"""

Loading data
Loading test data
Splitting the existing data according to the ratios
For train data, we got 228912 data points
For val data, we got 12208 data points
For edit data, we got 3052 data points
For test data, we got 27644 data points

train-new.jsonl
{
'input': 'Adoration of the Trinity [SEP] creator', 
'output': [{'answer': 'Albrecht Dürer'}],
'meta': {
    'template_questions': ['Who is Adoration of the Trinity by?']}, 
    'rephrases': ['Who Is Worship of the Trinity Through?', 'Who is Adoration of the Trinity Through?', 
                  'Who is worshiping the Trinity through?', 'Who is worship of the Trinity by?', 
                  'Who is through the worship of the Trinity?', 'Who is the worship of the Trinity through?', 
                  'Who is through worship of the Trinity?', 'Who through the worship of the Trinity?', 
                  'Who is by worship of the Trinity?', 'Who is the Worship of the Trinity?', 
                  'Who Is Worship of the Trinity?', 'Who is worshipping the Trinity?', 'Who is worshiping the Trinity?', 
                  'Who is Adoration of the Trinity by?']
}

dev-new.jsonl
{
'input': 'Watts Humphrey [SEP] educated at', 
'output': [{'answer': 'Illinois Institute of Technology'}], 
'meta': {
    'template_questions': ['What university did Watts Humphrey attend?']}, 
    'rephrases': ['Which university did Watts Humphrey attend?', 'Which university has Watts Humphrey attended?', 
                  'Which university did Watts Humphrey go to?', 'Which university has Watts Humphrey visited?', 
                  'Which university attended Watts Humphrey?', 'Which university did Watts go to Humphrey?', 
                  'What university did Watts attend Humphrey at?', 'Which university did Watts attend Humphrey?', 
                  'What university did Watts attend Humphrey?', 'What university did Watts go to Humphrey?', 
                  'Which university did Watts Humphrey take part in?', 'What university did Watts Humphrey take part in?', 
                  'Which university did Watts Humphrey participate in?', 'Which university did Watts Humphrey study at?', 
                  'What university did Watts Humphrey study at?', 'What university did Watts Humphrey go to?', 
                  'What university did Watts Humphrey attend?'], 
}

train-new_annotated_final.jsonl
{
'input': 'Who is Adoration of the Trinity by?', 
'output': [{'answer': 'Albrecht Dürer'}], 
'rephrases': ['Who Is Worship of the Trinity Through?', 'Who is Adoration of the Trinity Through?', 'Who is worshiping the Trinity through?', 
              'Who is worship of the Trinity by?', 'Who is through the worship of the Trinity?', 'Who is the worship of the Trinity through?', 
              'Who is through worship of the Trinity?', 'Who through the worship of the Trinity?', 'Who is by worship of the Trinity?', 
              'Who is the Worship of the Trinity?', 'Who Is Worship of the Trinity?', 'Who is worshipping the Trinity?', 
              'Who is worshiping the Trinity?', 'Who is Adoration of the Trinity by?'], 
}


{
'input': 'What university did Watts Humphrey attend?', 
'output': [{'answer': 'Illinois Institute of Technology']}], 
'meta': {
    'template_questions': ['What university did Watts Humphrey attend?']}, 
    'rephrases': ['Which university did Watts Humphrey attend?', 'Which university has Watts Humphrey attended?', 
                  'Which university did Watts Humphrey go to?', 'Which university has Watts Humphrey visited?', 
                  'Which university attended Watts Humphrey?', 'Which university did Watts go to Humphrey?', 
                  'What university did Watts attend Humphrey at?', 'Which university did Watts attend Humphrey?', 
                  'What university did Watts attend Humphrey?', 'What university did Watts go to Humphrey?', 
                  'Which university did Watts Humphrey take part in?', 'What university did Watts Humphrey take part in?', 
                  'Which university did Watts Humphrey participate in?', 'Which university did Watts Humphrey study at?', 
                  'What university did Watts Humphrey study at?', 'What university did Watts Humphrey go to?', 
                  'What university did Watts Humphrey attend?'], 
}

"""
