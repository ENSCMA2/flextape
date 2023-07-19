import os
import sys
from argparse import ArgumentParser
from pytorch_lightning import LightningModule, Trainer, Callback
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.utilities.seed import seed_everything
from pytorch_lightning.utilities import rank_zero_info
import torch
import time
sys.path.append('.')
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3,4,5'

class CUDACallback(Callback):

    def on_train_epoch_start(self, trainer, pl_module):
        # Reset the memory use counter
        torch.cuda.reset_peak_memory_stats(self.root_gpu(trainer))
        torch.cuda.synchronize(self.root_gpu(trainer))
        self.start_time = time.time()

    def on_train_epoch_end(self, trainer, pl_module):
        torch.cuda.synchronize(self.root_gpu(trainer))
        max_memory = torch.cuda.max_memory_allocated(self.root_gpu(trainer)) / 2 ** 20
        epoch_time = time.time() - self.start_time

        max_memory = trainer.strategy.reduce(max_memory)
        epoch_time = trainer.strategy.reduce(epoch_time)

        rank_zero_info(f"Average Epoch time: {epoch_time:.2f} seconds")
        rank_zero_info(f"Average Peak memory {max_memory:.2f}MiB")

    def root_gpu(self, trainer):
        return trainer.strategy.root_device.index

if __name__ == "__main__":

    from src.models.gpt_module import GPTJSeq2Seq

    parser = ArgumentParser()
    parser.add_argument("--log_path", type=str, default="./log/models/gptj_seq2seq")
    parser.add_argument("--save_top_k", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", type=int, default=0)
    # parser.add_argument("--gpus", type=list, default=[0,1,2,3,4])
    parser.add_argument("--cache_dir", type=str, default='./hugging_cache')

    parser = GPTJSeq2Seq.add_model_specific_args(parser)

    args, _ = parser.parse_known_args()
    seed_everything(args.seed)
    logger = TensorBoardLogger(args.log_path, name=None)

    callbacks = [
        ModelCheckpoint(
            monitor="nll_loss", mode="min",
            dirpath=os.path.join(logger.log_dir, "checkpoints"),
            save_weights_only=True, save_top_k=args.save_top_k,
            filename="gptj-seq2seq-{epoch:02d}-{nll_loss:.4f}"
        ),
        LearningRateMonitor(logging_interval="step"),
        CUDACallback()
    ]
    trainer = Trainer.from_argparse_args(args, logger=logger,
                                         callbacks=callbacks,
                                         max_epochs=2,
                                         accelerator="gpu",
                                         strategy='deepspeed_stage_3_offload')
    # trainer = Trainer.from_argparse_args(args, logger=logger,
    #                                      callbacks=callbacks,
    #                                      max_epochs=2
    #                                      )
    # trainer = Trainer.from_argparse_args(args, logger=logger)

    model = GPTJSeq2Seq(**vars(args))
    print('Model Loading Done. \n')
    # trainer.validate(model)
    trainer.fit(model)

