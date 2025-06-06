import re
from typing import List, Dict, Optional

try:
    import textstat
except ImportError:
    textstat = None # Handle gracefully if textstat is not installed


def _simple_word_tokenize(text: str) -> List[str]:
    """
    A simple tokenizer that splits text into words using regex,
    converting to lowercase and removing most punctuation.
    """
    # Find sequences of alphanumeric characters (words)
    # This also handles numbers as words and splits hyphenated words like 'world-class' into 'world', 'class'
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens


def calculate_word_count(text: str) -> int:
    """
    Counts the number of words in a given text after basic cleaning.
    """
    if not isinstance(text, str):
        return 0
    words = _simple_word_tokenize(text)
    return len(words)


def calculate_readability_flesch(text: str) -> Optional[float]:
    """
    Calculates the Flesch Reading Ease score for a given text.
    Returns None if textstat is not available or if input text is too short/empty.
    """
    if textstat is None:
        return None
    if not isinstance(text, str) or not text.strip():
        return None
    
    try:
        score = textstat.flesch_reading_ease(text)
        return score
    except ValueError:
        return None
    except Exception:
        return None


def calculate_keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
    """
    Calculates the density of specified keywords in a given text.
    """
    if not isinstance(text, str) or not text.strip():
        return {keyword: 0.0 for keyword in keywords}
    if not keywords:
        return {}

    # Use the internal simple tokenizer
    words = _simple_word_tokenize(text)
    total_words = len(words)

    if total_words == 0:
        return {keyword: 0.0 for keyword in keywords}

    keyword_densities = {}
    for keyword in keywords:
        cleaned_keyword = _simple_word_tokenize(keyword)[0] if _simple_word_tokenize(keyword) else keyword.lower()
        keyword_count = words.count(cleaned_keyword)
        density = (keyword_count / total_words) if total_words > 0 else 0.0
        keyword_densities[keyword] = density
        
    return keyword_densities
