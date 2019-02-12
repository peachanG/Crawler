# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
楽天市場APIを用いて商品情報を収集するプログラム
"""

import requests
import configparser
import codecs
import os
import json
from time import sleep

import sys
sys.path.append("..")
from Preprocessing import Delete

def search(base_uri,query):
    res = requests.get(base_uri,params=query)
    return res.json()

def search_words_generator(keyword,append_keywords):
	search_list = [keyword]
	for append_keyword in append_keywords:
		search_list.append(keyword + " " + append_keyword)
	return search_list

def main():
    """設定ファイルの読み込み"""
    inifile = configparser.ConfigParser(allow_no_value = True,interpolation = configparser.ExtendedInterpolation())
    inifile.readfp(codecs.open("./RakutenIchiba_Crawler.ini",'r','utf8'))

    """保存先のパス"""
    save_dir_path = inifile.get('other_settings','Raw_save_dir_path')
    save_dir_text_path = inifile.get('other_settings','Text_save_dir_path')

    query = {}
    """共通パラメーターの設定"""
    query['applicationId'] = inifile.get('tokens','ApplicationId')
    query['affiliateId'] = inifile.get('tokens','AffiliateId')

    """サービス固有パラメーターの設定"""
    Req_URL = inifile.get('search_params','Req_URL')
    keyword = inifile.get('search_params','keyword')
    append_keywords = inifile.get('search_params','append_keywords')

    if append_keywords == "":
        search_list = [keyword]
    else:
        search_list = search_words_generator(keyword,append_keywords.split(" "))

    page = int(inifile.get('search_params','page'))
    query['hits'] = int(inifile.get('search_params','hits'))

    # query['NGKeyword'] = inifile.get('search_params','NGKeyword')
    query['orFlag'] = int(inifile.get('search_params','orFlag'))
    # query['imageFlag'] = int(inifile.get('search_params','imageFlag'))
    # query['hasReviewFlag'] = int(inifile.get('search_params','hasReviewFlag'))

    # query['itemCode'] = inifile.get('search_params','itemCode')
    # query['shopCode'] = inifile.get('search_params','shopCode')
    # query['genreId'] = inifile.get('search_params','genreId')
    # query['tagId'] = inifile.get('search_params','tagId')

    """検索実行"""
    for i,keyword in enumerate(search_list):
        print("検索ワード：" + keyword)
        query['keyword'] = keyword

        """保存先の設定"""
        if len(search_list) == 1 or keyword == search_list[0]:
            save_dir_name = keyword
        elif not len(search_list) == 1 and query['orFlag'] == 0:
            save_dir_name = keyword + "_AND"
        elif not len(search_list) == 1 and query['orFlag'] == 1:
            save_dir_name = keyword + "_OR"

        save_dir = os.path.join(save_dir_path,save_dir_name)
        os.makedirs(save_dir,exist_ok=True)
        save_dir_text = os.path.join(save_dir_text_path,save_dir_name)
        os.makedirs(save_dir_text,exist_ok=True)

        """ページごとに取得"""
        for j in range(page):
            print("page:" + str(j+1))
            query['page'] = j + 1

            res = search(Req_URL,query)
            print("取得件数：" + str(len(res["Items"])))

            with codecs.open(os.path.join(save_dir,"products" + str(j+1) + ".json"),'w','utf8') as fo:
                json.dump(res,fo,sort_keys = True, indent = 4)

            for k in range(len(res["Items"])):
                Item_dic = res["Items"][k]["Item"]
                title = Delete.title(Item_dic["itemName"])
                text = Item_dic["itemCaption"]

                with open(os.path.join(save_dir_text,title + ".txt"),'w',encoding='UTF-8') as file_text:
                    file_text.write(text)

            sleep(1)#アクセス制限対策

if __name__ == "__main__":
    main()
