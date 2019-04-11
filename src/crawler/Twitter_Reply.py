# -*- coding: utf-8 -*-
"""TwitterAPIを用いてTweetを収集するプログラム."""
import os
import sys
import argparse
import ssl

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
import global_function as global_func
import api_function as api_func


# ssl認証
ssl._create_default_https_context = ssl._create_unverified_context


parser = argparse.ArgumentParser(description='Twitter Reply Crawler')
parser.add_argument('--config_path', '-config', type=str, default='config/crawler/reply.yml',
                    help='config(yaml) file path')
parser.add_argument('--token_path', '-token', type=str, default='data/twitter_token.yml',
                    help='twitter account token file path')
parser.add_argument('--log_path', '-l', type=str, default='log_dir/crawler_reply.log',
                    help='log directory (log_file, crawler_csv in this directory)')
parser.add_argument('--save_data_dir', '-s', type=str, default='data/text_data/reply',
                    help='save text data directory')
args = parser.parse_args()


def main():
    """保存用のdirectoryの準備"""
    os.makedirs(args.save_data_dir, exist_ok=True)

    """build logger"""
    logger = global_func.build_logger(args.log_path)

    """load config"""
    config = global_func.load_config(args.config_path)

    """build tweets_getter"""
    getter = api_func.ReplyTweetsGetter(args.token_path)

    getter.set_csv_dir(args.save_data_dir)
    for tweet_id in config['tweet_id_list']:
        logger.debug('Crawler Tweet id : {}'.format(tweet_id))
        getter.set_root_tweet(tweet_id)
        getter.get_tweets()


if __name__ == "__main__":
    main()
