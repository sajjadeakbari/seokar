class ContentQuality:
    """Thresholds and standards for content quality in SEO."""
    MIN_WORD_COUNT_FOR_DEEP_ANALYSIS: int = 500
    GOOD_READABILITY_SCORE_THRESHOLD: float = 60.0  # e.g., Flesch Reading Ease
    MIN_KEYWORD_DENSITY: float = 0.005  # 0.5%
    MAX_KEYWORD_DENSITY: float = 0.02  # 2%


class ReadabilityFormulas:
    """Standardized names for common readability formulas."""
    FLESCH_READING_EASE: str = "Flesch-Kincaid Reading Ease"
    DALE_CHALL: str = "Dale-Chall Readability Formula"
    SMOG_INDEX: str = "SMOG Index"
