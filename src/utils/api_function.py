import os

import pandas as pd
import twitter

import global_function as global_func
import preprocess_function as preprocess_func


def build_api(token_path):
    token_config = global_func.load_config(token_path)

    """アクセストークンの読み込み."""
    ConsumerKey = token_config['ConsumerKey']
    ConsumerSecret = token_config['ConsumerSecret']
    AccessToken = token_config['AccessToken']
    AccessTokenSecret = token_config['AccessTokenSecret']

    api = twitter.Twitter(auth=twitter.OAuth(AccessToken, AccessTokenSecret, ConsumerKey, ConsumerSecret), retry=True)
    return api


class TweetsGetter(object):
    """twitterのtweetを集める(親クラス).

    # Arguments
        token_path: twitter apiのtoken　configのpath
        max_count: apiの一回のリクエストで要求するtweet数
        ## set_default_params
        APIの返り値からcsvへの出力のkeyを設定

    # How to use
        getter = TweetsGetter(token_path, csv_dir)
        getter.set_csv_dir('data/text_data/crawler/nega')
        getter.set_info() # ここは継承ごとに変更
        getter.get_tweets()
        ==> csv_dir/'{}.csv'.format(root_tweet_id)に所得したreplyを保存

    """
    def __init__(self, token_path, max_count=100):
        self._set_default_params()
        self.api = build_api(token_path)
        self.max_count = max_count
        self.delete_reply = False

    def _set_default_params(self):
        self.key_list = ['created_at', 'id', 'screen_name', 'text']
        self.user_key_list = ['screen_name']

    def set_csv_dir(self, csv_dir):
        os.makedirs(csv_dir, exist_ok=True)
        self.csv_dir = csv_dir

    def get_tweets(self):
        """
        Subclasses should override for any actions to run.
        """

        self.df = pd.DataFrame()
        tweets = []
        """
        self.apiを用いてデータを所得
        """
        self._write_tweets_df(tweets)
        self.df.to_csv(self.csv_path, index=False)
        del self.df

    def _write_tweets_df(self, tweets):
        tweets_norm = [self._extract_data(tweet) for tweet in tweets]
        for tweet in tweets_norm:
            text = preprocess_func.text_norm(tweet[-1], self.delete_reply)
            if text == '':
                continue
            tweet[-1] = text
            tmp = pd.DataFrame(tweet, self.key_list)
            self.df = self.df.append(tmp.T)

    def _extract_data(self, tweet):
        output_info = []
        for key in self.key_list:
            value = tweet['user'][key] if key in self.user_key_list else tweet[key]
            output_info.append(value)
        return output_info


class UserTweetsGetter(TweetsGetter):
    """twitterの特定のUser_name(screen_name)のtweetを集める.

    # Arguments
        token_path: twitter apiのtoken　configのpath
        csv_dir: csvの保存先(２回目以降の場合はそのcsvの親のdiretoryのpath)
        max_count: apiの一回のリクエストで要求するtweet数
        ## set_default_params
        APIの返り値からcsvへの出力のkeyを設定

    # How to use
        getter = UserTweetsGetter(token_path, csv_dir)
        getter.set_csv_dir('data/text_data/crawler/nega')
        getter.set_user('peachgan_r6s')
        getter.get_tweets()
        ==> csv_dir/'{}.csv'.format(user_name)に所得したtweetsを保存

    """
    def __init__(self, token_path, max_count=100):
        super(UserTweetsGetter, self).__init__(token_path, max_count)
        self.delete_reply = True

    def set_user(self, screen_name):
        self.screen_name = screen_name

        self.csv_path = os.path.join(self.csv_dir, '{}.csv'.format(screen_name))
        if os.path.isfile(self.csv_path):  # resume twitter crawler
            self.base_df = pd.read_csv(self.csv_path)
            self.since_id = self.base_df['id'].iat[0]
            self.resume_flag = True
        else:  # first crawler
            self.since_id = None
            self.resume_flag = False

    def get_tweets(self):
        self.df = pd.DataFrame()
        max_id = None
        while True:
            min_id, tweets_num = self._get_tweets_core(max_id)
            max_id = min_id - 1
            if tweets_num < self.max_count:
                break

        if self.resume_flag:
            self.df = pd.concat([self.df, self.base_df])

        self.df = self.df.dropna(subset=['text'])
        self.df = self.df[self.df['text'] != '']
        self.df.to_csv(self.csv_path, index=False)
        del self.df

    def _get_tweets_core(self, max_id=None):
        tweets = self._get_user_timeline(max_id)
        tweets_num = len(tweets)
        if tweets_num == 0:
            min_id = 0
        else:
            min_id = tweets[-1]['id']
            self._write_tweets_df(tweets)

        return min_id, tweets_num

    def _get_user_timeline(self, max_id=None):
        # 参考()
        if self.since_id is None:  # screen_nameの初めてのsearch
            if max_id is None:  # 1回目のsearch
                tweets = self.api.statuses.user_timeline(screen_name=self.screen_name,
                                                         count=self.max_count)
            else:  # 2回目のsearch
                tweets = self.api.statuses.user_timeline(screen_name=self.screen_name,
                                                         max_id=max_id, count=self.max_count)
        else:  # search_nameの二回目以降のsearch
            if max_id is None:  # 1回目のsearch
                tweets = self.api.statuses.user_timeline(screen_name=self.screen_name,
                                                         since_id=self.since_id,
                                                         count=self.max_count)
            else:
                tweets = self.api.statuses.user_timeline(screen_name=self.screen_name,
                                                         since_id=self.since_id,
                                                         max_id=max_id,
                                                         count=self.max_count)
        return tweets


class ReplyTweetsGetter(TweetsGetter):
    """twitterの特定のtweetの対するリプライを集める.

    # Arguments
        token_path: twitter apiのtoken　configのpath
        max_count: apiの一回のリクエストで要求するtweet数
        ## set_default_params
        APIの返り値からcsvへの出力のkeyを設定

    # How to use
        getter = ReplyTweetsGetter(token_path, csv_dir)
        getter.set_csv_dir('data/text_data/crawler/nega')
        getter.set_root_tweet(1115797923499892736)
        getter.get_tweets()
        ==> csv_dir/'{}.csv'.format(root_tweet_id)に所得したreplyを保存

    """
    def __init__(self, token_path, max_count=100):
        super(ReplyTweetsGetter, self).__init__(token_path, max_count)

    def set_root_tweet(self, tweet_id):
        self.root_tweet_id = tweet_id
        self.csv_path = os.path.join(self.csv_dir, '{}.csv'.format(self.root_tweet_id))

    def get_tweets(self):
        self.df = pd.DataFrame()
        root_tweet = self.api.statuses.show(id=self.root_tweet_id)
        reply_list = self._get_replys(root_tweet)
        if len(reply_list) == 0:
            return

        self._write_tweets_df(reply_list)
        for reply in reply_list:
            reply_reply_list = self._get_replys(reply)
            if len(reply_reply_list) == 0:
                continue
            self._write_tweets_df(reply_reply_list)

        self.df = self.df.dropna(subset=['text'])
        self.df = self.df[self.df['text'] != '']
        self.df = self.df.drop_duplicates(keep='first', subset='text')
        self.df.to_csv(self.csv_path, index=False)
        del self.df

    def _get_replys(self, tweet):
        reply_list = []
        query = "to:" + tweet['user']['screen_name']
        tweet_id = tweet['id']
        max_id = None
        while True:
            responce_list = self._get_reply_core(query, tweet_id, max_id)
            if len(responce_list) == 0:
                break
            for responce in responce_list:
                if responce['in_reply_to_status_id'] == tweet_id:
                    reply_list.append(responce)
            if len(responce_list) < self.max_count:
                break
            max_id = responce_list[-1]['id'] - 1

        return reply_list

    def _get_reply_core(self, query, since_id, max_id=None):
        if max_id is None:  # 1回目のsearch
            tweets = self.api.search.tweets(q=query,
                                            since_id=since_id,
                                            count=self.max_count)['statuses']
        else:  # 2回目のsearch
            tweets = self.api.search.tweets(q=query,
                                            since_id=since_id,
                                            max_id=max_id,
                                            count=self.max_count)['statuses']

        return tweets
