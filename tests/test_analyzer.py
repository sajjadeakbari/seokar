# tests/test_analyzer.py
import pytest
from seokar import Seokar # یا from seokar.analyzer import Seokar اگر __init__.py را طور دیگری نوشتید

# --- Test Fixtures (Sample HTML) ---
@pytest.fixture
def sample_html_full():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Test Page Title & More</title>
        <meta name="description" content="This is a test meta description. It's awesome.">
        <meta name="robots" content="index, follow, noarchive">
        <link rel="canonical" href="https://example.com/test-page">
        <meta property="og:title" content="OG Test Title">
        <meta property="og:description" content="OG Test Description.">
        <meta property="og:type" content="website">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Twitter Test Title">
    </head>
    <body>
        <h1>Main Heading 1</h1>
        <h1>Another H1</h1>
        <h2>Sub Heading 2.1</h2>
        <p>Some content.</p>
        <h3>Sub-sub Heading 3.1</h3>
        <h4></h4> <!-- Empty H4 -->
        <h5>H5 with <span>nested</span> text</h5>
    </body>
    </html>
    """

@pytest.fixture
def sample_html_minimal():
    return """
    <html><head><title>Minimal</title></head><body><h1>Minimal H1</h1></body></html>
    """

@pytest.fixture
def sample_html_empty():
    return """
    <html><head></head><body></body></html>
    """

# --- Test Cases ---

def test_initialization(sample_html_full):
    analyzer = Seokar(sample_html_full, url="https://example.com")
    assert analyzer.html_content == sample_html_full
    assert analyzer.url == "https://example.com"
    assert analyzer.soup is not None

def test_initialization_type_error():
    with pytest.raises(TypeError, match="html_content must be a string"):
        Seokar(123) # type: ignore

# --- Title ---
def test_get_title_present(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_title() == "Test Page Title & More" # BeautifulSoup decodes entities

def test_get_title_missing(sample_html_empty):
    analyzer = Seokar(sample_html_empty)
    assert analyzer.get_title() is None

def test_get_title_length(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_title_length() == 22 # "Test Page Title & More"

def test_get_title_length_missing(sample_html_empty):
    analyzer = Seokar(sample_html_empty)
    assert analyzer.get_title_length() == 0

# --- Meta Description ---
def test_get_meta_description_present(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_meta_description() == "This is a test meta description. It's awesome."

def test_get_meta_description_missing(sample_html_minimal):
    analyzer = Seokar(sample_html_minimal)
    assert analyzer.get_meta_description() is None

def test_get_meta_description_length(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_meta_description_length() == 46

# --- Meta Robots ---
def test_get_meta_robots_present(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_meta_robots() == ["index", "follow", "noarchive"]

def test_get_meta_robots_missing(sample_html_minimal):
    analyzer = Seokar(sample_html_minimal)
    assert analyzer.get_meta_robots() == []

def test_get_meta_robots_empty_content():
    html = '<meta name="robots" content="">'
    analyzer = Seokar(html)
    assert analyzer.get_meta_robots() == []

# --- Canonical URL ---
def test_get_canonical_url_present(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_canonical_url() == "https://example.com/test-page"

def test_get_canonical_url_missing(sample_html_minimal):
    analyzer = Seokar(sample_html_minimal)
    assert analyzer.get_canonical_url() is None

# --- Open Graph ---
def test_get_open_graph_tags_present(sample_html_full):
    analyzer = Seokar(sample_html_full)
    expected_og = {
        "og:title": "OG Test Title",
        "og:description": "OG Test Description.",
        "og:type": "website"
    }
    assert analyzer.get_open_graph_tags() == expected_og

def test_get_open_graph_tags_missing(sample_html_minimal):
    analyzer = Seokar(sample_html_minimal)
    assert analyzer.get_open_graph_tags() == {}
    
def test_get_open_graph_tags_no_content():
    html = '<meta property="og:title" content=""> <meta property="og:description">'
    analyzer = Seokar(html)
    assert analyzer.get_open_graph_tags() == {}


# --- Twitter Cards ---
def test_get_twitter_card_tags_present(sample_html_full):
    analyzer = Seokar(sample_html_full)
    expected_twitter = {
        "twitter:card": "summary_large_image",
        "twitter:title": "Twitter Test Title"
    }
    assert analyzer.get_twitter_card_tags() == expected_twitter

def test_get_twitter_card_tags_missing(sample_html_minimal):
    analyzer = Seokar(sample_html_minimal)
    assert analyzer.get_twitter_card_tags() == {}

# --- Headings ---
def test_get_h1_tags(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_h1_tags() == ["Main Heading 1", "Another H1"]

def test_get_h1_tags_missing(sample_html_empty):
    analyzer = Seokar(sample_html_empty)
    assert analyzer.get_h1_tags() == []

def test_get_h2_tags(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_h2_tags() == ["Sub Heading 2.1"]
    
def test_get_h5_tags_with_nested_span(sample_html_full):
    analyzer = Seokar(sample_html_full)
    assert analyzer.get_h5_tags() == ["H5 with nested text"]


def test_get_all_heading_tags(sample_html_full):
    analyzer = Seokar(sample_html_full)
    expected_headings = {
        "h1": ["Main Heading 1", "Another H1"],
        "h2": ["Sub Heading 2.1"],
        "h3": ["Sub-sub Heading 3.1"],
        "h5": ["H5 with nested text"] # H4 is empty, so not included
    }
    assert analyzer.get_all_heading_tags() == expected_headings

def test_get_all_heading_tags_minimal(sample_html_minimal):
    analyzer = Seokar(sample_html_minimal)
    expected_headings = {
        "h1": ["Minimal H1"]
    }
    assert analyzer.get_all_heading_tags() == expected_headings

def test_get_all_heading_tags_empty(sample_html_empty):
    analyzer = Seokar(sample_html_empty)
    assert analyzer.get_all_heading_tags() == {}

# --- Get All SEO Data ---
def test_get_all_seo_data(sample_html_full):
    analyzer = Seokar(sample_html_full)
    data = analyzer.get_all_seo_data()
    assert data["title"] == "Test Page Title & More"
    assert data["meta_description"] == "This is a test meta description. It's awesome."
    assert "og:title" in data["open_graph_tags"]
    assert "h1" in data["headings"]
    assert len(data["headings"]["h1"]) == 2
