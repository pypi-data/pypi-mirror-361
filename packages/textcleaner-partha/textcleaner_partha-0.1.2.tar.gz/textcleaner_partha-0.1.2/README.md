# 🧹 textcleaner-partha

[![PyPI version](https://img.shields.io/pypi/v/textcleaner-partha?color=blue)](https://pypi.org/project/textcleaner-partha/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight and reusable text preprocessing package for NLP tasks.
It cleans text by removing HTML tags and emojis, expanding contractions, correcting spelling, and performing lemmatization using spaCy.

## ✨ Features
	•	✅ HTML tag and emoji removal
	•	✅ Contraction expansion (e.g., “can’t” → “cannot”)
	•	✅ Spelling correction with autocorrect
	•	✅ Lemmatization using spaCy (en_core_web_sm)
	•	✅ Filters out stopwords, punctuation, numbers
	•	✅ Retains only nouns, verbs, adjectives, and adverbs


## 🚀 Installation

### From PyPI:

```bash
pip install textcleaner-partha
```

Install directly from GitHub:

```bash
pip install git+https://github.com/partha6369/textcleaner.git
```

## 🧠 Usage

```python
from textcleaner import preprocess

text = "I can't believe it's already raining! 😞 <p>Click here</p>"

# Default usage (all features enabled)
cleaned = preprocess(text)
print(cleaned)

# Custom usage with optional features disabled
cleaned_partial = preprocess(
    text,
    lemmatize=False,            # Skip spaCy processing (lemmatisation, POS filtering)
    correct=False,              # Skip spelling correction
    expand=False                # Skip contraction expansion
)
print(cleaned_partial)
```

## 🔧 Parameters

The preprocess() function offers flexible control over each text cleaning step. You can selectively enable or disable operations using the parameters below:

```python
def preprocess(
    text,
    lowercase=True,
    remove_html=True,
    remove_emoji=True,
    expand=True,
    correct=True,
    lemmatize=True,
)
```

## 📦 Dependencies

	•	spacy
	•	autocorrect
	•	contractions

You can install them manually or via the included requirements.txt:
```bash
pip install -r requirements.txt
```

And download the required spaCy model:
```bash
python -m spacy download en_core_web_sm
```


## 📄 License

MIT License © Dr. Partha Majumdar
