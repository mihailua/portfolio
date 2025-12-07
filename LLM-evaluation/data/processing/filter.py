import json
from pathlib import Path

class Config:
    project_root = Path(__file__).resolve().parents[2]

    def __init__(self, args:list):
        self.source_lang = args[1]
        self.source_lang_code = args[2]
        self.target_lang = args[3]
        self.target_lang_code = args[4]
        self.pos = args[5]

        self.raw_data = Config.project_root/'data'/'raw'/(self.source_lang+'_'+self.pos+'.jsonl')
        self.processed_data = Config.project_root/'data'/'processed'/(self.source_lang_code+'_'+self.pos+'.csv')

        self.allowed_word_symbols = ["-", "'", "’", "«", "»"] + ["\u0301", "\u0300", "\u02C8", "\u02CC"]

def quote_correct(row: list) -> str:
    corrected= ",".join('"' + i.replace('"', '""').replace('ё','е') + '"' for i in row)  + "\n"
    return corrected

def is_valid_word(word:str, cfg:Config) -> bool:
    if word is None or word ==  '':
        return False
    cleaned = "".join(ch for ch in word if ch not in cfg.allowed_word_symbols)
    return cleaned.isalpha()

def has_glosses(entry):
    return any(
        sense.get("glosses")
        for sense in entry.get("senses", [])
    )

def extract_entry_info(entry, cfg:Config) -> list:

    word = entry.get('word')

    # word-level translations
    word_target_translations = [
        t.get('word') for t in entry.get('translations', [])
        if t.get('lang') == cfg.target_lang
    ]
    word_target_translations = [t for t in word_target_translations if is_valid_word(t,cfg)]

    glosses_seen = set()
    rows = []

    synonyms_seen = []
    for sense in entry.get('senses', []):
        glosses = [i.replace('.','').replace('\n', ' ') for i in sense.get('glosses', []) if '{' not in i]

        tags = [i for i in sense.get('tags', []) if '{' not in i]

        sense_target_translations = [
            t.get('word') for t in sense.get('translations', [])
            if t.get('lang') == cfg.target_lang
        ]

        synonyms = list(set(
            t.get('word') for t in sense.get('synonyms', [])
            if t.get('word') not in synonyms_seen and t.get('word')!=word
        ))

        sense_target_translations = [t for t in sense_target_translations if is_valid_word(t,cfg)]

        for gloss in glosses:
            #if gloss in glosses_seen:
             #   break
            row = [
                    word,
                    json.dumps(word_target_translations,ensure_ascii=False).replace("''", '""'),
                    gloss,
                   # json.dumps(synonyms, ensure_ascii=False).replace("''", '""'),
                    json.dumps(sense_target_translations,ensure_ascii=False).replace("''", '""'),
                    json.dumps(tags,ensure_ascii=False).replace("''", '""'),
                ]
            row = [i.replace('\u0301','').replace('\u0300','').rstrip() for i in row]
            if row not in rows:
                rows.append(row)
            synonyms_seen.extend(synonyms)
            glosses_seen.add(gloss)

    return rows

def main(cfg:Config):
    with open(cfg.processed_data, 'w', encoding='utf-8', newline='') as csvfile:

        csvfile.write(quote_correct([
            'word',
            cfg.target_lang_code,
            'gloss',
            'gloss_'+cfg.target_lang_code,
            'tags'
        ]
        ))

        with open(cfg.raw_data, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                word_json = json.loads(line)

                if not is_valid_word(word_json['word'],cfg) or not has_glosses(word_json):
                        continue

                rows = extract_entry_info(word_json,cfg)

                for row in rows:
                    csvfile.write(quote_correct(row))

if __name__ == "__main__":
    import sys
    cfg = Config(sys.argv)
    if not cfg.processed_data.exists():
        main(cfg)