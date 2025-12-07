import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
data = project_root/'data'/'processed'

pos_names = {'NOUN':'noun','ADJ':'adjective'}

allowed_adj_deprels = ["amod", "acl", "acl:relcl", "nmod", "flat", "fixed", 'advmod'] + [
    "compound", "nmod", "nmod:poss", "flat", "fixed"
]
allowed_noun_deprels = ["root","nsubj", "nsubj:pass", "obj", "iobj", "obl"]

class Word:

    def _get_feature(self, feature_name):
        if not self._word_obj.feats:
            return None
        for f in self._word_obj.feats.split('|'):
            name, value = f.split('=')
            if name == feature_name:
                return value
        return None

    def _get_glosses(self, path):
        glosses = []
        try:
            for chunk in pd.read_csv(path, chunksize=50000):
                matches = chunk.loc[chunk["word"] == self.word, "gloss"]
                glosses.extend(matches.tolist())
            if not glosses:
                return None
        except FileNotFoundError:
            return None
        return glosses


    def __init__(self, word, lang_code):
        self.lang = lang_code
        self._word_obj = word
        self.word = word.text
        try:
            self.pos = pos_names[word.upos]
        except KeyError:
            if self._word_obj.deprel in allowed_adj_deprels:
                self.pos = 'adjective'
            elif self._word_obj.deprel in allowed_noun_deprels:
                self.pos = 'noun'
            else:
                self.pos = ''

        self.glosses = self._get_glosses(data/(lang_code+'_'+self.pos+'s.csv'))

        self.feats = dict()
        self.feats['case'] = self._get_feature('Case')
        self.feats['definiteness'] = self._get_feature('Definite')
        self.feats['gender'] = self._get_feature('Gender')
        self.feats['number'] = self._get_feature('Number')
        self.feats['animacy'] = self._get_feature('Animacy')

        if self.pos == 'adjective':
            self.degree = self._get_feature('Degree')
            self.numtype = self._get_feature('NumType')