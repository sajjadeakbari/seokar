import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
import re

from seokar.analyzer import SeokarAnalyzer
from seokar.models import SEOResult, CoreWebVitalsMetrics, ContentMetrics
from seokar.exceptions import SeokarError, SeokarHTTPError
from seokar.utils.network import SimpleCache
from seokar.constants.core import StatusCode, SeoLimits, RobotsTxt
from seokar.constants.technical import PageSpeed, TechnicalIssues
from seokar.constants.security import SecurityHeaders, RecommendedSecurityValues
from seokar.constants.content import ContentQuality
from seokar.constants.schema import SchemaTypes, SchemaProperties, SchemaUrls


@pytest.fixture
def html_content_basic():
    """Basic HTML content for testing, adheres to good SEO practices."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Basic Test Page Title</title>
        <meta name="description" content="This is a basic meta description for the test page.">
    </head>
    <body>
        <h1>Main Heading of the Page</h1>
        <p>This is a paragraph of content.</p>
    </body>
    </html>
    """


@pytest.fixture
def html_content_complex():
    """Complex HTML content to test various SEO issues and features."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Complex Page Title for SEO Analysis Example</title>
        <meta name="description" content="This is a meta description for a complex page, designed to test various SEO analysis features.">
        <link rel="canonical" href="https://www.example.com/complex-page-canonical/">
        <meta name="robots" content="noindex, nofollow">
        <script type="application/ld+json">
        {{
          "@context": "{SchemaUrls.JSON_LD_CONTEXT}",
          "@type": "{SchemaTypes.PRODUCT}",
          "name": "Example Product",
          "description": "A very good example product.",
          "image": "https://www.example.com/images/product.jpg",
          "offers": {{
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": "19.99"
          }}
        }}
        </script>
        <link rel="stylesheet" href="http://cdn.example.com/style.css"> <!-- Mixed content -->
        <img src="http://cdn.example.com/image.png" alt="An image"> <!-- Mixed content -->
        <script src="http://cdn.example.com/script.js"></script> <!-- Mixed content -->
    </head>
    <body>
        <h1>Main Heading One</h1>
        <h1>Another H1 Tag - Should trigger warning</h1>
        <p>This is the first paragraph of content. It has many words. Word count is important for content quality metrics. We want to ensure that our analysis tools can accurately calculate the number of words. Readability is also a key factor in SEO, influencing user engagement and search engine rankings. Keyword density needs to be monitored to avoid keyword stuffing, but also to ensure relevant terms are present. This paragraph specifically contains the words "seo", "analysis", "website", and "optimization" multiple times to test keyword density calculation.</p>
        <p>This is the second paragraph. It continues the discussion on seo and website optimization. The goal is to provide comprehensive analysis. We are testing how well the system identifies and quantifies content quality. Analysis is a core function. Website optimization is crucial.</p>
        <p>And a third paragraph, just to add more word count. This content is for testing. The analysis focuses on various aspects of website seo. Optimization is the key. Analysis provides insights. Website is the target. Seo is the goal.</p>
        <a href="/internal-link">Internal Link</a>
        <a href="http://external.com/broken">Broken External Link</a>
        <img src="/image-no-alt.jpg"> <!-- No alt text -->
        <div style="background-image: url('http://example.com/bg.png');">Inline mixed content</div>
    </body>
    </html>
    """


@pytest.fixture
def mock_cache():
    """A mock instance of SimpleCache."""
    return SimpleCache()


@pytest.fixture
def mock_fetch_and_get_status():
    """Mocks fetch_page_content to return a successful response."""
    with patch('seokar.utils.network.fetch_page_content') as mock_fetch:
        mock_fetch.return_value = (
            b'<html><head><title>Test</title></head><body>Hello</body></html>',
            StatusCode.OK,
            {"Content-Type": "text/html", "Strict-Transport-Security": "max-age=31536000"}
        )
        yield mock_fetch


@pytest.fixture
def mock_fetch_and_get_status_complex(html_content_complex):
    """Mocks fetch_page_content for complex HTML with specific headers."""
    with patch('seokar.utils.network.fetch_page_content') as mock_fetch:
        # Mock headers for security checks
        headers = {
            "Content-Type": "text/html",
            SecurityHeaders.STRICT_TRANSPORT_SECURITY: f"max-age={RecommendedSecurityValues.HSTS_MIN_AGE}; includeSubDomains",
            SecurityHeaders.X_FRAME_OPTIONS: RecommendedSecurityValues.X_FRAME_OPTIONS_VALUE,
            SecurityHeaders.X_CONTENT_TYPE_OPTIONS: RecommendedSecurityValues.X_CONTENT_TYPE_OPTIONS_VALUE,
            SecurityHeaders.REFERRER_POLICY: RecommendedSecurityValues.REFERRER_POLICY_VALUE,
            SecurityHeaders.PERMISSIONS_POLICY: "geolocation=(), microphone=()",
            SecurityHeaders.CONTENT_SECURITY_POLICY: "; ".join(RecommendedSecurityValues.CSP_RECOMMENDED_DIRECTIVES)
        }
        mock_fetch.return_value = (html_content_complex.encode('utf-8'), StatusCode.OK, headers)
        yield mock_fetch


@pytest.fixture
def mock_fetch_and_get_status_failure():
    """Mocks fetch_page_content to return None and get_url_status to return an error code."""
    with patch('seokar.utils.network.fetch_page_content', return_value=None) as mock_fetch:
        with patch('seokar.utils.network.get_url_status', return_value=StatusCode.INTERNAL_SERVER_ERROR) as mock_get_status:
            yield mock_fetch, mock_get_status


@pytest.fixture
def mock_text_analysis_functions():
    """Mocks text analysis functions to return predefined values."""
    with patch('seokar.utils.text_analysis.calculate_word_count', return_value=500) as mock_wc, \
         patch('seokar.utils.text_analysis.calculate_readability_flesch', return_value=65.5) as mock_read, \
         patch('seokar.utils.text_analysis.calculate_keyword_density', return_value={"seo": 0.01, "analysis": 0.008}) as mock_kd:
        yield mock_wc, mock_read, mock_kd


def test_analyzer_init_with_url():
    """Test SeokarAnalyzer initialization with a URL."""
    analyzer = SeokarAnalyzer(url="https://example.com")
    assert analyzer._url == "https://example.com"
    assert analyzer._html_content_str is None
    assert isinstance(analyzer._cache, SimpleCache)


def test_analyzer_init_with_html_content(html_content_basic):
    """Test SeokarAnalyzer initialization with direct HTML content."""
    analyzer = SeokarAnalyzer(html_content=html_content_basic)
    assert analyzer._url is None
    assert analyzer._html_content_str == html_content_basic.strip()
    assert analyzer._status_code == StatusCode.OK
    assert analyzer._loading_time_ms == 0.0
    assert analyzer._page_size_bytes == len(html_content_basic.encode('utf-8', errors='ignore'))
    assert analyzer._soup is not None


def test_analyzer_init_raises_error_no_input():
    """Test SeokarAnalyzer raises ValueError when no URL or HTML is provided."""
    with pytest.raises(ValueError, match="Either 'url' or 'html_content' must be provided."):
        SeokarAnalyzer()


def test_analyzer_init_raises_error_both_inputs():
    """Test SeokarAnalyzer raises ValueError when both URL and HTML are provided."""
    with pytest.raises(ValueError, match="Cannot provide both 'url' and 'html_content'. Choose one."):
        SeokarAnalyzer(url="https://example.com", html_content="<html></html>")


@patch('seokar.utils.helpers.is_valid_url', return_value=True)
def test_analyze_basic_page_success(mock_is_valid_url, html_content_basic, mock_fetch_and_get_status):
    """
    Test basic page analysis and ensure core SEOResult fields are populated correctly.
    """
    mock_fetch_and_get_status.return_value = (html_content_basic.encode('utf-8'), StatusCode.OK, {"Content-Type": "text/html"})
    
    analyzer = SeokarAnalyzer(url="https://example.com/basic-page")
    result = analyzer.analyze()

    assert isinstance(result, SEOResult)
    assert result.url == "https://example.com/basic-page"
    assert result.status_code == StatusCode.OK
    assert result.title == "Basic Test Page Title"
    assert result.meta_description == "This is a basic meta description for the test page."
    assert result.h1_tags == ["Main Heading of the Page"]
    assert result.page_size_bytes == len(html_content_basic.encode('utf-8', errors='ignore'))
    assert result.loading_time_ms is not None and result.loading_time_ms >= 0

    # Ensure other fields are default/empty/None for basic analysis
    assert result.canonical_url is None
    assert result.robots_tag is None
    assert result.technical_issues == []
    assert result.security_headers == {}
    assert result.schema_present is False
    assert result.core_web_vitals is not None
    assert result.core_web_vitals.lcp is None
    assert result.content_metrics is None


@patch('seokar.utils.helpers.is_valid_url', return_value=True)
def test_analyze_complex_page_technical_issues(mock_is_valid_url, html_content_complex, mock_fetch_and_get_status_complex):
    """
    Test analysis of a complex page to identify technical SEO issues and security headers.
    """
    url = "https://www.example.com/complex-page/"
    analyzer = SeokarAnalyzer(url=url)
    result = analyzer.analyze()

    assert isinstance(result, SEOResult)
    assert result.url == url
    assert result.status_code == StatusCode.OK
    assert result.title == "Complex Page Title for SEO Analysis Example"
    assert result.meta_description == "This is a meta description for a complex page, designed to test various SEO analysis features."
    assert result.h1_tags == ["Main Heading One", "Another H1 Tag - Should trigger warning"]
    assert result.canonical_url == "https://www.example.com/complex-page-canonical/"
    assert result.robots_tag == "noindex, nofollow"

    # Verify technical issues
    expected_technical_issues = [
        TechnicalIssues.MULTIPLE_H1,
        f"Robots Tag contains '{RobotsTxt.NOINDEX}' directive.",
        f"Robots Tag contains '{RobotsTxt.NOFOLLOW}' directive.",
        TechnicalIssues.MIXED_CONTENT # From stylesheet, image, script, inline style
    ]
    for issue in expected_technical_issues:
        assert issue in result.technical_issues

    # Verify security headers
    expected_security_headers = {
        SecurityHeaders.STRICT_TRANSPORT_SECURITY: f"max-age={RecommendedSecurityValues.HSTS_MIN_AGE}; includeSubDomains",
        SecurityHeaders.X_FRAME_OPTIONS: RecommendedSecurityValues.X_FRAME_OPTIONS_VALUE,
        SecurityHeaders.X_CONTENT_TYPE_OPTIONS: RecommendedSecurityValues.X_CONTENT_TYPE_OPTIONS_VALUE,
        SecurityHeaders.REFERRER_POLICY: RecommendedSecurityValues.REFERRER_POLICY_VALUE,
        SecurityHeaders.PERMISSIONS_POLICY: "geolocation=(), microphone=()",
        SecurityHeaders.CONTENT_SECURITY_POLICY: "; ".join(RecommendedSecurityValues.CSP_RECOMMENDED_DIRECTIVES)
    }
    assert result.security_headers == expected_security_headers


@patch('seokar.utils.helpers.is_valid_url', return_value=True)
def test_analyze_content_metrics(mock_is_valid_url, html_content_complex, mock_fetch_and_get_status_complex, mock_text_analysis_functions):
    """
    Test content analysis metrics are correctly calculated and populated.
    """
    analyzer = SeokarAnalyzer(url="https://www.example.com/complex-page/")
    result = analyzer.analyze()

    mock_wc, mock_read, mock_kd = mock_text_analysis_functions

    # Assert that the text analysis functions were called
    mock_wc.assert_called_once()
    mock_read.assert_called_once()
    mock_kd.assert_called_once()

    assert result.content_metrics is not None
    assert isinstance(result.content_metrics, ContentMetrics)
    assert result.content_metrics.word_count == 500
    assert result.content_metrics.readability_score == 65.5
    assert result.content_metrics.keyword_density == {"seo": 0.01, "analysis": 0.008}


@patch('seokar.utils.helpers.is_valid_url', return_value=True)
def test_analyze_schema_markup(mock_is_valid_url, html_content_complex, mock_fetch_and_get_status_complex):
    """
    Test that schema markup is correctly detected.
    """
    analyzer = SeokarAnalyzer(url="https://www.example.com/complex-page/")
    result = analyzer.analyze()

    assert result.schema_present is True


@patch('seokar.utils.helpers.is_valid_url', return_value=True)
def test_analyzer_network_failure(mock_is_valid_url, mock_fetch_and_get_status_failure):
    """
    Test that SeokarAnalyzer raises SeokarHTTPError on network failure.
    """
    # mock_fetch_and_get_status_failure provides (mock_fetch, mock_get_status)
    mock_fetch, mock_get_status = mock_fetch_and_get_status_failure

    analyzer = SeokarAnalyzer(url="https://nonexistent.com")
    
    with pytest.raises(SeokarHTTPError) as excinfo:
        analyzer.analyze()
    
    assert "Failed to fetch content" in str(excinfo.value)
    assert excinfo.value.status_code == StatusCode.INTERNAL_SERVER_ERROR
    
    mock_fetch.assert_called_once_with("https://nonexistent.com", timeout=10, retries=3)
    mock_get_status.assert_called_once_with("https://nonexistent.com", timeout=5, retries=2)


def test_analyzer_invalid_url():
    """Test that SeokarAnalyzer raises SeokarError for an invalid URL."""
    analyzer = SeokarAnalyzer(url="invalid-url-string")
    with pytest.raises(SeokarError, match="Invalid URL provided: invalid-url-string"):
        analyzer.analyze()


@patch('seokar.utils.helpers.is_valid_url', return_value=True)
def test_analyzer_uses_cache(mock_is_valid_url, mock_fetch_and_get_status, mock_cache):
    """
    Test that SeokarAnalyzer utilizes the SimpleCache.
    """
    test_url = "https://example.com/cached-page"
    cached_content = b'<html>Cached Content</html>'
    cached_status = StatusCode.OK
    cached_headers = {"Cache-Control": "max-age=3600"}

    # Mock cache.get to return data on first call
    mock_cache.get = MagicMock(return_value=(cached_content, cached_status, cached_headers))
    # Mock cache.set to verify it's called on a cache miss (which won't happen here)
    mock_cache.set = MagicMock()

    analyzer = SeokarAnalyzer(url=test_url, cache=mock_cache)
    
    # First call - should hit cache
    result_from_cache = analyzer.analyze()
    mock_cache.get.assert_called_once_with(test_url)
    mock_fetch_and_get_status.assert_not_called() # fetch_page_content should NOT be called

    assert result_from_cache.url == test_url
    assert result_from_cache.status_code == cached_status
    assert result_from_cache.page_size_bytes == len(cached_content)
    assert result_from_cache.loading_time_ms == 0.0 # Should be 0 when from cache
    assert analyzer._response_headers == cached_headers # Ensure headers are loaded from cache

    # Reset mocks for second call test (simulate a cache miss)
    mock_cache.get.reset_mock()
    mock_fetch_and_get_status.reset_mock()
    mock_cache.set.reset_mock()
    
    # Mock cache.get to return None for cache miss
    mock_cache.get.return_value = None
    # Mock fetch_page_content to provide new data
    mock_fetch_and_get_status.return_value = (
        b'<html>New Content</html>',
        StatusCode.OK,
        {"New-Header": "value"}
    )
    
    # Second call - should miss cache and fetch
    analyzer_new_instance = SeokarAnalyzer(url=test_url, cache=mock_cache) # New instance to ensure fresh state if needed
    result_from_fetch = analyzer_new_instance.analyze()

    mock_cache.get.assert_called_once_with(test_url)
    mock_fetch_and_get_status.assert_called_once_with(test_url, timeout=10, retries=3) # fetch_page_content SHOULD be called
    mock_cache.set.assert_called_once_with(test_url, (b'<html>New Content</html>', StatusCode.OK, {"New-Header": "value"}))

    assert result_from_fetch.url == test_url
    assert result_from_fetch.status_code == StatusCode.OK
    assert result_from_fetch.page_size_bytes == len(b'<html>New Content</html>')
    assert result_from_fetch.loading_time_ms > 0.0 # Should be > 0 when fetched
    assert analyzer_new_instance._response_headers == {"New-Header": "value"}
