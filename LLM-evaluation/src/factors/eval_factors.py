from pathlib import Path
import re
import json
import numpy as np
import pandas as pd
import torch
import math
from objects.AdjectiveNounPair import AdjectiveNounPair
from models.initialisation import models

project_root = Path(__file__).resolve().parents[2]

def cosine_similarity(source:AdjectiveNounPair, target:AdjectiveNounPair)->float:
    phrase1 = source.original
    phrase2 = target.original
    vector1 = models.embedder.encode(phrase1)
    vector2 = models.embedder.encode(phrase2)

    return round(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)),3)

def _one_side_pseudo_ppl(phrase: str, word: str, lang_code) -> float:
    word_or = word
    tok, model = models.transformer(lang_code)
    enc = tok(phrase, return_tensors="pt")
    input_ids = enc["input_ids"][0]
    word = tok(word, add_special_tokens=False)["input_ids"]

    match_pos = None
    for i in range(len(input_ids) - len(word)):
        if input_ids[i:i+len(word)].tolist() == word:
            match_pos = (i, i + len(word))
            break

    if match_pos is None:
        raise ValueError(f"Could not find word '{word_or}' in phrase '{phrase}' after tokenization.")

    start, end = match_pos

    masked = input_ids.clone()
    for idx in range(start, end):
        masked[idx] = tok.mask_token_id

    with torch.no_grad():
        out = model(
            input_ids=masked.unsqueeze(0),
            labels=input_ids.unsqueeze(0)
        )
        loss = out.loss.item()

    return math.exp(loss)

def _pseudo_perplexity(phrase:str, lang_code) -> float:
    tok, model = models.transformer(lang_code)
    enc = tok(phrase, return_tensors="pt")
    input_ids = enc["input_ids"][0]

    losses = []

    for i in range(1, len(input_ids) - 1):
        masked = input_ids.clone()
        masked[i] = tok.mask_token_id

        with torch.no_grad():
            out = model(
                input_ids=masked.unsqueeze(0),
                labels=input_ids.unsqueeze(0)
            )
            losses.append(out.loss.item())

    return math.exp(sum(losses) / len(losses))

def is_order_correct(pair:AdjectiveNounPair):
    pair_direct = pair.original
    pair_indirect = pair.original.split(' ')[1]+' '+ pair.original.split(' ')[0]
    perplexity_direct = _pseudo_perplexity(pair_direct, pair.lang_code)
    perplexity_indirect = _pseudo_perplexity(pair_indirect, pair.lang_code)

   # print(perplexity_direct, perplexity_indirect, pair.original)

    if perplexity_direct < perplexity_indirect:
        return 1
    else:
        return 0

def natural_fluency(pair:AdjectiveNounPair)->float:
    natf_score = 0
    weights = {
        'gender':1/6,
        'number':1/6,
        'definiteness':1/6,
        'animacy':1/6,
        'case': 1/6,
        'word_order': 1/6
    }
    for feat in set(pair.adj.feats.keys()) | set(pair.noun.feats.keys()):
        if pair.adj.feats[feat] == pair.noun.feats[feat]:
            natf_score += weights[feat]
        elif pair.adj.feats[feat] is None or pair.noun.feats[feat] is None:
            natf_score += weights[feat]/2

    natf_score += weights['word_order']*is_order_correct(pair)

    return round(natf_score,3)

def commonness_match(source:AdjectiveNounPair, target:AdjectiveNounPair)->float:

    a = _one_side_pseudo_ppl(source.original,source.noun.word, 'ru')
    b = _one_side_pseudo_ppl(source.original,source.adj.word, 'ru')
    source_ratio = a / b
    a = _one_side_pseudo_ppl(target.original,target.noun.word, 'ru' )
    b = _one_side_pseudo_ppl(target.original,target.adj.word, 'ru')
    target_ratio = a / b
    source_to_target = source_ratio/target_ratio
    maxratio = 5

    r = max(source_to_target, 1 / maxratio)
    r = min(r, maxratio)
    score = 1 - abs(math.log(r)) / math.log(maxratio)
    return max(0, min(1, round(score,3)))

def back_translation_match(pair:AdjectiveNounPair, translation:AdjectiveNounPair)->float:
    score = 0
    if pair.adj == translation.adj:
        score += 0.4
    if pair.noun == translation.noun:
        score += 0.4
    if is_order_correct(translation):
        score+=0.2
    return score

def _read_translations(source_word, source_lang_code, target_lang_code, pos)->list:
    translations = []
    translations_seen = set()
    try:
        for chunk in pd.read_csv(project_root/'data'/'processed'/(source_lang_code+'_'+pos+'s.csv'), chunksize=50000):
            check = chunk.loc[chunk["word"] == source_word, ['gloss','tags']]
            if 'form-of' in check['tags']:
                source_word = re.search(r"of\s+([^\s(]+)\s*\(", check.loc[0,'gloss'])
                _read_translations(source_word.group(1), source_lang_code, target_lang_code, pos)
            matches = chunk.loc[chunk["word"] == source_word, [target_lang_code, 'gloss_'+target_lang_code]]
            for trans_words in matches.values.flatten():
                trans_words = json.loads(trans_words)
                for trans_word in trans_words:
                    if trans_word not in translations_seen:
                        translations.append(trans_word.replace('ё','е'))
                        translations_seen.add(trans_word)
        return translations
    except FileNotFoundError:
        raise "Incorrect dictionary path"
    except KeyError:
        raise "Dictionary not adapted for target language"


def _base_form(word:str, lang_code:str, pos:str, recheck = True)->str:
    found = False
    try:
        for chunk in pd.read_csv(project_root/'data'/'processed'/(lang_code+'_'+pos+'s.csv'), chunksize=50000):
            check = chunk.loc[chunk["word"] == word, ['gloss','tags']]
            if len(check)>0:
                found = True
            if check['tags'].str.contains('form-of', na=False).any():
                form_of_row = check[check['tags'].str.contains('form-of', na=False)]
                newword = re.search(r"of\s+([^\s(]+)", form_of_row.iloc[0]['gloss'])
                if not newword is None:
                    return newword.group(1)
        if not found and recheck:
            return _base_form(word[:-1], lang_code, pos, recheck=False)
        else:
            return word

    except FileNotFoundError:
        raise "Incorrect dictionary path"
    except KeyError:
        raise "Dictionary not adapted for target language"



def dictionary_translation_match(source:AdjectiveNounPair, target:AdjectiveNounPair)->float:
    score = 0

    base_form_adj_source = _base_form(source.adj.word, source.lang_code, 'adjective')
    base_form_noun_source = _base_form(source.noun.word, source.lang_code, 'noun')

    adj_translations = _read_translations(base_form_adj_source,source_lang_code= source.lang_code, target_lang_code=target.lang_code, pos='adjective')
    noun_translations = _read_translations(base_form_noun_source,source_lang_code= source.lang_code,target_lang_code=target.lang_code, pos='noun')

    base_form_adj = _base_form(target.adj.word, target.lang_code, 'adjective')
    base_form_noun = _base_form(target.noun.word, target.lang_code, 'noun')

    if base_form_adj in adj_translations:
        score += 0.4
        if base_form_adj == adj_translations[0]:
            score += 0.1
    if base_form_noun in noun_translations:
        score += 0.4
        if base_form_noun == noun_translations[0]:
            score += 0.1
    return score