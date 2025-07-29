# langak/detector.py

from .alphabets import alphabets

def detect_language(text):
    text = text.lower()
    char_counts = {}

    for lang, alphabet in alphabets.items():
        count = sum(1 for char in text if char in alphabet)
        char_counts[lang] = count

    best_match = max(char_counts, key=char_counts.get)
    return best_match if char_counts[best_match] > 0 else "unknown"
