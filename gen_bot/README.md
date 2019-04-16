# twitter bot

## tweetの取得
* ### 特定のツイートのreplyを取得

```
from get_tweet import ReplyTweetsGetter

token_path = 'twitter_token.yml'
getter = ReplyTweetsGetter(token_path)
getter.set_root_tweet(1115797923499892736)
first_output = getter.get_tweets()
```

* ### user timelineの取得

```
from get_tweet import UserTweetsGetter

token_path = 'twitter_token.yml'
getter = UserTweetsGetter(token_path)
getter.set_user('peachgan_r6s')
first_output = getter.get_tweets()
```
