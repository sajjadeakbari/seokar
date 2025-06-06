import pytest
from unittest.mock import patch, MagicMock
import tldextract # Assuming tldextract is installed for these tests

from seokar.utils.helpers import is_valid_url, clean_html_text, get_page_size_bytes, convert_bytes_to_kb, extract_domain


@pytest.mark.parametrize("url", [
    "http://example.com",
    "https://www.example.com/path/to/page?query=test#fragment",
    "http://192.168.1.1/index.html",
    "https://sub.domain.co.uk",
    "http://localhost:8080"
])
def test_is_valid_url_valid_cases(url):
    """Test is_valid_url with valid HTTP/HTTPS URLs."""
    assert is_valid_url(url) is True


@pytest.mark.parametrize("url", [
    "ftp://example.com",
    "www.example.com", # Missing scheme
    "example.com",     # Missing scheme
    "http://",         # Missing netloc
    "https://",        # Missing netloc
    "",                # Empty string
    "just_a_string",
    None,              # Test with None input
    123                # Test with non-string input
])
def test_is_valid_url_invalid_cases(url):
    """Test is_valid_url with invalid URLs or inputs."""
    assert is_valid_url(url) is False


@pytest.mark.parametrize("html_input, expected_output", [
    ("<p>Hello <b>World</b>!</p>", "Hello World!"),
    ("  <div>  Some   Text  </div>  ", "Some Text"),
    ("<h1>Title</h1>\n<p>Line 1</p>\n<p>Line 2</p>", "Title Line 1 Line 2"),
    ("", ""),
    (None, ""),
    (" ", ""),
    ("  \n  \t  ", ""),
    ("Text with & entities — and < >", "Text with & entities — and < >") # BeautifulSoup decodes entities
])
def test_clean_html_text_basic(html_input, expected_output):
    """Test clean_html_text with basic HTML and whitespace."""
    assert clean_html_text(html_input) == expected_output


def test_clean_html_text_with_scripts_styles():
    """Test clean_html_text removes script and style tags."""
    html_content = """
    <html>
    <head>
        <style>body { color: red; }</style>
    </head>
    <body>
        <p>Main content.</p>
        <script>alert('hello');</script>
        <div>More text.</div>
        <script type="text/javascript">console.log('foo');</script>
    </body>
    </html>
    """
    expected_output = "Main content. More text."
    assert clean_html_text(html_content) == expected_output


@pytest.mark.parametrize("content_bytes, expected_size", [
    (b"hello", 5),
    (b"", 0),
    (b"\x00\x01\x02", 3),
    ("string".encode('utf-8'), 6)
])
def test_get_page_size_bytes(content_bytes, expected_size):
    """Test get_page_size_bytes returns correct size for bytes."""
    assert get_page_size_bytes(content_bytes) == expected_size


@pytest.mark.parametrize("bytes_size, expected_kb", [
    (0, 0.0),
    (1024, 1.0),
    (2048, 2.0),
    (500, 0.49),
    (1023, 1.00), # Rounds up
    (1025, 1.00), # Rounds down
    (300 * 1024, 300.0)
])
def test_convert_bytes_to_kb(bytes_size, expected_kb):
    """Test convert_bytes_to_kb converts and rounds correctly."""
    assert convert_bytes_to_kb(bytes_size) == expected_kb


@pytest.mark.parametrize("url, expected_domain", [
    ("https://www.example.com/path", "example.com"),
    ("http://blog.example.co.uk", "example.co.uk"),
    ("https://sub.domain.com", "domain.com"),
    ("http://www.google.com", "google.com"),
    ("https://mail.google.com/mail/", "google.com"),
    ("https://example.info", "example.info"),
    ("ftp://ftp.example.org/dir", "example.org"), # tldextract works for non-http schemes, but per spec, domain extraction applies to web
])
def test_extract_domain_standard_urls(url, expected_domain):
    """Test extract_domain with standard URLs."""
    assert extract_domain(url) == expected_domain


@pytest.mark.parametrize("url, expected_domain", [
    ("http://192.168.1.1/", "192.168.1.1"),
    ("https://10.0.0.5:8080/app", "10.0.0.5")
])
def test_extract_domain_ip_addresses(url, expected_domain):
    """Test extract_domain with IP addresses."""
    assert extract_domain(url) == expected_domain


@pytest.mark.parametrize("url, expected_domain", [
    ("http://localhost:8000/", "localhost"),
    ("https://localhost/", "localhost")
])
def test_extract_domain_localhost(url, expected_domain):
    """Test extract_domain with localhost."""
    assert extract_domain(url) == expected_domain


@pytest.mark.parametrize("url", [
    "",
    "just_a_string",
    "http://",
    "invalid-url",
    None # Test with None input
])
def test_extract_domain_invalid_urls(url):
    """Test extract_domain with invalid or empty URLs."""
    assert extract_domain(url) is None

# Test tldextract fallback if it were to fail (though current implementation assumes success)
@patch('seokar.utils.helpers.tldextract.extract')
def test_extract_domain_tldextract_exception_fallback(mock_tldextract_extract):
    mock_tldextract_extract.side_effect = Exception("Simulated tldextract failure")
    
    # Test with a URL that should trigger the fallback
    url = "https://www.example.com/path"
    domain = extract_domain(url)
    assert domain == "www.example.com" # Fallback should return netloc

    url_no_netloc = "invalid-url-string"
    domain_no_netloc = extract_domain(url_no_netloc)
    assert domain_no_netloc is None # Fallback should return None for no netloc
