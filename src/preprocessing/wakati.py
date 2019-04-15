# -*- coding: utf-8 -*-
"""Twitterのデータのtextに対して分かち書きをするスクリプト(元のcsvに代入)."""
import os
import sys
import argparse
import ssl

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
import global_function as global_func
import preprocess_function as preprocess_func


# ssl認証
ssl._create_default_https_context = ssl._create_unverified_context


parser = argparse.ArgumentParser(description='Twitter User Tweets Crawler')
parser.add_argument('--config_path', '-config', type=str, default='config/twitter.yml',
                    help='config(yaml) file path')
parser.add_argument('--token_path', '-token', type=str, default='data/twitter_token.yml',
                    help='twitter account token file path')
parser.add_argument('--log_path', '-l', type=str, default='log_dir/wakati.log',
                    help='log directory (log_file, crawler_csv in this directory)')
parser.add_argument('--input_dir', '-input', type=str, default='data/text_data/crawler/negative',
                    help='crawler output csv directory (input)')
args = parser.parse_args()


def main():
    """build logger"""
    logger = global_func.build_logger(args.log_path)

    """load config"""
    config = global_func.load_config(args.config_path)
    library_name = config['library_name'].lower()
    text_colums_name = config['text_colums_name']
    wakati_option = config['wakati_option']

    """build tweets_getter"""
    if library_name == 'mecab':
        preprocess = preprocess_func.MecabPreprocess(**wakati_option)
    elif library_name == 'ginza':
        preprocess = preprocess_func.GinzaPreprocess(**wakati_option)
    else:
        raise Exception("Not supported on {} yet".format(library_name))

    file_path_list = []
    for curDir, dirs, files in os.walk(args.input_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path_list.append(os.path.join(curDir, file))

    for i, file_path in enumerate(file_path_list):
        logger.debug('{}/{} => wakati file_path: {}'.format(i, len(file_path_list), file_path))
        df = pd.read_csv(file_path)
        # dfの中にtext_colums_nameのcolumがもうすでにあったら処理をしない。
        if text_colums_name in list(df.columns.values):
            continue
        text_list = df['text']
        output_text_list = [preprocess.wakati(text) for text in text_list]
        wakati_df = pd.DataFrame({text_colums_name: output_text_list})
        wakati_df = pd.concat([df, wakati_df], axis=1)
        wakati_df.to_csv(file_path, index=False)


if __name__ == "__main__":
    main()
