import re

import mojimoji

import spacy
import MeCab


def text_norm(text, delete_reply=False, return_empty_phrase='shindanmaker'):
    text = text.lower()

    if return_empty_phrase in text:
        text = ''

    # アルファベット, 記号（全角→半角), #かな（半角→全角）#数字（全角→半角）
    text = mojimoji.zen_to_han(text, kana=False)

    # ()でかこまれた文章を削除
    text = re.sub('\(.*\)', '', text)
    text = re.sub('\【.*\】', '', text)
    text = re.sub('\-.*\-', '', text)
#    text = re.sub('\『.*\』', '', text)

    # ~~でかこまれた文章を削除
    text = re.sub('\~.*\~', '', text)
    # 改行を削除
    text = re.sub('\n', '', text)

    # 特定のtweetを削除
    # RT
    if text[:2] == 'rt':
        return ''
    # リプライ
    if delete_reply:
        if text[:1] == '@':
            return ''

    # URL
    text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    # ユーザ名
    text = re.sub(r'@[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    # ハッシュタグ
    text = re.sub(r'#[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    # unicode非対応の文字の削除
    symbol = re.sub(r'[\u0000-\uE0FFF]', "", text)
    if not symbol == "":
        text = re.sub("[%s]" % symbol, "", text)

    # 空白削除
    text = text.strip()
    return text


class BasePreprocess(object):
    def __init__(self, dict_option='', delete_POS_list=['BOS/EOS', '記号'], extract_POS_list=[], delete_human_name=True):
        """textの前処理(親クラス).

        # Arguments
            dict_option: それぞれのAPIの初期設定に必要な辞書やモデル
            delete_POS_list: 取り除く品詞のリスト
            extract_POS_list: 抽出する品詞のリスト(なければすべて)

        # How to use
            preprocess = Base_preprocess()
            output = preprocess.wakati(text)

        """
        self.api = self._build_api(dict_option)
        self.delete_POS_list = delete_POS_list
        self.extract_POS_list = extract_POS_list
        self.delete_human_name = delete_human_name

    def _build_api(self, dict_option):
        """
        Subclasses should override for any actions to run.
        """
        api = None
        return api

    def _text_norm(self, text):
        index = text.rfind('by')
        if index < 0:
            return text
        else:
            return text[:index]

    def _delete_judge(self, info):
        # 削除に指定されたPOSの単語の場合 True
        if info[0] in self.delete_POS_list:
            return True
        # 人名の場合 True
        if self.delete_human_name and info[2] == '人名':
            return True
        # 抽出に指定されたPOSの単語の場合
        if len(self.extract_POS_list) != 0:
            if info[0] in self.extract_POS_list:
                return False
            else:
                return True
        return False

    def _extract_word(self, POS):
        if len(self.extract_POS_list) == 0 or POS in self.extract_POS_list:
            return True
        else:
            return False

    def wakati(self, text):
        """
        Subclasses should override for any actions to run.
        """
        output = None
        return output

    def lemma_wakati(self, text):
        """
        Subclasses should override for any actions to run.
        """

        output = None
        return output


class MecabPreprocess(BasePreprocess):
    def __init__(self, dict_option='', delete_POS_list=['BOS/EOS', '記号'], extract_POS_list=[], delete_human_name=True):
        super(MecabPreprocess, self).__init__(dict_option, delete_POS_list, extract_POS_list, delete_human_name)

    def _build_api(self, dict_option):
        api = MeCab.Tagger(dict_option)
        api.parse('')
        return api

    def wakati(self, text):
        node = self.api.parseToNode(text)
        output = ""
        while node:
            word = node.surface
            info = node.feature.split(',')
            if not self._delete_judge(info) and word != '':
                output += word
                output += " "
            node = node.next
        output = output[:-1]
        output = self._text_norm(output)
        return output

    def lemma_wakati(self, text):
        node = self.api.parseToNode(text)
        output = ""
        while node:
            info = node.feature.split(',')
            word = info[6]
            if not self._delete_judge(info) and word != '':
                output += word
                output += " "
            node = node.next
        output = output[:-1]
        output = self._text_norm(output)
        return output


class GinzaPreprocess(BasePreprocess):
    def __init__(self, dict_option='ja_ginza_nopn', delete_POS_list=['BOS/EOS', '補助記号'], extract_POS_list=[]):
        super(GinzaPreprocess, self).__init__(dict_option, delete_POS_list, extract_POS_list)

    def _build_api(self, dict_option):
        api = spacy.load('ja_ginza_nopn')
        return api

    def wakati(self, text):
        doc = self.api(text)
        output = ""
        for sent in doc.sents:
            for token in sent:
                word = token.orth_
                info = token._.pos_detail.split(',')
                if not self._delete_judge(info) and word != '':
                    output += word
                    output += " "
        output = output[:-1]
        output = self._text_norm(output)
        return output

    def lemma_wakati(self, text):
        doc = self.api(text)
        output = ""
        for sent in doc.sents:
            for token in sent:
                word = token.lemma_
                info = token._.pos_detail.split(',')
                if not self._delete_judge(info) and word != '':
                    output += word
                    output += " "
        output = output[:-1]
        output = self._text_norm(output)
        return output
