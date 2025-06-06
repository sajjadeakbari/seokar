import re
from typing import List, Dict, Optional

try:
    import textstat
except ImportError:
    textstat = None # Handle gracefully if textstat is not installed

try:
    from nltk.tokenize import word_tokenize
    # NLTK data might need to be downloaded, but we assume it's available for this step.
    # import nltk
    # nltk.download('punkt') # Example of what might be needed
except ImportError:
    word_tokenize = None # Handle gracefully if NLTK is not installed


def calculate_word_count(text: str) -> int:
    """
    Counts the number of words in a given text after basic cleaning.
    """
    if not isinstance(text, str):
        return 0
    # Remove punctuation and convert to lowercase
    cleaned_text = re.sub(r'[^\w\s]', '', text).lower()
    words = cleaned_text.split()
    return len(words)


def calculate_readability_flesch(text: str) -> Optional[float]:
    """
    Calculates the Flesch Reading Ease score for a given text.
    Returns None if textstat is not available or if input text is too short/empty.
    """
    if textstat is None:
        # print("Warning: textstat library not found. Cannot calculate Flesch Reading Ease.") # For debugging
        return None
    if not isinstance(text, str) or not text.strip():
        return None
    
    # textstat can raise ValueError for very short texts
    try:
        score = textstat.flesch_reading_ease(text)
        return score
    except ValueError:
        # print(f"Warning: Text too short or invalid for Flesch Reading Ease calculation: '{text[:50]}...'") # For debugging
        return None
    except Exception:
        # Catch any other unexpected errors from textstat
        return None


def calculate_keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
    """
    Calculates the density of specified keywords in a given text.
    """
    if word_tokenize is None:
        # print("Warning: NLTK 'punkt' tokenizer not found. Cannot calculate keyword density.") # For debugging
        return {keyword: 0.0 for keyword in keywords}
    if not isinstance(text, str) or not text.strip():
        return {keyword: 0.0 for keyword in keywords}
    if not keywords:
        return {}

    # Clean text: convert to lowercase and remove punctuation
    cleaned_text = re.sub(r'[^\w\s]', '', text).lower()
    
    # Tokenize the cleaned text
    words = word_tokenize(cleaned_text)
    total_words = len(words)

    if total_words == 0:
        return {keyword: 0.0 for keyword in keywords}

    keyword_densities = {}
    for keyword in keywords:
        cleaned_keyword = re.sub(r'[^\w\s]', '', keyword).lower()
        keyword_count = words.count(cleaned_keyword)
        density = (keyword_count / total_words) if total_words > 0 else 0.0
        keyword_densities[keyword] = density
        
    return keyword_densities
