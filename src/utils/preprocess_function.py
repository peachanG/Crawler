import spacy
import MeCab


class Base_preprocess(object):
    def __init__(self, dict_option='', delete_POS_list=['BOS/EOS', '記号'], extract_POS_list=[]):
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

    def _build_api(self, dict_option):
        """
        Subclasses should override for any actions to run.
        """
        api = None
        return api

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


class MecabPreprocess(Base_preprocess):
    def __init__(self, dict_option='', delete_POS_list=['BOS/EOS', '記号'], extract_POS_list=[]):
        super(MecabPreprocess, self).__init__(dict_option, delete_POS_list, extract_POS_list)

    def _build_api(self, dict_option):
        api = MeCab.Tagger(dict_option)
        return api

    def wakati(self, text):
        self.api.parse('')
        node = self.api.parseToNode(text)
        output = ""
        while node:
            word = node.surface
            info = node.feature.split(',')
            if not info[0] in self.delete_POS_list and self._extract_word(info[0]):
                output += word
                output += " "
            node = node.next
        output = output[:-1]
        return output

    def lemma_wakati(self, text):
        node = self.api.parseToNode(text)
        output = ""
        while node:
            info = node.feature.split(',')
            word = info[6]
            if not info[0] in self.delete_POS_list and self._extract_word(info[0]):
                output += word
                output += " "
            node = node.next
        output = output[:-1]
        return output


class GinzaPreprocess(Base_preprocess):
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
                if not info[0] in self.delete_POS_list and self._extract_word(info[0]):
                    output += word
                    output += " "
        output = output[:-1]
        return output

    def lemma_wakati(self, text):
        doc = self.api(text)
        output = ""
        for sent in doc.sents:
            for token in sent:
                word = token.lemma_
                info = token._.pos_detail.split(',')
                if not info[0] in self.delete_POS_list and self._extract_word(info[0]):
                    output += word
                    output += " "
        output = output[:-1]
        return output
