# 🧹 textcleaner

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

Install directly from GitHub:

```bash
pip install git+https://github.com/partha6369/textcleaner.git
```

## 🧠 Usage

```python
from textcleaner import preprocess

text = "I can't believe it's already raining! 😞 <p>Click here</p>"
cleaned = preprocess(text)
print(cleaned)
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

MIT License © Partha Majumdar
