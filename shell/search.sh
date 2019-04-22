#!/bin/sh

watch -n 300 python3 src/crawler/Twitter_Search.py -config config/crawler/emoji.yml -l log_dir/twitter_emoji.log -s data/text_data/crawler/emoji
