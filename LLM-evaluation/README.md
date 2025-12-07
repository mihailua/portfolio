# LLM Adjective + Noun Translation Evaluation

A toolkit for evaluating large language models by generating and analyzing
adjective–noun pairs across 20+ languages.
We're using **Google Gemini** and/or **OpenAI** generated input data, **Stanza**,
and custom linguistic processing to compare grammatical and semantic alignment between English
and target languages. The source of reference translation data are **Wiktionary**
processed dumps, which are beforehand adapted for out use (original English nouns dataset > 1.5gb)
---

## Features

- **Gemini** and **OpenAI** API wrappers for standardised input  
- Processing large lexical corporas
- Analysis using:
  - **Stanza** (POS tagging, dependency parsing)
  - **wordfreq**
  - Custom dictionary-based lemma extraction
  - BERT-like models for tokenization
- Cross-lingual evaluation suitability
- Jupyter Notebook workflows

---

## Project Structure
```
LLM-evaluation
src/
├─ src/exp #notebooks or/and .py experiments running
├─ src/factor #evaluation methods/functions
data/
├─ data/raw #storage of raw wiktextract .json datasets
├─ data/processed #storage of .csv processed datasets
├─ data/processing #algorithm for time and memory efficient data processing
models/ #Gemini, OpenAI wrappers, NLP models centralised initialissation
├─ models/env #API keys storage
objects/ #classes of AdjectiveNounPair and Word, etc.

.gitignore
README.md
requirements.txt
```

## License

MIT License

Copyright (c) 2025 MYKHAILO VAKOLIUK

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.






