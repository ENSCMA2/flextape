import os
import sys
import time
import logging
import argparse
import pickle
import threading
# from transformers import T5Tokenizer, LlamaTokenizer, GPT2Tokenizer
from transformers import T5Tokenizer, GPT2Tokenizer

sys.path.append('.')
sys.path.append('..')
LOG = logging.getLogger(__name__)
LOG.setLevel(level=logging.DEBUG)
# log_interval=200


def run_py(i):
    os.system(i)


def handle_process_folders_args(inp, edit_folders):
    if inp == 'all_folders':
        res = [i for i in range(edit_folders)]
    elif inp.startswith('seg'):
        start, end = inp.split("_")[1:]
        res = [int(r) for r in range(int(start), int(end))]
    else:
        res = inp[1:-1].split(',')
        res = [int(r) for r in res]
    return res


if __name__ == '__main__':
    from src.models.seq2seq_modules import BartSeq2Seq
    from src.models.class_modules import BertBinary
    from src.dataset.sme_dataset import SeqEditDataSet
    from src.utils import get_handler, get_time_post_fix, patch_related_args, ft_related_args, main_args
    parser = argparse.ArgumentParser()
    '''adding main arguments'''
    parser = main_args(parser)
    '''adding the arguments related to the method T-patch '''
    parser = patch_related_args(parser)
    '''adding the arguments related to the method fine_tuning '''
    ft_related_args(parser)

    args, _ = parser.parse_known_args()
    if not args.task_id:
        args.task_id = f'{args.task}_{args.method}_{args.edit_folder_num}folders'
    args.mlc = 5 if args.task == 'fever' else 10
    # deal with the fold to process
    args.process_folders = handle_process_folders_args(args.process_folders, args.edit_folder_num)
    LOG.info("This scripts deal with the {}".format(args.process_folders))

    # deal with the log path
    args.log_path = f'log/{args.method}/{args.task}/{args.task_id}_{args.model_path.split("/")[-1]}_tongyici'
    if args.debug_mode == 1:
        args.log_path = f'log/{args.method}/{args.task}/{get_time_post_fix()}'

    # deal with the data_path
    args.data_path = "/home/halevy/flextape/data"
    f_h, s_h = get_handler(args.log_path, log_name=args.log_name)
    LOG.addHandler(f_h)
    LOG.addHandler(s_h)

    # deal with the model
    if args.method in ['ft', 'T-patch']:
        if not os.path.exists(os.path.join(args.data_path, f'seq_edit_data_{args.task}_{args.model_type}_{args.edit_folder_num}.pkl')):
            if args.task == 'zsre' and args.model_type == 'bart':
                model_to_edit = BartSeq2Seq.load_from_checkpoint(args.model_path)
                tokenizer = model_to_edit.tokenizer
            elif args.model_type == 't5' :
                model_dir = os.path.join(args.cache_dir, args.model_name) \
                    if "cache_dir" in args else args.model_name
                try:
                    tokenizer = T5Tokenizer.from_pretrained(model_dir)
                except:
                    print("The cache can not be used")
                    tokenizer = T5Tokenizer.from_pretrained(args.model_name,
                                                                 cache_dir=args.cache_dir)  # h
            elif args.model_type == 'llama':
                model_dir = os.path.join(args.cache_dir, args.model_name) \
                    if "cache_dir" in args else args.model_name
                try:
                    tokenizer = LlamaTokenizer.from_pretrained(model_dir)
                except:
                    print("The cache can not be used")
                    tokenizer = LlamaTokenizer.from_pretrained(args.model_name,
                                                                 cache_dir=args.cache_dir)
                tokenizer.pad_token_id = 0
                tokenizer.padding_side = 'left'
            elif args.model_type == 'gptj':
                model_dir = os.path.join(args.cache_dir, args.model_name) \
                    if "cache_dir" in args else args.model_name
                try:
                    tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
                except:
                    print("The cache can not be used")
                    tokenizer = GPT2Tokenizer.from_pretrained(args.model_name,
                                                                 cache_dir=args.cache_dir)
                tokenizer.pad_token_id = tokenizer.eos_token_id
                tokenizer.padding_side = 'left'
            else:
                model_to_edit = BertBinary.load_from_checkpoint(args.model_path)
                tokenizer = model_to_edit.tokenizer
            seq_edit_dataset = SeqEditDataSet(
                task_name=args.task, tokenizer=tokenizer, data_path=args.data_path,
                train_sub_size=args.train_sub_size, memory_size=args.memory_size, edit_folder_num=args.edit_folder_num,
                batch_size=args.batch_size, num_workers=args.num_workers, loss_as_val_metric=args.val_metric_type == 'loss'
            )
            saved_dataset_file = open(os.path.join(args.data_path, f'seq_edit_data_{args.task}_{args.model_type}_{args.edit_folder_num}.pkl'), 'wb')
            saved_dataset_file.write(pickle.dumps(seq_edit_dataset))
            saved_dataset_file.close()
    else:
        LOG.info("Only support T-patch and fine-tuning method")
        exit()

    orders, FOLD_TO_GPU = [], {}

    for n, fold_n in enumerate(args.process_folders):
        r = n - n // args.gpu_nums * args.gpu_nums
        FOLD_TO_GPU[fold_n] = r
    LOG.info('The fold_to_gpu dict is: {}'.format(FOLD_TO_GPU))

    # We firstly get the orders that need to be processed
    for fold_n in args.process_folders:
        order = f'python3 scripts/{args.method}.py'
        for k, v in vars(args).items():
            order += f' --{k}={v}'
        order += f' --fold_n={fold_n} --device={FOLD_TO_GPU[fold_n]}'
        orders.append(order)

    threads_list = []
    for order in orders:
        task = threading.Thread(target=run_py, args=(order, ))
        threads_list.append(task)

    for i, task in enumerate(threads_list):
        if i != 0:
            time.sleep(15)
        task.start()
