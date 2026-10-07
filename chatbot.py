# import libraries

import json
import random
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Load dataset
# ---------------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "intents.json"

with open(DATA_FILE, "r", encoding="utf-8") as file:
    intents = json.load(file)["intents"]

CONFIDENCE_THRESHOLD = 0.7

# Common words ignored while matching
STOP_WORDS = {
    "what", "is", "are", "a", "an", "the", "of", "me", "you", "i", "am", "to",
    "do", "does", "how", "which", "tell", "about", "explain", "define", "please",
    "kya", "hai", "hain", "ka", "ki", "ke", "mein", "se", "ko", "kaun",
    "karo", "batao", "mujhe", "tum", "aap", "main", "mai", "hoon", "hu",
}


# ---------------------------------------------------------------------------
# Text helpers

def preprocess_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def content_words(text):
    words = text.split()
    important = [w for w in words if w not in STOP_WORDS]
    return set(important) if important else set(words)


# ---------------------------------------------------------------------------
# Prepare English and Hindi patterns separately
# ---------------------------------------------------------------------------
prepared_intents = []

for item in intents:
    for lang in ("en", "hi"):
        if lang in item:
            prepared_intents.append({
                "intent": item["intent"],
                "lang": lang,
                "patterns": [preprocess_text(p) for p in item[lang]["patterns"]],
                "responses": item[lang]["responses"],
            })

# Words that appear in only one language (used for language detection)

_en_vocab = {w for i in prepared_intents if i["lang"] == "en"
             for p in i["patterns"] for w in p.split()}
_hi_vocab = {w for i in prepared_intents if i["lang"] == "hi"
             for p in i["patterns"] for w in p.split()}
EN_ONLY = _en_vocab - _hi_vocab
HI_ONLY = _hi_vocab - _en_vocab


def detect_language(user_text):
    words = user_text.split()
    hi_count = sum(w in HI_ONLY for w in words)
    en_count = sum(w in EN_ONLY for w in words)
    return "hi" if hi_count > en_count else "en"


# Intent matching

def calculate_score(user_text, pattern):
    pattern_words = content_words(pattern)
    user_words = set(user_text.split())
    matched = pattern_words & user_words
    return len(matched) / len(pattern_words), len(matched)


def find_intent(user_text):
    user_text = preprocess_text(user_text)
    user_lang = detect_language(user_text)

    best = ("unknown", user_lang)
    best_key = (0.0, 0, 0)

    for item in prepared_intents:
        for pattern in item["patterns"]:
            if user_text == pattern:
                return item["intent"], item["lang"], 1.0

            score, matched = calculate_score(user_text, pattern)
            key = (score, int(item["lang"] == user_lang), matched)

            if key > best_key:
                best_key = key
                best = (item["intent"], item["lang"])

    return best[0], best[1], best_key[0]


# Response generation

def generate_response(intent, lang):
    for item in prepared_intents:
        if item["intent"] == intent and item["lang"] == lang:
            return random.choice(item["responses"])
    return ("Sorry, I don't understand that yet." if lang == "en"
            else "Maaf kijiye, mujhe ye samajh nahi aaya.")


def get_response(user_input):
    """Main function used by the UI. Returns (response_text, intent_name)."""
    intent, lang, score = find_intent(user_input)

    if score < CONFIDENCE_THRESHOLD:
        intent = "unknown"
        lang = detect_language(preprocess_text(user_input))

    return generate_response(intent, lang), intent






