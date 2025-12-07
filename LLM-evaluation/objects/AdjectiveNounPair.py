from .Word import Word
from models.initialisation import models


class AdjectiveNounPair:

    def __init__(self, pair:str, lang_code:str):
        pair = pair.replace('ё','е')
        self.original = pair
        self.lang_code = lang_code

        nlp = models.get_stanza(lang_code)
        pair = nlp(pair)

        word1 = Word(pair.sentences[0].words[0], lang_code)
        word2 = Word(pair.sentences[0].words[1], lang_code)

        if len(pair.sentences[0].words) > 2:
            manual1 = nlp([[self.original.split(' ')[0]]]).sentences[0].words[0]
            manual2 = nlp([[self.original.split(' ')[1]]]).sentences[0].words[0]
            word1 = Word(manual1, lang_code)
            word2 = Word(manual2, lang_code)

        self.adj, self.noun = (
            (word1, word2) if word1.pos == "adjective" else (word2, word1)
        )
