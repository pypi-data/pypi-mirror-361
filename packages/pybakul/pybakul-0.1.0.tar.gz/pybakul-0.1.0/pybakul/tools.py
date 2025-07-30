from collections import Counter

def char_frequency(text: str) -> dict:
    """Return frequency of each character in the input text."""
    return dict(Counter(text))

def reverse_string(text: str) -> str:
    """Return the reversed version of the input text."""
    return text[::-1]
