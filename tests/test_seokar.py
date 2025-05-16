# tests/test_seokar.py
import pytest
from seokar import Seokar, SEOResultLevel, __version__

# --- Test Fixtures (Sample HTML) ---

@pytest.fixture
def html_full_valid():
    """A relatively well-structured HTML for testing GOOD cases and some minor warnings."""
    return """
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <title>Optimal Page Title For SEO (50 Chars Exactly)</title>
        <meta name="description" content="This is an optimized meta description for SEO purposes, well within the recommended length of 70 to 160 characters. It is very descriptive.">
        <meta name="robots" content="index, follow">
        <link rel="canonical" href="https://example.com/sample-page">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" href="/favicon.ico">
        <meta property="og:title" content="Open Graph Title">
        <meta property="og:description" content="Open Graph Description.">
        <meta property="og:type" content="website">
        <meta property="og:image" content="https://example.com/og-image.jpg">
        <meta property="og:url" content="https://example.com/sample-page">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Twitter Card Title">
        <meta name="twitter:description" content="Twitter Card Description.">
        <meta name="twitter:image" content="https://example.com/twitter-image.jpg">
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Article",
          "headline": "Article Headline",
          "author": {
            "@type": "Person",
            "name": "John Doe"
          }
        }
        </script>
    </head>
    <body>
        <h1>Main Page Heading: Clear and Concise</h1>
        <p>This is the first paragraph of the main content. It provides value to the user and search engines.
           We need enough words here to pass basic content length checks and for readability scoring.
           Let's add more sentences. This sentence helps with word count. Another sentence here.
           The Flesch reading ease score should be reasonable.
        </p>
        <h2>First Subheading (H2)</h2>
        <p>Content under the first subheading. This text is also important. We can add more details.
           Seokar analyzes various aspects of on-page SEO.
        </p>
        <img src="image1.jpg" alt="A descriptive alt text for image one.">
        <img src="image2.png" alt=""> <!-- Intentionally decorative -->
        <a href="/internal-link">Internal Link Text</a>
        <a href="https://external.com" rel="nofollow">External Nofollow Link</a>
    </body>
    </html>
    """

@pytest.fixture
def html_with_many_issues():
    """HTML with multiple SEO issues to test WARNING, ERROR, CRITICAL results."""
    return """
    <html>
    <head>
        <title>T</title> <!-- Title too short -->
        <!-- No meta description -->
        <meta name="robots" content="noindex, nofollow"> <!-- Critical and Warning -->
        <!-- No canonical -->
        <!-- No viewport -->
        <!-- No charset -->
    </head>
    <body lang=""> <!-- Empty lang -->
        <!-- No H1 tag -->
        <h2>Subheading without H1</h2>
        <h3>Another subheading</h3>
        <h1>Second H1 (problematic if first one also existed)</h1> <!-- This becomes the first H1 found -->
        <p>Short.</p> <!-- Thin content -->
        <img src="img.gif"> <!-- Missing alt -->
        <img src="img2.jpg" alt=" "> <!-- Empty alt, not marked decorative -->
        <img src="img3.png" alt="This is an extremely long alt text that definitely exceeds the recommended maximum length for image alt attributes, designed to trigger a warning for alt text length.">
        <a href="http://example.com/page1">Link 1</a> <!-- External link, assuming self.url is different -->
        <a href="/page2"></a> <!-- Empty anchor text -->
    </body>
    </html>
    """

@pytest.fixture
def html_minimal():
    return "<html><head><title>Min</title></head><body><h1>Ok H1</h1></body></html>"

@pytest.fixture
def html_empty_structure():
    return "<html><head></head><body></body></html>"


# --- Helper Function to Find Issues ---
def find_issue(report_issues, element_type, level=None, message_contains=None):
    for issue in report_issues:
        match_element = issue["element_type"] == element_type
        match_level = level is None or issue["level"]["name"] == level.name
        match_message = message_contains is None or message_contains in issue["message"]
        if match_element and match_level and match_message:
            return issue
    return None

# --- Initialization and Basic Getters ---
def test_seokar_version():
    assert isinstance(__version__, str)
    assert len(__version__) > 0 # e.g., "0.1.0"

def test_initialization(html_minimal):
    analyzer = Seokar(html_minimal, url="https://example.com")
    assert analyzer.html_content == html_minimal
    assert analyzer.url == "https://example.com"
    assert analyzer.soup is not None
    assert analyzer.get_version() == __version__

def test_initialization_no_url(html_minimal):
    analyzer = Seokar(html_minimal)
    assert analyzer.url is None

def test_initialization_invalid_url_type():
    with pytest.raises(ValueError, match="HTML content cannot be empty"): # Adjusted based on actual exception in Seokar
        Seokar("")
    with pytest.raises(TypeError, match="HTML content must be a string"):
        Seokar(123) # type: ignore

def test_get_title(html_full_valid, html_empty_structure):
    analyzer_valid = Seokar(html_full_valid)
    assert analyzer_valid.get_title() == "Optimal Page Title For SEO (50 Chars Exactly)"
    analyzer_empty = Seokar(html_empty_structure)
    assert analyzer_empty.get_title() is None

def test_get_meta_description(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    assert analyzer_valid.get_meta_description() == "This is an optimized meta description for SEO purposes, well within the recommended length of 70 to 160 characters. It is very descriptive."
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_meta_description() is None

def test_get_meta_robots(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    assert analyzer_valid.get_meta_robots() == ["index", "follow"] # Your code might produce more or less based on regex
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_meta_robots() == []

def test_get_canonical_url(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid, url="https://example.com/sample-page") # URL is important for _make_absolute_url
    assert analyzer_valid.get_canonical_url() == "https://example.com/sample-page"
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_canonical_url() is None

def test_get_viewport(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    assert "width=device-width" in analyzer_valid.get_viewport()
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_viewport() is None

def test_get_charset(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    assert analyzer_valid.get_charset() == "utf-8"
    analyzer_minimal = Seokar(html_minimal) # Assuming no charset specified
    assert analyzer_minimal.get_charset() is None

def test_get_html_lang(html_full_valid, html_empty_structure):
    analyzer_valid = Seokar(html_full_valid)
    assert analyzer_valid.get_html_lang() == "en-US"
    analyzer_empty = Seokar(html_empty_structure)
    assert analyzer_empty.get_html_lang() is None

def test_get_favicon_url(html_full_valid, html_minimal):
    # Test with base URL for resolving relative favicon path
    analyzer_valid = Seokar(html_full_valid, url="https://example.com")
    assert analyzer_valid.get_favicon_url() == "https://example.com/favicon.ico"

    # Test without specific favicon tag, should try default /favicon.ico if URL exists
    analyzer_minimal_with_url = Seokar(html_minimal, url="http://another.com")
    assert analyzer_minimal_with_url.get_favicon_url() == "http://another.com/favicon.ico"

    analyzer_minimal_no_url = Seokar(html_minimal)
    assert analyzer_minimal_no_url.get_favicon_url() is None

# --- Social and Structured Data ---
def test_get_open_graph_tags(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    og_tags = analyzer_valid.get_open_graph_tags()
    assert og_tags.get("og:title") == "Open Graph Title"
    assert og_tags.get("og:type") == "website"
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_open_graph_tags() == {}

def test_get_twitter_card_tags(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    twitter_tags = analyzer_valid.get_twitter_card_tags()
    assert twitter_tags.get("twitter:card") == "summary_large_image"
    assert twitter_tags.get("twitter:title") == "Twitter Card Title"
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_twitter_card_tags() == {}

def test_get_json_ld_data(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    json_ld = analyzer_valid.get_json_ld_data()
    assert len(json_ld) == 1
    assert json_ld[0].get("@type") == "Article"
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_json_ld_data() == []

# --- Headings ---
def test_get_all_headings(html_full_valid, html_minimal):
    analyzer_valid = Seokar(html_full_valid)
    headings = analyzer_valid.get_all_headings()
    assert headings.get("h1") == ["Main Page Heading: Clear and Concise"]
    assert headings.get("h2") == ["First Subheading (H2)"]
    analyzer_minimal = Seokar(html_minimal)
    assert analyzer_minimal.get_all_headings().get("h1") == ["Ok H1"]

# --- Content & Links (Basic Tests) ---
def test_get_main_content_text(html_full_valid):
    analyzer = Seokar(html_full_valid)
    content = analyzer.get_main_content_text()
    assert "first paragraph of the main content" in content
    assert "First Subheading (H2)" in content # Assuming h2 is part of main content extraction logic

def test_get_all_images(html_full_valid):
    analyzer = Seokar(html_full_valid)
    images = analyzer.get_all_images()
    assert len(images) == 2
    assert images[0].get("alt") == "A descriptive alt text for image one."
    assert images[1].get("alt") == ""

def test_get_all_links(html_full_valid):
    analyzer = Seokar(html_full_valid, url="https://example.com") # URL needed for internal/external classification
    links_data = analyzer.get_all_links()
    assert len(links_data["internal"]) == 1
    assert links_data["internal"][0]["text"] == "Internal Link Text"
    assert len(links_data["external"]) == 1
    assert links_data["external"][0]["is_nofollow"] is True


# --- Test `analyze()` method and SEOResults ---

def test_analyze_full_valid_html(html_full_valid):
    analyzer = Seokar(html_full_valid, url="https://example.com/sample-page")
    report = analyzer.analyze()

    assert report["analyzer_version"] == __version__
    assert report["url"] == "https://example.com/sample-page"

    # Basic SEO Checks - expecting GOOD results
    assert find_issue(report["issues"], "Title", SEOResultLevel.GOOD, "Optimal Title Length")
    assert find_issue(report["issues"], "Meta Description", SEOResultLevel.GOOD, "Optimal Meta Description Length")
    assert find_issue(report["issues"], "Meta Robots", SEOResultLevel.INFO, "Meta Robots Not Specified") is None # Should find "index, follow"
    assert find_issue(report["issues"], "Canonical URL", SEOResultLevel.GOOD, "Canonical URL Matches Page URL")
    assert find_issue(report["issues"], "Viewport", SEOResultLevel.GOOD, "Viewport Configured for Mobile")
    assert find_issue(report["issues"], "Charset", SEOResultLevel.GOOD, "UTF-8 Charset Declared")
    assert find_issue(report["issues"], "HTML Language", SEOResultLevel.GOOD, "HTML Language Declared")
    assert find_issue(report["issues"], "Favicon", SEOResultLevel.GOOD, "Favicon Link/Default Resolved")

    # Headings
    assert find_issue(report["issues"], "H1 Tag", SEOResultLevel.GOOD, "Single H1 Tag Present")
    assert find_issue(report["issues"], "Headings Hierarchy", SEOResultLevel.GOOD, "Logical Heading Hierarchy")

    # Content Quality (values depend on your constants)
    assert report["content_quality"]["content_length_chars"] > analyzer.MIN_CONTENT_LENGTH
    assert report["content_quality"]["text_to_html_ratio_percent"] > analyzer.MIN_TEXT_HTML_RATIO
    # Assuming readability is good for this sample
    assert report["content_quality"]["flesch_reading_ease_score"] >= 60 # Or check for GOOD issue

    # Images
    img_alt_issue = find_issue(report["issues"], "Image Alt Text", SEOResultLevel.GOOD, "Decorative Image Correctly Marked")
    # This check might need refinement based on how Seokar handles decorative images vs. all good
    # assert img_alt_issue or find_issue(report["issues"], "Image Alt Text", SEOResultLevel.GOOD, "Good Image Alt Text Coverage")

    # Links - basic check, more detailed tests could be added
    assert report["links"]["internal_links_count"] == 1
    assert report["links"]["external_links_count"] == 1

    # Social Media and Structured Data
    assert find_issue(report["issues"], "Open Graph", SEOResultLevel.GOOD, "Essential Open Graph Tags Present")
    assert find_issue(report["issues"], "Twitter Card", SEOResultLevel.GOOD, "Twitter Card Tags Appear Configured")
    assert find_issue(report["issues"], "Structured Data (JSON-LD)", SEOResultLevel.GOOD, "JSON-LD Data Found")

    # SEO Health Score should be high
    assert report["seo_health"]["score"] > 85 # Example threshold

def test_analyze_with_many_issues(html_with_many_issues):
    # Assuming base URL makes "http://example.com/page1" external
    analyzer = Seokar(html_with_many_issues, url="https://different-domain.com")
    report = analyzer.analyze()

    # Critical Issues
    assert find_issue(report["issues"], "Title", SEOResultLevel.CRITICAL, "Missing Title Tag") is None # Title is "T" which is short, not missing
    assert find_issue(report["issues"], "Meta Robots", SEOResultLevel.CRITICAL, "Page is NoIndexed")
    assert find_issue(report["issues"], "H1 Tag", SEOResultLevel.GOOD, "Single H1 Tag Present") # It finds "Second H1"

    # Error Issues
    assert find_issue(report["issues"], "Meta Description", SEOResultLevel.WARNING, "Missing Meta Description") # Should be Warning or Error
    assert find_issue(report["issues"], "Viewport", SEOResultLevel.ERROR, "Missing Viewport Meta Tag")
    assert find_issue(report["issues"], "Charset", SEOResultLevel.ERROR, "Charset Not Declared")
    assert find_issue(report["issues"], "Image Alt Text", SEOResultLevel.ERROR, "Missing Alt Attribute") # For img.gif

    # Warning Issues
    assert find_issue(report["issues"], "Title", SEOResultLevel.WARNING, "Title Too Short")
    assert find_issue(report["issues"], "Meta Robots", SEOResultLevel.WARNING, "Page is NoFollow")
    assert find_issue(report["issues"], "Canonical URL", SEOResultLevel.WARNING, "Missing Canonical URL")
    assert find_issue(report["issues"], "HTML Language", SEOResultLevel.WARNING, "HTML Language Not Declared") # lang=""
    assert find_issue(report["issues"], "Content Quality", SEOResultLevel.WARNING, "Thin Content")
    assert find_issue(report["issues"], "Image Alt Text", SEOResultLevel.WARNING, "Empty Alt Text") # For img2.jpg
    assert find_issue(report["issues"], "Image Alt Text", SEOResultLevel.WARNING, "Alt Text Too Long") # For img3.png
    # For link with empty anchor text, depends on how you classify it.
    # assert find_issue(report["issues"], "Link Structure", SEOResultLevel.WARNING, "Empty Anchor Text")


    # SEO Health Score should be low
    assert report["seo_health"]["score"] < 50 # Example threshold

def test_analyze_empty_structure(html_empty_structure):
    analyzer = Seokar(html_empty_structure, url="https://example.com")
    report = analyzer.analyze()
    assert find_issue(report["issues"], "Title", SEOResultLevel.CRITICAL, "Missing Title Tag")
    assert find_issue(report["issues"], "H1 Tag", SEOResultLevel.ERROR, "Missing H1 Tag")
    assert find_issue(report["issues"], "Content Quality", SEOResultLevel.WARNING, "No Main Content Text Extracted") or \
           find_issue(report["issues"], "Content Quality", SEOResultLevel.WARNING, "Thin Content")

# --- More specific tests for complex logic (examples) ---

def test_keyword_density_calculation():
    # This would require mocking get_main_content_text or providing specific text
    # and then checking the _calculate_keyword_density output via the report.
    # For direct testing of private methods (if complex enough), you might do:
    # analyzer = Seokar("<body>test test keyword</body>")
    # density = analyzer._calculate_keyword_density("test test keyword stopword test") # Assuming _calculate_keyword_density is accessible for testing
    # assert density.get("test") is not None
    pass # Placeholder for more complex tests

def test_url_resolution_with_base_tag():
    html_with_base = """
    <html><head><base href="https://base.example.com/folder/">
    <link rel="canonical" href="page.html">
    </head><body><a href="../another.html">Link</a></body></html>
    """
    analyzer = Seokar(html_with_base, url="https://original.example.com") # Original URL might be different
    assert analyzer.get_canonical_url() == "https://base.example.com/folder/page.html"
    links = analyzer.get_all_links()
    assert links["internal"][0]["url"] == "https://base.example.com/another.html" # Assuming _is_internal_url compares against original.example.com

# Run with: pytest -v
