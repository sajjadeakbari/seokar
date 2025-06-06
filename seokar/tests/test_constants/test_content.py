import pytest
from seokar.constants.content import ContentQuality, ReadabilityFormulas


def test_content_quality_constants():
    """Tests the values of constants in ContentQuality."""
    assert ContentQuality.MIN_WORD_COUNT_FOR_DEEP_ANALYSIS == 500
    assert ContentQuality.GOOD_READABILITY_SCORE_THRESHOLD == 60.0
    assert ContentQuality.MIN_KEYWORD_DENSITY == 0.005
    assert ContentQuality.MAX_KEYWORD_DENSITY == 0.02


def test_readability_formulas_constants():
    """Tests the values of constants in ReadabilityFormulas."""
    assert ReadabilityFormulas.FLESCH_READING_EASE == "Flesch-Kincaid Reading Ease"
    assert ReadabilityFormulas.DALE_CHALL == "Dale-Chall Readability Formula"
    assert ReadabilityFormulas.SMOG_INDEX == "SMOG Index"
