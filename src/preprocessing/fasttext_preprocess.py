# -*- coding: utf-8 -*-
"""Twitterの分かち書き済みのcsvをfasttextの入力の形に変形し一つのtextファイルにする."""
import os
import sys
import argparse
import random

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
import global_function as global_func


parser = argparse.ArgumentParser(description='Twitter User Tweets Crawler')
parser.add_argument('--input_dir', '-input', type=str, default='data/text_data/crawler',
                    help='input csv directory after wakati')
parser.add_argument('--output_text_directory', '-o', type=str, default='data/text_data/fasttext_input/train.txt',
                    help='output directory path')
parser.add_argument('--separate', action='store_true',
                    help='separate dataset train validation test')
parser.add_argument('--log_path', '-l', type=str, default='log_dir/fasttext_preprocess.log',
                    help='log directory (log_file in this directory)')
parser.add_argument('--text_column', '-column', type=str, default='wakati_text',
                    help='column of text to extract')
args = parser.parse_args()


def main():
    """build logger"""
    logger = global_func.build_logger(args.log_path)

    label_dict = {}
    text_list = []
    for i, label_ in enumerate(os.listdir(args.input_dir)):
        if label_[0] == '.':
            continue
        i += 1
        text_label_list = []
        label_dict[label_] = i
        label_path = os.path.join(args.input_dir, label_)
        for csv_name in os.listdir(label_path):
            if not csv_name.endswith(".csv"):
                continue
            csv_path = os.path.join(label_path, csv_name)
            logger.debug('Read csv ==> {}'.format(csv_path))
            df = pd.read_csv(csv_path, engine='python')
            text_label_list.extend(df[args.text_column].values.tolist())

        text_label_list = ['__label__{} '.format(i) + text + ' \n' for text in text_label_list]
        text_list.extend(text_label_list)

    before_num = len(text_list)
    text_list = list(set(text_list))
    text_list = random.shuffle(text_list)
    after_num = (len(text_list))
    logger.debug('Duplicate {} => {}'.format(before_num, after_num))

    train_ratio = 0.8
    val_ratio = 0.1
    test_ratio = 0.1
    train_num = len(text_list) * train_ratio
    val_num = len(text_list) * val_ratio
    test_num = len(text_list) * test_ratio
    if args.separate:
        # train
        os.makedirs(os.path.dirname(args.output_text_path), exist_ok=True)
        with open(, 'w') as f:
            f.writelines(text_list)
    else:
        os.makedirs(os.path.dirname(args.output_text_path), exist_ok=True)
        with open(args., 'w') as f:
            f.writelines(text_list)


if __name__ == "__main__":
    main()
