import stanza
from transformers import AutoTokenizer, AutoModelForMaskedLM, logging
from sentence_transformers import SentenceTransformer
from wordfreq import word_frequency
from objects.Word import Word

class ModelManager:
    logging.set_verbosity_error()

    def __init__(self):
        self.transformer_cache = {}
        self._embedder = None
        self.stanza_cache = {}

    @staticmethod
    def get_frequency(word:Word)->float:
        return word_frequency(word.word, word.lang, wordlist="large")

    @property
    def embedder(self):
        if self._embedder is not None:
            return self._embedder
        self._embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        return self._embedder

    def transformer(self,lang_code):
        if lang_code in self.transformer_cache:
            return self.transformer_cache[lang_code]
        if lang_code == 'ru':
            model_name = 'DeepPavlov/rubert-base-cased'
        else:
            model_name = "xlm-roberta-base"
        tok = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        mod = AutoModelForMaskedLM.from_pretrained(model_name)
        mod.eval()
        self.transformer_cache[lang_code] = tok, mod

        return tok, mod

    def get_stanza(self, lang):
        if lang in self.stanza_cache:
            return self.stanza_cache[lang]

        nlp = stanza.Pipeline(lang=lang, processors="tokenize,pos,lemma,depparse",verbose=False, tokenize_pretokenized=True)

        self.stanza_cache[lang] = nlp
        return nlp

models = ModelManager()
