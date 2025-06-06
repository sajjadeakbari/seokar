import time
import re
from typing import Optional, List, Dict, Any, Tuple

from bs4 import BeautifulSoup

from ..models import SEOResult, CoreWebVitalsMetrics, ContentMetrics
from ..exceptions import SeokarError, SeokarHTTPError
from ..utils.network import fetch_page_content, get_url_status, SimpleCache
from ..utils.helpers import get_page_size_bytes, is_valid_url
from ..constants.core import StatusCode, SeoLimits
from ..constants.technical import CoreWebVitals, PageSpeed, TechnicalIssues
from ..constants.security import SecurityHeaders, RecommendedSecurityValues


class SeokarAnalyzer:
    """
    The core analysis engine for the Seokar library.
    Responsible for fetching content, parsing HTML, and extracting various SEO elements.
    """
    def __init__(self, url: Optional[str] = None, html_content: Optional[str] = None, cache: Optional[SimpleCache] = None):
        if url is None and html_content is None:
            raise ValueError("Either 'url' or 'html_content' must be provided.")
        if url is not None and html_content is not None:
            raise ValueError("Cannot provide both 'url' and 'html_content'. Choose one.")

        self._url = url
        self._html_content_bytes: Optional[bytes] = None
        self._html_content_str: Optional[str] = None
        self._status_code: Optional[int] = None
        self._loading_time_ms: Optional[float] = None
        self._page_size_bytes: Optional[int] = None
        self._soup: Optional[BeautifulSoup] = None
        self._response_headers: Dict[str, str] = {}  # Added for security header analysis
        self._cache = cache if cache is not None else SimpleCache()

        # If HTML content is provided directly, initialize properties and BeautifulSoup immediately
        if html_content:
            self._html_content_str = html_content
            self._html_content_bytes = html_content.encode('utf-8', errors='ignore')
            self._status_code = StatusCode.OK  # Assume success if content is directly provided
            self._loading_time_ms = 0.0  # No network load time
            self._page_size_bytes = get_page_size_bytes(self._html_content_bytes)
            self._soup = BeautifulSoup(self._html_content_str, "html.parser")
            self._response_headers = {} # No headers for direct content, initialize empty


    def _fetch_and_parse_page(self) -> None:
        """
        Responsible for fetching page content, status code, and headers,
        and initializing BeautifulSoup. Handles caching for network requests.
        """
        if not self._url or not is_valid_url(self._url):
            raise SeokarError(f"Invalid URL provided: {self._url}")

        cached_data = self._cache.get(self._url)
        
        if cached_data:
            # If data is in cache, use it
            self._html_content_bytes, self._status_code, self._response_headers = cached_data
            self._loading_time_ms = 0.0  # Indicate it was served from cache
            self._page_size_bytes = get_page_size_bytes(self._html_content_bytes)
        else:
            # Otherwise, fetch from network
            start_time = time.perf_counter()
            fetched_result: Optional[Tuple[bytes, int, Dict[str, str]]] = fetch_page_content(self._url)
            end_time = time.perf_counter()
            
            self._loading_time_ms = (end_time - start_time) * 1000

            if fetched_result is None:
                # fetch_page_content already handles 4xx/5xx as failure for content retrieval
                # We need to get the status code specifically if content fetching failed
                # However, for this design, we treat no content as a failure, so status code becomes irrelevant
                # in this specific branch. If we wanted to distinguish, fetch_page_content would need to return
                # status code even on non-2xx.
                raise SeokarHTTPError(f"Failed to fetch content or encountered HTTP error for {self._url}.", status_code=None)

            self._html_content_bytes, self._status_code, self._response_headers = fetched_result
            self._page_size_bytes = get_page_size_bytes(self._html_content_bytes)
            
            # Cache the fetched content bytes, status code, and headers
            self._cache.set(self._url, (self._html_content_bytes, self._status_code, self._response_headers))

        # Decode bytes to string for BeautifulSoup parsing
        self._html_content_str = self._html_content_bytes.decode('utf-8', errors='ignore')
        
        # Initialize BeautifulSoup with the full (decoded) HTML content
        self._soup = BeautifulSoup(self._html_content_str, "html.parser")

    def _get_title(self) -> Optional[str]:
        """Extracts the page title from the HTML content."""
        if not self._soup:
            return None
        title_tag = self._soup.find('title')
        return title_tag.string.strip() if title_tag and title_tag.string else None

    def _get_meta_description(self) -> Optional[str]:
        """Extracts the meta description from the HTML content."""
        if not self._soup:
            return None
        meta_description_tag = self._soup.find('meta', attrs={'name': 'description'})
        if not meta_description_tag:
            meta_description_tag = self._soup.find('meta', attrs={'property': 'og:description'})
        
        return meta_description_tag.get('content').strip() if meta_description_tag and meta_description_tag.get('content') else None

    def _get_h1_tags(self) -> List[str]:
        """Extracts all <h1> tag contents from the HTML content."""
        if not self._soup:
            return []
        h1_tags = self._soup.find_all('h1')
        return [h1.get_text(strip=True) for h1 in h1_tags if h1.get_text(strip=True)]

    def _get_canonical_url(self) -> Optional[str]:
        """Extracts the canonical URL from the HTML content."""
        if not self._soup:
            return None
        canonical_link_tag = self._soup.find('link', rel='canonical')
        return canonical_link_tag.get('href').strip() if canonical_link_tag and canonical_link_tag.get('href') else None

    def _get_robots_tag(self) -> Optional[str]:
        """Extracts the content of the robots meta tag."""
        if not self._soup:
            return None
        robots_meta_tag = self._soup.find('meta', attrs={'name': 'robots'})
        return robots_meta_tag.get('content').strip() if robots_meta_tag and robots_meta_tag.get('content') else None

    def _analyze_technical_issues(self) -> List[str]:
        """
        Analyzes technical SEO issues based on page content and retrieved data.
        """
        issues: List[str] = []

        # Ensure necessary data is available
        if not self._soup or self._status_code is None:
            issues.append("Insufficient data for full technical analysis.")
            return issues

        # Title Check
        if not self._get_title():
            issues.append(TechnicalIssues.MISSING_TITLE)

        # Meta Description Check
        if not self._get_meta_description():
            issues.append(TechnicalIssues.MISSING_META_DESCRIPTION)

        # Multiple H1 Check
        if len(self._get_h1_tags()) > SeoLimits.H1_MAX_COUNT:
            issues.append(TechnicalIssues.MULTIPLE_H1)

        # Canonical URL Check
        if not self._get_canonical_url():
            issues.append(TechnicalIssues.NO_CANONICAL)

        # Robots Tag Check
        robots_tag_content = self._get_robots_tag()
        if robots_tag_content:
            robots_tag_lower = robots_tag_content.lower()
            if "noindex" in robots_tag_lower:
                issues.append(f"Robots Tag contains '{RobotsTxt.NOINDEX}' directive.")
            if "nofollow" in robots_tag_lower:
                issues.append(f"Robots Tag contains '{RobotsTxt.NOFOLLOW}' directive.")

        # HTTP Status Code Check
        if self._status_code is not None:
            if self._status_code >= StatusCode.BAD_REQUEST and self._status_code < StatusCode.INTERNAL_SERVER_ERROR: # 4xx
                if self._status_code != StatusCode.NOT_FOUND:
                    issues.append(f"Client Error ({self._status_code}) detected.")
            elif self._status_code >= StatusCode.INTERNAL_SERVER_ERROR and self._status_code < 600: # 5xx
                issues.append(f"Server Error ({self._status_code}) detected.")
            # Note: 404 is generally not flagged as an "error" in this context but rather "not found"
            # The prompt says "apart from 404", so we specifically exclude it from generic 4xx errors.

        # Page Size Check
        if self._page_size_bytes is not None and self._page_size_bytes > PageSpeed.MAX_PAGE_SIZE_BYTES:
            issues.append("Page Size Too Large.")

        # Loading Time Check
        if self._loading_time_ms is not None:
            if self._loading_time_ms > PageSpeed.ACCEPTABLE_LOADING_TIME_MS:
                issues.append("Slow Page Load Time.")
            elif self._loading_time_ms > PageSpeed.GOOD_LOADING_TIME_MS:
                issues.append("Acceptable Page Load Time (needs improvement).")

        # Mixed Content Check
        if self._url and self._url.startswith("https://") and self._soup:
            mixed_content_found = False
            for tag in self._soup.find_all(['img', 'link', 'script']):
                src_or_href = tag.get('src') or tag.get('href')
                if src_or_href and src_or_href.startswith("http://"):
                    issues.append(TechnicalIssues.MIXED_CONTENT)
                    mixed_content_found = True
                    break # Only need to find one instance
            # Check for inline styles with http URLs (less common but possible)
            if not mixed_content_found:
                for tag in self._soup.find_all(lambda tag: tag.has_attr('style')):
                    style_attr = tag['style']
                    if "url('http://" in style_attr or 'url("http://' in style_attr:
                        issues.append(TechnicalIssues.MIXED_CONTENT)
                        break

        return issues

    def _analyze_security_headers(self) -> Dict[str, str]:
        """
        Extracts relevant security headers from the HTTP response.
        """
        security_headers_found: Dict[str, str] = {}
        # Ensure headers are available (e.g., if content was provided directly without network request)
        if not self._response_headers:
            return security_headers_found

        # Iterate through common security headers and add them if present
        for header_name_constant in [
            SecurityHeaders.STRICT_TRANSPORT_SECURITY,
            SecurityHeaders.CONTENT_SECURITY_POLICY,
            SecurityHeaders.X_CONTENT_TYPE_OPTIONS,
            SecurityHeaders.X_FRAME_OPTIONS,
            SecurityHeaders.REFERRER_POLICY,
            SecurityHeaders.PERMISSIONS_POLICY,
        ]:
            # Headers are case-insensitive, so iterate over keys in a case-insensitive manner
            for header_key, header_value in self._response_headers.items():
                if header_key.lower() == header_name_constant.lower():
                    security_headers_found[header_name_constant] = header_value
                    break # Found the header, move to the next constant

        return security_headers_found


    def analyze(self) -> SEOResult:
        """
        Performs a full SEO analysis on the initialized page content,
        including basic page info, technical issues, and security headers.
        """
        # If initialized with a URL and content hasn't been fetched/parsed yet
        if self._url and self._soup is None:
            self._fetch_and_parse_page()

        # Ensure content and soup are available before proceeding
        if self._soup is None or self._status_code is None:
            raise SeokarError("Page content or status code not available for analysis. Cannot proceed.")

        # Extract basic page information
        title = self._get_title()
        meta_description = self._get_meta_description()
        h1_tags = self._get_h1_tags()
        canonical_url = self._get_canonical_url()
        robots_tag = self._get_robots_tag()

        # Perform technical and security analysis
        technical_issues = self._analyze_technical_issues()
        security_headers = self._analyze_security_headers()

        # Initialize placeholder for Core Web Vitals (real values come from browser data)
        core_web_vitals = CoreWebVitalsMetrics()
        # Initialize placeholder for Content Metrics (will be populated later)
        content_metrics: Optional[ContentMetrics] = None


        # Create and return the SEOResult object
        result = SEOResult(
            url=self._url if self._url else "N/A (HTML content provided)",
            status_code=self._status_code,
            page_size_bytes=self._page_size_bytes,
            loading_time_ms=self._loading_time_ms,
            title=title,
            meta_description=meta_description,
            h1_tags=h1_tags,
            canonical_url=canonical_url,
            robots_tag=robots_tag,
            technical_issues=technical_issues,
            security_headers=security_headers,
            schema_present=False, # Placeholder for schema analysis
            core_web_vitals=core_web_vitals,
            content_metrics=content_metrics,
            # analysis_timestamp is automatically set by default_factory
        )
        return result
