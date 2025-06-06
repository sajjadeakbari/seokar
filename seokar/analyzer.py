import time
from typing import Optional, List, Dict, Any

from bs4 import BeautifulSoup

from ..models import SEOResult, CoreWebVitalsMetrics, ContentMetrics
from ..exceptions import SeokarError, SeokarHTTPError
from ..utils.network import fetch_page_content, get_url_status, SimpleCache
from ..utils.helpers import get_page_size_bytes, is_valid_url
from ..constants.core import StatusCode


class SeokarAnalyzer:
    """
    The core analysis engine for the Seokar library.
    Responsible for fetching content, parsing HTML, and extracting basic SEO elements.
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
        self._cache = cache if cache is not None else SimpleCache()

        # If HTML content is provided directly, initialize properties and BeautifulSoup immediately
        if html_content:
            self._html_content_str = html_content
            self._html_content_bytes = html_content.encode('utf-8', errors='ignore')
            self._status_code = StatusCode.OK  # Assume success if content is directly provided
            self._loading_time_ms = 0.0  # No network load time
            self._page_size_bytes = get_page_size_bytes(self._html_content_bytes)
            self._soup = BeautifulSoup(self._html_content_str, "html.parser")

    def _fetch_and_parse_page(self) -> None:
        """
        Responsible for fetching page content and status code, and initializing BeautifulSoup.
        Handles caching for network requests.
        """
        if not self._url or not is_valid_url(self._url):
            raise SeokarError(f"Invalid URL provided: {self._url}")

        cached_data = self._cache.get(self._url)
        
        if cached_data:
            # If data is in cache, use it
            self._html_content_bytes, self._status_code = cached_data
            self._loading_time_ms = 0.0  # Indicate it was served from cache
            self._page_size_bytes = get_page_size_bytes(self._html_content_bytes)
        else:
            # Otherwise, fetch from network
            start_time = time.perf_counter()
            content_bytes = fetch_page_content(self._url)
            end_time = time.perf_counter()
            
            self._loading_time_ms = (end_time - start_time) * 1000

            # Get the actual status code via a HEAD request
            status_code = get_url_status(self._url)
            
            if status_code is None:
                raise SeokarError(f"Failed to get status code for {self._url} after retries.")
            self._status_code = status_code

            if content_bytes is None:
                raise SeokarHTTPError(f"Failed to fetch content for {self._url}. Status Code: {self._status_code}", status_code=self._status_code)

            self._html_content_bytes = content_bytes
            self._page_size_bytes = get_page_size_bytes(self._html_content_bytes)
            
            # Cache the fetched content bytes and status code
            self._cache.set(self._url, (self._html_content_bytes, self._status_code))

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
            # Fallback to Open Graph description if meta description is not found
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

    def analyze(self) -> SEOResult:
        """
        Performs a full SEO analysis on the initialized page content.
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

        # Initialize placeholder fields for future analysis stages
        technical_issues: List[str] = []
        security_headers: Dict[str, str] = {}
        schema_present: bool = False
        core_web_vitals: Optional[CoreWebVitalsMetrics] = None
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
            schema_present=schema_present,
            core_web_vitals=core_web_vitals,
            content_metrics=content_metrics,
            # analysis_timestamp is automatically set by default_factory
        )
        return result
