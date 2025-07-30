# textcleaner_partha/preprocess.py

import re
import spacy
import contractions
from autocorrect import Speller
from bs4 import BeautifulSoup

# Lazy initialization
_nlp = None
_spell = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise OSError("Model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    return _nlp

def get_spell():
    global _spell
    if _spell is None:
        _spell = Speller()
    return _spell

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U0001FA70-\U0001FAFF"  # extended pictographs
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def correct_spellings(text):
    spell = get_spell()
    return ' '.join([spell(w) for w in text.split()])

def expand_contractions(text):
    return contractions.fix(text)

def preprocess(
    text,
    lowercase=True,
    remove_html=True,
    remove_emoji=True,
    expand_contraction=True,
    correct_spelling=True,
    lemmatise=True,
    verbose=False,
):
    if lowercase:
        text = text.lower()

    if remove_html:
        text = remove_html_tags(text)

    if remove_emoji:
        text = remove_emojis(text)

    if expand_contraction:
        text = expand_contractions(text)

    if correct_spelling:
        try:
            text = correct_spellings(text)
        except Exception as e:
            if verbose:
                print(f"[textcleaner warning] Spelling correction skipped: {e}")

    if lemmatise:
        doc = get_nlp()(text)
        tokens = [
            token.lemma_ for token in doc
            if token.is_alpha
            and not token.is_stop
            and not token.is_punct
            and not token.like_num
            and token.pos_ in {"NOUN", "VERB", "ADJ", "ADV"}
        ]
        return ' '.join(tokens)

    return text