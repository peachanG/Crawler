import ssl
import yaml
import twitter

ssl._create_default_https_context = ssl._create_unverified_context


def load_config(path):
    with open(path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def build_api(token_path):
    token_config = load_config(token_path)

    """アクセストークンの読み込み."""
    ConsumerKey = token_config['ConsumerKey']
    ConsumerSecret = token_config['ConsumerSecret']
    AccessToken = token_config['AccessToken']
    AccessTokenSecret = token_config['AccessTokenSecret']

    twitter_api = twitter.Twitter(auth=twitter.OAuth(AccessToken, AccessTokenSecret, ConsumerKey, ConsumerSecret), retry=True)
    return twitter_api


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
        self.api = build_api(token_path)
        self.max_count = max_count

    def get_tweets(self, since_id=None):
        """
        Subclasses should override for any actions to run.
        """
        tweets = []
        """
        self.apiを用いてデータを所得
        """
        return tweets


class UserTweetsGetter(TweetsGetter):
    """twitterの特定のUser_name(screen_name)のtweetを集める.

    # Arguments
        token_path: twitter apiのtoken　configのpath
        csv_dir: csvの保存先(２回目以降の場合はそのcsvの親のdiretoryのpath)
        max_count: apiの一回のリクエストで要求するtweet数
        ## set_default_params
        APIの返り値からcsvへの出力のkeyを設定

    # How to use
        getter = UserTweetsGetter(token_path)
        getter.set_user('peachgan_r6s')
        getter.get_tweets()
        ==> tweetsのlistを返し、self.since_id_dictにscreen_nameとsince_idを保持(前回分)

    """
    def __init__(self, token_path, max_count=100):
        self.since_id_dict = {}
        super(UserTweetsGetter, self).__init__(token_path, max_count)

    def set_user(self, screen_name):
        self.screen_name = screen_name
        self.since_id = self.since_id_dict.get(self.screen_name, None)

    def _set_since_id(self, since_id):
        self.since_id = since_id

    def get_tweets(self):
        max_id = None
        output_list = []
        while True:
            tweets, min_id, tweets_num = self._get_tweets_core(max_id)
            max_id = min_id - 1
            output_list.extend(tweets)
            if tweets_num < self.max_count:
                break
        if len(output_list) != 0:
            self.since_id_dict[self.screen_name] = output_list[0]['id']

        return output_list

    def _get_tweets_core(self, max_id=None):
        tweets = self._get_user_timeline(max_id)
        tweets_num = len(tweets)
        if tweets_num == 0:
            min_id = 0
        else:
            min_id = tweets[-1]['id']

        return tweets, min_id, tweets_num

    def _get_user_timeline(self, max_id):
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
        getter = ReplyTweetsGetter(token_path)
        getter.set_root_tweet(1115797923499892736)
        getter.get_tweets()
        ==> csv_dir/'{}.csv'.format(root_tweet_id)に所得したreplyを保存

    """
    def __init__(self, token_path, max_count=100):
        self.since_id_dict = {}
        super(ReplyTweetsGetter, self).__init__(token_path, max_count)

    def set_root_tweet(self, tweet_id):
        self.root_tweet_id = tweet_id
        self.since_id = self.since_id_dict.get(self.root_tweet_id, None)

    def get_tweets(self):
        output_list = []
        root_tweet = self.api.statuses.show(id=self.root_tweet_id)
        reply_list = self._get_replys(root_tweet)
        output_list.extend(reply_list)

        for reply in reply_list:
            reply_reply_list = self._get_replys(reply)
            output_list.extend(reply_reply_list)

        reply_id_list = [tweet['id'] for tweet in output_list]
        if len(reply_id_list) != 0:
            self.since_id_dict[self.root_tweet_id] = max(reply_id_list)

        return output_list

    def _get_replys(self, tweet):
        reply_list = []
        query = "to:" + tweet['user']['screen_name']
        tweet_id = tweet['id']
        if self.since_id is None:
            since_id = tweet_id
        else:
            since_id = max(self.since_id, tweet_id)

        max_id = None
        while True:
            responce_list = self._get_reply_core(query, since_id, max_id)
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
