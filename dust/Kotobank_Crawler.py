#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import os
import re
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import sys
sys.path.append("..")
from Preprocessing import Delete

def main():
    """取得辞書と保存先の設定"""
    eng = "World Encyclopedia"
    jp = "世界大百科事典 第２版"
    OUTPUT_DIR = XXXXXXXXXX

    opener = urllib.request.build_opener()
    opener.addheaders=[
    ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"),
    ('Accept-Language','ja,en-us;q=0.7,en;q=0.3')
    ]

    urllib.request.install_opener(opener)

    """コトバンクの辞書一覧ページ"""
    URL = 'https://kotobank.jp/dictionary/'
    try:
        soup = BeautifulSoup(urllib.request.urlopen(URL).read(),"html.parser")
    except Exception as e:
        print(e)
        print("強制終了（辞書一覧ページ）")
        sys.exit()

    for i,dic_link in enumerate(soup.findAll("a")):
        if "dictionary" in dic_link.get("href") and not "https" in dic_link.get("href") and not dic_link.get("href") == r"/dictionary/":

            dic_title = str(dic_link.text)
            dic_title = Delete.title(dic_title)#辞書の名前(日本語)

            dic_eng = dic_link.get("href").split(r"/")[2]#辞書の名前(英語)

            """指定した辞書の取得"""
            if dic_title == jp:
                print("取得対象：" + dic_title)

                """保存先の決定"""
                OUTPUT = OUTPUT_DIR + "/Raw"
                os.makedirs(OUTPUT,exist_ok=True)

                """「最初から」もしくは「続きから」辞書を取得"""
                if not os.path.exists(os.path.join(OUTPUT_DIR,eng + ".txt")):
                    print("Getting from the beginning.")
                    totalpage = 0#ページ数
                    main_URL = 'https://kotobank.jp' + str(dic_link.get("href"))
                    with open(os.path.join(OUTPUT_DIR,eng + ".txt"),'w',encoding='UTF-8') as fi_info:
                        fi_info.write(str(totalpage) + "\n" + main_URL)
                else:
                    print("Getting from the continuation.")
                    with open(os.path.join(OUTPUT_DIR,eng + ".txt"),'r') as fi_info:
                        infos = fi_info.readlines()
                        totalpage = int(infos[0])-1
                        main_URL = infos[1]

                """ページ内に「次へ」があったらループ"""
                judge = True#「次へ」の有無
                while judge:
                    totalpage += 1
                    print(str(totalpage) + "ページ目")

                    """辞書内のページ"""
                    try:
                        search_soup = BeautifulSoup(urllib.request.urlopen(main_URL).read(),"html.parser")
                    except:
                        with open(os.path.join(OUTPUT_DIR,eng + ".txt"),'w',encoding='UTF-8') as fi_info:
                            fi_info.write(str(totalpage) + "\n" + main_URL)
                        print("強制終了（辞書内の見出しページ）")
                        sys.exit()

                    linklists = search_soup.findAll("a",rel="dic_" + str(dic_eng))
                    print("リンク数：" + str(len(linklists)))
                    for link in linklists:
                        """辞書の各項目のページ"""
                        item_URL = 'https://kotobank.jp' + str(link.get('href'))
                        try:
                            item_soup = BeautifulSoup(urllib.request.urlopen(item_URL).read(),"html.parser")
                        except Exception as e:
                            with open(os.path.join(OUTPUT_DIR,eng + ".txt"),'w',encoding='UTF-8') as fi_info:
                                fi_info.write(str(totalpage) + "\n" + main_URL)
                            print("強制終了（項目のページ）")
                            print(e)
                            sys.exit()

                        """タイトルとテキストの取得"""
                        dics = item_soup.find_all('article')
                        for dic in dics:
                            if dic_title in str(dic("h2")) :

                                title = str(dic("h3")[0])
                                title = BeautifulSoup(title,"lxml")
                                title = title.get_text()
                                title = Delete.title(title)

                                if len(dic("section")) == 1:
                                    text = str(dic("section")[0])
                                else:
                                    text = ""
                                    for x in dic("section"):
                                        text += str(x)

                                text = BeautifulSoup(text,"lxml")
                                text = text.get_text()

                                with open(os.path.join(OUTPUT,title + ".txt"),'w',encoding='UTF-8') as file_out:
                                    print(title)
                                    file_out.write(text)

                    """「次へ」の有無判断"""
                    nexts = search_soup.find("li",class_="next")
                    if not nexts == None:
                        judge = True
                        main_URL = 'https://kotobank.jp' + str(nexts.find("a").get("href"))
                    else:
                        judge = False

if __name__ == "__main__":
	main()
