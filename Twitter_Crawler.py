#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TwitterAPIを用いてTweetを収集するプログラム
"""

import configparser
import codecs
import os
import json
import twitter

"""
関数がエラー終了した際のラッピング．失敗した際にデフォルト値を返す．
@arg
	func:実際に実行する関数
	*args:その関数に渡す引数
	default:その関数がエラー終了した際に返す値
@ret
	関数が実行可能だった場合はその結果．エラー終了した場合はデフォルト値
"""
def get_or_setDefault(func,*args,default=''):
	value = default
	try:
		value = func(*args)
	except configparser.NoOptionError:
		pass
	except:
		pass
	return value

def main():
	"""設定ファイルの読み込み"""
	inifile = configparser.ConfigParser(allow_no_value = True,interpolation = configparser.ExtendedInterpolation())
	inifile.readfp(codecs.open("./Twitter_Crawler.ini",'r','utf8'))

	"""アクセストークンの読み込み"""
	ConsumerKey = inifile.get('tokens','ConsumerKey')
	ConsumerSecret = inifile.get('tokens','ConsumerSecret')
	AccessToken = inifile.get('tokens','AccessToken')
	AccessTokenSecret = inifile.get('tokens','AccessTokenSecret')

	"""検索パラメータの読み込み"""
	#q = inifile.get('search_params', 'query')
	q = "。,！,？+-\n+-笑+-「+-」+-w+-ｗ+-(+-（+-http+-https+exclude:retweets"#URL投稿やリツイートを含まないようにクエリ設定
	geocode = get_or_setDefault(inifile.get,'search_params','geocode')
	lang = get_or_setDefault(inifile.get,'search_params','lang')
	locale = get_or_setDefault(inifile.get,'search_params','locale')
	result_type = get_or_setDefault(inifile.get,'search_params','result_type')
	count = get_or_setDefault(inifile.get,'search_params','count')
	until = get_or_setDefault(inifile.get,'search_params','until')
	since_id = get_or_setDefault(inifile.get,'search_params','since_id')
	max_id = get_or_setDefault(inifile.get,'search_params','max_id')
	include_entities = get_or_setDefault(inifile.get,'search_params','include_entities')

	"""検索パラメータ(非ポスト)の読み込み"""
	search_count = get_or_setDefault(inifile.getint,'search_params','search_count',default=1)
	if search_count == 0:
		search_count = True

	"""保存先の設定"""
	save_dir_path = inifile.get('other_settings','Tweet_save_dir_path')
	save_dir_name = inifile.get('other_settings','save_dir_name')
	save_dir = os.path.join(save_dir_path,save_dir_name)

	"""「最初から」もしくは「続きから」ツイートを取得"""
	if os.path.exists(save_dir):
		print("Getting from the continuation.")
		with open(os.path.join(save_dir,save_dir_name + ".txt"),'r') as file_info:
			infos = file_info.readlines()
			max_id = int(infos[0].split(":")[1])#maxidの設定
			tweets_no = int(infos[1].split(":")[1])#保存時の通し番号
			collected_data_count = int(infos[2].split(":")[1])#取得ツイート数
	else:
		print("Getting from the beginning.")
		os.mkdir(save_dir)
		tweets_no = 1#保存時の通し番号
		collected_data_count = 0#取得ツイート数

	"""検索実行"""
	t = twitter.Twitter(auth=twitter.OAuth(AccessToken,AccessTokenSecret,ConsumerKey,ConsumerSecret),retry = True)

	while search_count:
		try:
			datas = t.search.tweets(q=q,geocode=geocode,lang=lang,locale=locale,result_type=result_type,count=count,until=until,since_id=since_id,max_id=max_id,include_entities=include_entities)
		except Exception as e:
			print(e)
			break
		if datas["statuses"] == []:
			print("There are not tweets.")
			break

		with codecs.open(os.path.join(save_dir,"tweets"+str(tweets_no)+".json"),'w','utf8') as fo:
			json.dump(datas["statuses"],fo,indent=4,ensure_ascii=False)

		tweets_no += 1#保存時の通し番号
		collected_data_count += len(datas["statuses"])
		print("collected %d tweets"%collected_data_count)#取得ツイート数表示

		"""次の検索時の最大max_idの設定"""
		max_id = datas["statuses"][-1]["id"]#収集したデータからmax_idを直接取得する．next_paramsはたまに取得できないときがある？
		max_id = str(int(max_id)-1)#検索はmax_id未満に対して行うはずなのだが，なぜか重複するため-1する．
		# print("max_id:"+ str(max_id))#maxidの表示

		with open(os.path.join(save_dir,save_dir_name + ".txt"),'w') as file_info:
			file_info.write("next_max_id:" + str(max_id) + "\n" + "tweets_no:" + str(tweets_no) + "\n" + "collected tweets:" + str(collected_data_count))

		if type(search_count) is int:
			search_count -= 1

	if collected_data_count == 0:
		print("Target tweets are nothing.")

if __name__ == "__main__":
	main()
