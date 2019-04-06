# -*- coding: utf-8 -*-
"""TwitterAPIを用いてTweetを収集するプログラム."""
import os
import codecs
import json
import argparse

import twitter

import utils.global_function as global_func


parser = argparse.ArgumentParser(description='Twitter Crawler')
parser.add_argument('--config', type=str, default='config/twitter.yml',
                    help='config(yaml) file path')
parser.add_argument('--token', '-t', type=str, default='./twitter_token.yml',
                    help='twitter account token file path')
parser.add_argument('--results_dir', '-r', type=str, default='results',
                    help='results directory path')
args = parser.parse_args()


def main():
    """保存用ファイルのパス"""
    log_file_path = os.path.join(args.results_dir, "log")
    results_text_path = os.path.join(args.results_dir, "results.txt")
    results_json_path = os.path.join(args.results_dir, "tweets_{}.json")

    """build logger"""
    logger = global_func.build_logger(log_file_path)

    """load config"""
    token_config = global_func.load_config(args.token)
    config = global_func.load_config(args.config)

    """アクセストークンの読み込み."""
    ConsumerKey = token_config['ConsumerKey']
    ConsumerSecret = token_config['ConsumerSecret']
    AccessToken = token_config['AccessToken']
    AccessTokenSecret = token_config['AccessTokenSecret']

    """検索パラメータの読み込み"""
    q = "。,！,？+-\n+-笑+-「+-」+-w+-ｗ+-(+-（+-http+-https+exclude:retweets"  # URL投稿やリツイートを含まないようにクエリ設定
    search_params = config['search']
    geocode = search_params.get('geocode', '')
    lang = search_params.get('lang', '')
    locale = search_params.get('locale', '')
    result_type = search_params.get('result_type', '')
    count = search_params.get('count', 0)
    until = search_params.get('until', '')
    since_id = search_params.get('since_id', '')
    max_id = search_params.get('max_id', '')
    include_entities = search_params.get('include_entities', '')

    """検索パラメータ(非ポスト)の読み込み"""
    search_count = search_params.get('search_count', 1)
    if search_count == 0:
        search_count = True

    """「最初から」もしくは「続きから」ツイートを取得"""
    if os.path.exists(args.results_dir):
        logger.debug("Getting from the continuation.")
        with open(results_text_path, 'r') as file_info:
            infos = file_info.readlines()
        max_id = int(infos[0].split(":")[1])  # maxidの設定
        tweets_no = int(infos[1].split(":")[1])  # 保存時の通し番号
        collected_data_count = int(infos[2].split(":")[1])  # 取得ツイート数
    else:
        logger.debug("Getting from the beginning.")
        os.mkdir(args.results_dir)
        tweets_no = 1  # 保存時の通し番号
        collected_data_count = 0  # 取得ツイート数

    """検索実行"""
    t = twitter.Twitter(auth=twitter.OAuth(AccessToken, AccessTokenSecret, ConsumerKey, ConsumerSecret), retry=True)

    while search_count:
        try:
            datas = t.search.tweets(q=q, geocode=geocode, lang=lang, locale=locale,
                                    result_type=result_type, count=count, until=until,
                                    since_id=since_id, max_id=max_id, include_entities=include_entities)

        except Exception as e:
            logger.debug(e)
            break
        if datas["statuses"] == []:
            logger.debug("There is no tweet.")
            break

        with codecs.open(results_json_path.format(tweets_no), 'w', 'utf8') as fo:
            json.dump(datas["statuses"], fo, indent=4, ensure_ascii=False)

        tweets_no += 1  # 保存時の通し番号
        collected_data_count += len(datas["statuses"])
        logger.debug("collected %d tweets" % collected_data_count)  # 取得ツイート数表示

        """次の検索時の最大max_idの設定"""
        max_id = datas["statuses"][-1]["id"]  # 収集したデータからmax_idを直接取得する．next_paramsはたまに取得できないときがある？
        max_id = str(int(max_id)-1)  # 検索はmax_id未満に対して行うはずなのだが，なぜか重複するため-1する．
        # logger.debug("max_id:"+ str(max_id))#maxidの表示

        with open(results_text_path, 'w') as file_info:
            file_info.write("next_max_id:" + str(max_id) + "\n" +
                            "tweets_no:" + str(tweets_no) + "\n" +
                            "collected tweets:" + str(collected_data_count))

        if type(search_count) == int:
            search_count -= 1

        if collected_data_count == 0:
            logger.debug("Target tweets are nothing.")


if __name__ == "__main__":
    main()
