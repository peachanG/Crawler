#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import codecs
import os
import json
import glob
import json
import sys

sys.path.append("..")
from Crawler import Twitter_Crawler

from Preprocessing import Delete
from Preprocessing import Wakati

"""設定ファイルの読み込み"""
inifile = configparser.ConfigParser(allow_no_value=True,interpolation=configparser.ExtendedInterpolation())
inifile.readfp(codecs.open("../Crawler/Twitter_Crawler.ini",'r','utf8'))

"""パラメータの読み込み"""
# count = Twitter_Crawler.get_or_setDefault(inifile.get,'search_params','count')
until = Twitter_Crawler.get_or_setDefault(inifile.get,'search_params','until')
print("Tweetuntil:" + str(until))

"""読み込み先の設定"""
save_dir_path = inifile.get('other_settings','Tweet_save_dir_path')
save_dir_name = inifile.get('other_settings','save_dir_name')
save_dir = os.path.join(save_dir_path,save_dir_name)
tweets_paths = glob.glob(save_dir+"/tweets*")

"""保存先の設定"""
save_dir_txt = inifile.get('other_settings','Text_save_dir_path')
save_dir_corpus_path = inifile.get('other_settings','Corpus_save_dir_path')

save_dir_corpus_koko_path = inifile.get('other_settings','Corpuskoko_save_dir_path')
if not os.path.exists(save_dir_corpus_koko_path):
		os.mkdir(save_dir_corpus_koko_path)
save_dir_corpus_koko = os.path.join(save_dir_corpus_koko_path,save_dir_name)
if not os.path.exists(save_dir_corpus_koko):
		os.mkdir(save_dir_corpus_koko)

"""ツイートのテキスト文取得，前処理"""
filenumber = 1#ファイルの通し番号
f_txt = open(os.path.join(save_dir_txt,save_dir_name + ".txt"),'w',encoding='UTF-8')#テキスト文
f_pre = open(os.path.join(save_dir_corpus_path,save_dir_name + "_pre.txt"),'w',encoding='UTF-8')#前処理（まとめ）

for i,file in enumerate(tweets_paths):
	try:
		fi = codecs.open(tweets_paths[i-1],'r','utf8')
		tweet_datas=json.load(fi)
		print(str(i+1) + "×" + str(len(tweet_datas)) + "Tweets")
	except Exception:
		pass

	for j,tweet_data in enumerate(tweet_datas):
		text = tweet_data["text"].replace("\r","").replace("\n","")
		f_txt.write(text + "\n")
		text = text.replace(",","")

		"""文字列削除＆単語分割"""
		text = Delete.delete_twitter(text)#文字列削除

		text = Wakati.wakati(text)#分かち書き
		f_pre.write(text)

		with open(os.path.join(save_dir_corpus_koko,save_dir_name + "_pre_" + str(filenumber) + ".txt"),'w',encoding='UTF-8') as file_koko:#前処理（個々）
			file_koko.write(text)

		filenumber += 1
	fi.close()
f_txt.close()
f_pre.close()
