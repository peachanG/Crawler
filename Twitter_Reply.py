#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
リプライ取得
ユーザ名で検索かけてから，in_reply_to_status_idとidが一致したらリプライと定義．
"""

import configparser
import codecs
import twitter
import os
import time
import calendar

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

"""UNIX時間に変換"""
def unix(created_at):
    time_utc = time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    return int(unix_time)

"""日本時間に変換"""
def japan(created_at):
    time_utc = time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    return int(time.strftime("%Y%m%d%H%M%S", time_local))

def main():
    """設定ファイルの読み込み"""
    inifile = configparser.ConfigParser(allow_no_value=True,interpolation=configparser.ExtendedInterpolation())
    inifile.readfp(codecs.open('./Reply.ini',"r","utf8"))

    """アクセストークンの読み込み"""
    ConsumerKey=inifile.get('tokens','ConsumerKey')
    ConsumerSecret=inifile.get('tokens','ConsumerSecret')
    AccessToken=inifile.get('tokens','AccessToken')
    AccessTokenSecret=inifile.get('tokens','AccessTokenSecret')

    """検索パラメータの読み込み"""
    query = inifile.get('search_params','query')#検索ワード(元ツイートのユーザ名)
    id = inifile.get('search_params','id')#元ツイートid
    geocode=get_or_setDefault(inifile.get,'search_params', 'geocode')
    lang = get_or_setDefault(inifile.get,'search_params', 'lang')
    locale = get_or_setDefault(inifile.get,'search_params', 'locale')
    result_type = get_or_setDefault(inifile.get,'search_params', 'result_type')
    count = get_or_setDefault(inifile.get,'search_params', 'count')
    until = get_or_setDefault(inifile.get,'search_params', 'until')
    since_id=get_or_setDefault(inifile.get,'search_params', 'since_id')
    max_id=get_or_setDefault(inifile.get,'search_params', 'max_id')
    include_entities=get_or_setDefault(inifile.get,'search_params', 'include_entities')

    """検索パラメータ(非ポスト)の読み込み"""
    search_count=get_or_setDefault(inifile.getint,'search_params', 'search_count',default=1)
    if search_count == 0:
        search_count = True

    """保存先の設定"""
    save_dir_path = inifile.get('other_settings','save_dir_path')
    save_name = inifile.get('other_settings','save_dir_name')
    file = open(os.path.join(save_dir_path,save_name + ".csv"),'w',encoding='utf-8-sig')

    """検索実行"""
    t=twitter.Twitter(auth=twitter.OAuth(AccessToken, AccessTokenSecret, ConsumerKey, ConsumerSecret),retry=True)
    collected_data_count = 0#取得リプライ数
    searched_data_count = 0#探索ツイート数
    end_count = 0#リプライが1件も取得できなかった回数

    while search_count:
        stop_count = 0#n_reply_to_status_idとidが一致しなかった回数
        try:
            datas=t.search.tweets(q=query,lang=lang,locale=locale,result_type=result_type,count=count,max_id=max_id)
            #datas=t.search.tweets(q=query,geocode=geocode,lang=lang,locale=locale,result_type=result_type,count=count,until=until,since_id=since_id,max_id=max_id,include_entities=include_entities)
        except Exception as e:
            print(e)
            break

        if datas["statuses"] == []:
            print("There are not replies")
            break

        searched_data_count += len(datas["statuses"])
        print("searched %d tweets"%searched_data_count)

        """in_reply_to_status_idとidが一致したらリプライとする"""
        for i in range(len(datas["statuses"])):
            if datas["statuses"][i]["in_reply_to_status_id"] == int(id):
                collected_data_count += 1
                print("collected %d replies"%collected_data_count)
                file.write("reply" + str(collected_data_count) + ",")
                print(datas["statuses"][i]["created_at"])
                file.write(str(unix(datas["statuses"][i]["created_at"])) + ",")
                file.write(str(japan(datas["statuses"][i]["created_at"])) + ",")
                file.write(datas["statuses"][i]["text"].replace("\r","").replace("\n","") + "\n")
            else:
                stop_count += 1
                continue

        if  stop_count == len(datas["statuses"]):
            end_count += 1
        else:
            end_count = 0

        if end_count == 30:#リプライが30回取得できなかったら強制終了
            break

        """次の検索時の最大max_idの設定"""
        max_id = datas["statuses"][-1]["id"]
        max_id = str(int(max_id)-1)
        # print("max_id:"+ str(max_id))

        if type(search_count) is int:
            search_count -= 1

        if searched_data_count == 0:
            print("target tweets are nothing")

    file.close()

if __name__=="__main__":
	main()
