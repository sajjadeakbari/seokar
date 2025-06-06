import pytest
from unittest.mock import patch, MagicMock

# Mock textstat and nltk.tokenize.word_tokenize at the module level if they are imported conditionally
# This ensures that our tests don't fail just because these libraries aren't installed globally for testing.
# The actual functions in text_analysis.py handle their absence gracefully.
with patch('seokar.utils.text_analysis.textstat', new=MagicMock(spec_set=True)) as mock_textstat:
    with patch('seokar.utils.text_analysis.word_tokenize', new=MagicMock()) as mock_word_tokenize:
        from seokar.utils.text_analysis import (
            calculate_word_count,
            calculate_readability_flesch,
            calculate_keyword_density,
        )


# --- calculate_word_count Tests ---

@pytest.mark.parametrize("text, expected_count", [
    ("Hello world", 2),
    ("This is a test sentence.", 5),
    ("One-two three four", 3), # "one-two" becomes "onetwo"
    ("   leading and trailing spaces   ", 4),
    ("Word with, punctuation!", 2), # "word" "punctuation"
    ("Word1 Word2 Word3", 3),
])
def test_calculate_word_count_basic(text, expected_count):
    """Test calculate_word_count with basic texts and punctuation."""
    assert calculate_word_count(text) == expected_count


@pytest.mark.parametrize("text, expected_count", [
    ("", 0),
    ("   ", 0),
    (None, 0), # Test with None input
    (123, 0), # Test with non-string input
])
def test_calculate_word_count_empty_or_invalid_input(text, expected_count):
    """Test calculate_word_count with empty, whitespace, or invalid inputs."""
    assert calculate_word_count(text) == expected_count


# --- calculate_readability_flesch Tests ---

def test_calculate_readability_flesch_success():
    """Test calculate_readability_flesch returns a score when textstat is available."""
    # Ensure textstat is "available" for this test context
    with patch('seokar.utils.text_analysis.textstat') as mock_textstat_lib:
        mock_textstat_lib.flesch_reading_ease.return_value = 65.5
        score = calculate_readability_flesch("This is a sample text.")
        assert score == 65.5
        mock_textstat_lib.flesch_reading_ease.assert_called_once_with("This is a sample text.")


def test_calculate_readability_flesch_textstat_not_available():
    """Test calculate_readability_flesch returns None when textstat is not imported."""
    # Simulate textstat being None in the module
    with patch('seokar.utils.text_analysis.textstat', new=None):
        score = calculate_readability_flesch("This is a sample text.")
        assert score is None


@pytest.mark.parametrize("text_input", [
    "",
    "   ",
    "Short.", # textstat.flesch_reading_ease can raise ValueError for very short texts
    "Hello."
])
def test_calculate_readability_flesch_empty_or_short_text(text_input):
    """Test calculate_readability_flesch returns None for empty/short texts (ValueError from textstat)."""
    with patch('seokar.utils.text_analysis.textstat') as mock_textstat_lib:
        mock_textstat_lib.flesch_reading_ease.side_effect = ValueError
        score = calculate_readability_flesch(text_input)
        assert score is None


def test_calculate_readability_flesch_other_exception():
    """Test calculate_readability_flesch returns None for other unexpected exceptions from textstat."""
    with patch('seokar.utils.text_analysis.textstat') as mock_textstat_lib:
        mock_textstat_lib.flesch_reading_ease.side_effect = Exception("Some other error")
        score = calculate_readability_flesch("Another sample text.")
        assert score is None


# --- calculate_keyword_density Tests ---

@pytest.fixture(autouse=True)
def mock_nltk_word_tokenize_global():
    """Mocks nltk.tokenize.word_tokenize globally for keyword density tests."""
    # Ensure it's available for the tests where it's expected to work
    with patch('seokar.utils.text_analysis.word_tokenize', return_value=['this', 'is', 'a', 'sample', 'text', 'with', 'sample', 'keyword']) as mock_tokenize:
        yield mock_tokenize


@pytest.mark.parametrize("text, keywords, expected_density", [
    ("This is a sample text. This text has a sample keyword.", ["sample", "text"], {"sample": 2/10, "text": 2/10}),
    ("SEO is important for website optimization. SEO helps websites.", ["seo", "website"], {"seo": 2/8, "website": 2/8}),
    ("single", ["single"], {"single": 1/1}),
])
def test_calculate_keyword_density_basic(text, keywords, expected_density):
    """Test calculate_keyword_density with basic cases."""
    # Custom mock for word_tokenize to match the input text for accurate tokenization
    with patch('seokar.utils.text_analysis.word_tokenize', side_effect=lambda x: re.sub(r'[^\w\s]', '', x).lower().split()) as mock_tokenize:
        result = calculate_keyword_density(text, keywords)
        assert result == pytest.approx(expected_density) # Use approx for float comparison


@pytest.mark.parametrize("text, keywords, expected_density", [
    ("Seo IS important for Website optimization.", ["seo", "website"], {"seo": 2/6, "website": 2/6}),
    ("PYTHON is a Great language.", ["python", "language"], {"python": 1/4, "language": 1/4}),
])
def test_calculate_keyword_density_case_insensitivity(text, keywords, expected_density):
    """Test calculate_keyword_density is case-insensitive."""
    with patch('seokar.utils.text_analysis.word_tokenize', side_effect=lambda x: re.sub(r'[^\w\s]', '', x).lower().split()):
        result = calculate_keyword_density(text, keywords)
        assert result == pytest.approx(expected_density)


def test_calculate_keyword_density_no_keywords():
    """Test calculate_keyword_density with an empty keyword list."""
    with patch('seokar.utils.text_analysis.word_tokenize', return_value=['hello', 'world']):
        result = calculate_keyword_density("Hello world", [])
        assert result == {}


def test_calculate_keyword_density_keywords_not_found():
    """Test calculate_keyword_density when keywords are not in text."""
    with patch('seokar.utils.text_analysis.word_tokenize', return_value=['apple', 'banana', 'orange']):
        result = calculate_keyword_density("I like fruits", ["grape", "kiwi"])
        assert result == {"grape": 0.0, "kiwi": 0.0}


@pytest.mark.parametrize("text_input", [
    "",
    "   ",
    None, # Test with None input
    123, # Test with non-string input
])
def test_calculate_keyword_density_empty_text(text_input):
    """Test calculate_keyword_density with empty or whitespace text."""
    result = calculate_keyword_density(text_input, ["keyword"])
    assert result == {"keyword": 0.0}

    # Test with empty text and empty keywords
    result_empty = calculate_keyword_density(text_input, [])
    assert result_empty == {}


def test_calculate_keyword_density_nltk_not_available():
    """Test calculate_keyword_density returns 0.0 for all keywords when NLTK is not imported."""
    # Simulate word_tokenize being None in the module
    with patch('seokar.utils.text_analysis.word_tokenize', new=None):
        result = calculate_keyword_density("This is a test.", ["test", "word"])
        assert result == {"test": 0.0, "word": 0.0}


@pytest.mark.parametrize("text, keywords, expected_density", [
    ("Search engine optimization (SEO) is important.", ["seo", "optimization"], {"seo": 1/5, "optimization": 1/5}),
    ("Python's power is great.", ["python", "power"], {"python": 1/4, "power": 1/4}),
])
def test_calculate_keyword_density_with_punctuation(text, keywords, expected_density):
    """Test calculate_keyword_density handles punctuation around keywords."""
    with patch('seokar.utils.text_analysis.word_tokenize', side_effect=lambda x: re.sub(r'[^\w\s]', '', x).lower().split()):
        result = calculate_keyword_density(text, keywords)
        assert result == pytest.approx(expected_density)
