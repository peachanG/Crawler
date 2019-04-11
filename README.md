# Twitter ネガポジ判定

## Setup Evironment
基本的にDockerを用いて開発を行う
```
git clone https://github.com/peachanG/Twitter_NegaPosi.git
docker-compose build
docker-compose up -d   # jupyterlab -> http://localhost:8888 (Please change passward in Dockerfile)
docker-compose exec app /bin/bash
```

## Twitter Data Crawler
twitterのデータを集める。
各自APIのtokenを所得し, data/twitter_token.ymlとして保存する必要あり。(./example_token.ymlを参照)

### 特定ユーザーのツイートを所得
```
python3 src/crawler/Twitter_User_tweets.py -config config/crawler/crawler_negap
osi.yml -s data/text_data/crawler
```

### 特定のツイートに対するリプライを所得(深さ2ツイート分まで)
```
python3 src/crawler/Twitter_Reply.py -config config/crawler/reply.yml -s data/text_data/reply
```

## Twitter preprocessing

### 分かち書き
分かち書きのツールとしてMeCabとGiNZAが使用可能。

```
python3 src/preprocessing/wakati.py -config config/preprocess/wakati.yml -input
 data/text_data/crawler/
```
