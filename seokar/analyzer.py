"""
Seokar - Ultimate On-Page SEO Analysis Library for Python

A comprehensive, thread-safe, and memory-efficient toolkit for detailed on-page SEO analysis,
providing deep insights into meta tags, content quality, structure, links, social presence,
and structured data, complete with actionable recommendations and SEO health scoring.
This library is designed for accuracy, performance, and ease of use.

Key Features:
- Flawless analysis with detailed results categorized by severity (INFO, GOOD, WARNING, ERROR, CRITICAL).
- Thread-safe intelligent caching mechanism for optimized performance on repeated access.
- Strict type hinting (including Literal for Enums) for enhanced code quality and IDE support.
- Comprehensive documentation with clear usage examples for all public methods.
- Customizable constants for SEO best practices (e.g., optimal lengths, stop words).
- Enhanced built-in logging with rich contextual information for easier debugging.
- Optimized for memory usage through the use of __slots__.
- Versioned for reliable dependency management and tracking.
- Strict input validation for robust operation under various conditions.
- Advanced URL handling considering <base> tags and complex relative path resolution.
- Robust favicon detection including fallbacks to default locations.
- Advanced keyword density analysis including n-gram (bigram) support.
"""

__version__ = "1.0.0"  # Version Management (Module Level)

from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any, Tuple, Set, Union, Literal
from urllib.parse import urlparse, urljoin
import re
from dataclasses import dataclass
from enum import Enum
import json
from collections import defaultdict
import logging
import threading

# Configure basic logging for the library
# Users can further customize this logger instance if needed by getting it via logging.getLogger(__name__)
logger = logging.getLogger(__name__)
if not logger.hasHandlers(): # Avoid adding multiple handlers if library is re-imported or logger already configured
    _handler = logging.StreamHandler()
    # Enhanced Formatter to display 'url' and 'element' from the 'extra' dict in log records
    _formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [URL: %(url)s] - [Element: %(element)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)
    logger.setLevel(logging.WARNING) # Default logging level for the library operations

class SEOResultLevel(Enum):
    """Strictly typed severity levels for SEO analysis results."""
    INFO: Literal[0] = 0
    GOOD: Literal[1] = 1
    WARNING: Literal[2] = 2
    ERROR: Literal[3] = 3
    CRITICAL: Literal[4] = 4

@dataclass
class SEOResult:
    """Container for a single SEO analysis result item with post-init validation."""
    level: SEOResultLevel
    message: str
    element_type: str # e.g., "Title", "Meta Description", "Image Alt"
    details: Optional[str] = None
    recommendation: Optional[str] = None

    def __post_init__(self):
        """Validates that the level attribute is a proper SEOResultLevel enum instance."""
        if not isinstance(self.level, SEOResultLevel):
            try:
                # Attempt to convert if an integer or string value of the enum member was passed
                self.level = SEOResultLevel(self.level)
            except ValueError: # If conversion fails (e.g., invalid int or str)
                raise ValueError(
                    f"Invalid SEOResultLevel value provided: '{self.level}'. "
                    f"Must be an SEOResultLevel enum member or its valid integer/string representation."
                )

class Seokar:
    """
    Performs advanced on-page SEO analysis of HTML content and generates a comprehensive, flawless report.
    Provides detailed insights into meta tags, content quality, page structure, links, social media presence,
    and structured data, complete with actionable recommendations and an overall SEO health score.

    Attributes:
        OPTIMAL_TITLE_LENGTH (Tuple[int, int]): Recommended min/max length for page titles.
        OPTIMAL_DESCRIPTION_LENGTH (Tuple[int, int]): Recommended min/max length for meta descriptions.
        MAX_H1_TAGS (int): Maximum recommended number of H1 tags per page.
        MIN_CONTENT_LENGTH (int): Minimum recommended character length for main page content.
        MAX_HEADING_LENGTH (int): Maximum recommended character length for important headings (e.g., H1-H3).
        MAX_HEADING_WORDS (int): Maximum recommended word count for important headings.
        MAX_ALT_TEXT_LENGTH (int): Maximum recommended character length for image alt text.
        MIN_TEXT_HTML_RATIO (float): Minimum recommended text-to-HTML ratio percentage.
        KEYWORD_DENSITY_MIN_WORD_LEN (int): Minimum word length to consider for keyword density.
        KEYWORD_DENSITY_MIN_THRESHOLD_PERCENT (float): Minimum density percentage for a term to be included in results.
        STOP_WORDS (Set[str]): A set of common stop words (English) to be excluded from keyword analysis.

    Usage:
        >>> html_document = "<html><head><title>My Awesome Page</title></head><body><h1>Welcome!</h1></body></html>"
        >>> seo_analyzer = Seokar(html_content=html_document, url="https://example.com/awesome-page")
        >>> report = seo_analyzer.analyze()
        >>> print(f"Seokar Library Version: {seo_analyzer.get_version()}")
        >>> print(f"Overall SEO Health Score: {report['seo_health']['score']}%")
        >>> for issue in report['issues']:
        ...     # SEOResult stores level as Enum, but in report['issues'] it's dict, so compare value
        ...     if SEOResultLevel(issue['level']).value >= SEOResultLevel.WARNING.value:
        ...         print(f"- Issue ({issue['element_type']}): {issue['message']}")
        ...         if issue['recommendation']:
        ...             print(f"  Recommendation: {issue['recommendation']}")
    """
    __slots__ = [
        'html_content', 'url', 'soup', '_results',
        '_meta_tags_cache', '_all_headings_cache',
        '_all_links_cache', '_main_content_text_cache',
        '_all_images_cache', '_json_ld_cache',
        '_cache_lock'
    ]

    OPTIMAL_TITLE_LENGTH: Tuple[int, int] = (30, 60)
    OPTIMAL_DESCRIPTION_LENGTH: Tuple[int, int] = (70, 160)
    MAX_H1_TAGS: int = 1
    MIN_CONTENT_LENGTH: int = 300
    MAX_HEADING_LENGTH: int = 70
    MAX_HEADING_WORDS: int = 12
    MAX_ALT_TEXT_LENGTH: int = 125
    MIN_TEXT_HTML_RATIO: float = 15.0
    KEYWORD_DENSITY_MIN_WORD_LEN: int = 3
    KEYWORD_DENSITY_MIN_THRESHOLD_PERCENT: float = 1.0 # e.g. 1.0 means 1%

    STOP_WORDS: Set[str] = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'how', 'if', 'get', 'got',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'this', 'these', 'those',
        'to', 'was', 'were', 'will', 'with', 'i', 'you', 'me', 'my', 'we', 'our', 'or', 'html',
        'they', 'them', 'their', 'then', 'there', 'not', 'so', 'just', 'can', 'do', 'does', 'did',
        'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
        'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
        'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
        'don', "don't", 'should', "shouldn't", 'now', 've', 'll', 'page', 'content', 'tag', 'meta'
    } # Expanded stop words

    def __init__(self, html_content: str, url: Optional[str] = None):
        """
        Initializes the Seokar analyzer with HTML content and an optional URL.
        
        Args:
            html_content: The raw HTML content string to be analyzed.
            url: The original URL of the HTML content. Used for context like resolving
                 relative URLs and certain validation checks.
            
        Raises:
            TypeError: If `html_content` is not a string.
            ValueError: If `html_content` is empty/whitespace or `url` (if provided) is invalid.
        """
        if not isinstance(html_content, str):
            raise TypeError("HTML content must be a string.")
        if not html_content.strip():
            raise ValueError("HTML content cannot be empty or contain only whitespace.")

        self.html_content: str = html_content

        if url:
            if not self._is_valid_url(url):
                logger.warning(
                    f"Invalid URL provided: '{url}'. This may affect relative URL resolution and some domain-specific checks. "
                    "Proceeding without a fully qualified base URL for such operations."
                )
                self.url: Optional[str] = None # Set to None if invalid but was provided
            else:
                self.url: Optional[str] = url
        else:
            self.url: Optional[str] = None

        self.soup: BeautifulSoup = BeautifulSoup(self.html_content, 'html.parser')
        self._results: List[SEOResult] = []
        self._cache_lock = threading.Lock()

        self._meta_tags_cache: Dict[str, Optional[Union[str, List[str]]]] = {}
        self._all_headings_cache: Optional[Dict[str, List[str]]] = None
        self._all_links_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._main_content_text_cache: Optional[str] = None
        self._all_images_cache: Optional[List[Any]] = None
        self._json_ld_cache: Optional[List[Dict[str, Any]]] = None

    def _is_valid_url(self, url_string: Optional[str]) -> bool:
        """Helper function to validate if a URL string is well-formed and has HTTP/HTTPS scheme."""
        if not url_string:
            return False
        try:
            result = urlparse(url_string)
            # Must have a scheme (http, https) and a netloc (domain name)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except ValueError: # Handles malformed URLs that urlparse might raise issues with
            return False

    def get_version(self) -> str:
        """
        Returns the current version of the Seokar library.
        
        Returns:
            str: The library version string (e.g., "1.0.0").
        """
        return __version__

    def _reset_analysis_state(self) -> None:
        """Resets internal state variables (results and caches) for a fresh analysis run."""
        self._results = []
        self._meta_tags_cache = {}
        self._all_headings_cache = None
        self._all_links_cache = None
        self._main_content_text_cache = None
        self._all_images_cache = None
        self._json_ld_cache = None

    def analyze(self) -> Dict[str, Any]:
        """
        Performs a comprehensive on-page SEO analysis and returns a detailed report.
        The report includes various SEO aspects, an overall health score, identified issues,
        and actionable recommendations.
        
        Returns:
            A dictionary representing the full SEO analysis report.
        """
        self._reset_analysis_state()
        report: Dict[str, Any] = {
            "analyzer_version": self.get_version(),
            "url": self.url,
            "basic_seo": self._analyze_basic_seo(),
            "headings": self._analyze_headings_structure(),
            "content_quality": self._analyze_content_quality(),
            "images": self._analyze_images_alt_text(),
            "links": self._analyze_page_links(),
            "social_media_tags": self._get_social_media_tags_data(),
            "structured_data": self._get_all_structured_data_info(),
        }
        report["seo_health"] = self._calculate_seo_health_score()
        # Convert SEOResult objects to dictionaries for the final report
        report["issues"] = [res.__dict__ for res in self._results]
        report["recommendations"] = self._get_all_actionable_recommendations()
        return report

    def _add_result(self, level: SEOResultLevel, message: str, element_type: str,
                    details: Optional[str] = None, recommendation: Optional[str] = None) -> None:
        """Adds an SEO analysis result and logs it with contextual information."""
        log_level_map = {
            SEOResultLevel.INFO: logging.INFO,
            SEOResultLevel.GOOD: logging.DEBUG, # Good results are typically for debug/verbose mode
            SEOResultLevel.WARNING: logging.WARNING,
            SEOResultLevel.ERROR: logging.ERROR,
            SEOResultLevel.CRITICAL: logging.CRITICAL,
        }
        log_context = {"url": str(self.url or "N/A"), "element": element_type}
        log_msg_main = f"{message}"
        if details:
            log_msg_main += f" (Details: {details})"
        
        effective_log_level = log_level_map.get(level, logging.INFO)
        if logger.isEnabledFor(effective_log_level):
            # The 'extra' dict is passed to the logger. The formatter needs to be configured to use these.
            logger.log(effective_log_level, log_msg_main, extra=log_context)

        self._results.append(SEOResult(level, message, element_type, details, recommendation))

    def get_title(self) -> Optional[str]:
        """
        Extracts and returns the page title from the <title> tag.
        The result is cached for subsequent calls.
        
        Returns:
            Optional[str]: The text content of the title tag if found, otherwise None.
        
        Example:
            >>> analyzer = Seokar("<html><head><title>My Page</title></head></html>")
            >>> analyzer.get_title()
            'My Page'
        """
        cache_key = 'title_text'
        if cache_key not in self._meta_tags_cache:
            title_tag = self.soup.find('title')
            self._meta_tags_cache[cache_key] = title_tag.get_text(strip=True) if title_tag else None
        return self._meta_tags_cache[cache_key] # type: ignore

    def get_meta_description(self) -> Optional[str]:
        """
        Extracts and returns the content of the meta description tag.
        The result is cached.
        
        Returns:
            Optional[str]: The content of the meta description if found and not empty, otherwise None.
        
        Example:
            >>> html = '<meta name="description" content="Awesome page.">'
            >>> analyzer = Seokar(f"<html><head>{html}</head></html>")
            >>> analyzer.get_meta_description()
            'Awesome page.'
        """
        cache_key = 'meta_description_content'
        if cache_key not in self._meta_tags_cache:
            meta_tag = self.soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
            content = meta_tag.get('content', '').strip() if meta_tag and meta_tag.get('content') else None
            self._meta_tags_cache[cache_key] = content if content else None # Store None if empty or not found
        return self._meta_tags_cache[cache_key] # type: ignore

    def get_meta_robots(self) -> List[str]:
        """
        Extracts and returns the directives from the meta robots tag.
        Directives are returned as a list of lowercased strings. The result is cached.
        
        Returns:
            List[str]: A list of robots directives (e.g., ['index', 'nofollow']). Empty if not found.
        
        Example:
            >>> html = '<meta name="robots" content="noindex, nofollow">'
            >>> analyzer = Seokar(f"<html><head>{html}</head></html>")
            >>> analyzer.get_meta_robots()
            ['noindex', 'nofollow']
        """
        cache_key = 'meta_robots_directives'
        if cache_key not in self._meta_tags_cache:
            directives: List[str] = []
            meta_tag = self.soup.find('meta', attrs={'name': re.compile(r'^robots$', re.I)})
            if meta_tag and meta_tag.get('content'):
                directives = [d.strip().lower() for d in meta_tag['content'].split(',') if d.strip()]
            self._meta_tags_cache[cache_key] = directives
        return self._meta_tags_cache[cache_key] # type: ignore

    def get_canonical_url(self) -> Optional[str]:
        """
        Extracts, absolutizes, and returns the canonical URL from the <link rel="canonical"> tag.
        The result is cached.
        
        Returns:
            Optional[str]: The absolute canonical URL if found, otherwise None.
        
        Example:
            >>> html = '<link rel="canonical" href="/preferred/">'
            >>> analyzer = Seokar(f"<html><head>{html}</head></html>", url="https://ex.com")
            >>> analyzer.get_canonical_url()
            'https://ex.com/preferred/'
        """
        cache_key = 'canonical_url_absolute'
        if cache_key not in self._meta_tags_cache:
            canonical_tag = self.soup.find('link', attrs={'rel': re.compile(r'^canonical$', re.I)})
            href = canonical_tag.get('href', '').strip() if canonical_tag and canonical_tag.get('href') else None
            self._meta_tags_cache[cache_key] = self._make_absolute_url(href) # _make_absolute_url handles None href
        return self._meta_tags_cache[cache_key] # type: ignore

    def get_viewport(self) -> Optional[str]:
        """
        Extracts and returns the content of the viewport meta tag.
        The result is cached.
        
        Returns:
            Optional[str]: The content of the viewport tag if found and not empty, otherwise None.
        
        Example:
            >>> html = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            >>> analyzer = Seokar(f"<html><head>{html}</head></html>")
            >>> analyzer.get_viewport()
            'width=device-width, initial-scale=1.0'
        """
        cache_key = 'viewport_content'
        if cache_key not in self._meta_tags_cache:
            tag = self.soup.find('meta', attrs={'name': re.compile(r'^viewport$', re.I)})
            content = tag.get('content', '').strip() if tag and tag.get('content') else None
            self._meta_tags_cache[cache_key] = content if content else None
        return self._meta_tags_cache[cache_key] # type: ignore

    def get_charset(self) -> Optional[str]:
        """
        Detects and returns the character encoding (charset) of the page.
        Checks both <meta charset="..."> and <meta http-equiv="Content-Type" ...>.
        The result is cached and returned in lowercase.
        
        Returns:
            Optional[str]: The detected charset (e.g., 'utf-8'), or None if not found.
        
        Example:
            >>> analyzer = Seokar('<html><head><meta charset="UTF-8"></head></html>')
            >>> analyzer.get_charset()
            'utf-8'
        """
        cache_key = 'charset_value'
        if cache_key not in self._meta_tags_cache:
            charset_val = None
            charset_tag = self.soup.find('meta', attrs={'charset': True})
            if charset_tag and charset_tag.get('charset'):
                charset_val = charset_tag['charset'].strip().lower()
            else: # Check http-equiv only if direct charset not found
                http_equiv_tag = self.soup.find('meta', attrs={'http-equiv': re.compile(r'^Content-Type$', re.I)})
                if http_equiv_tag and http_equiv_tag.get('content'):
                    content_attr = http_equiv_tag['content']
                    match = re.search(r'charset=([^;]+)', content_attr, re.I)
                    if match:
                        charset_val = match.group(1).strip().lower()
            self._meta_tags_cache[cache_key] = charset_val
        return self._meta_tags_cache[cache_key] # type: ignore

    def get_html_lang(self) -> Optional[str]:
        """
        Detects and returns the language specified in the <html> tag's 'lang' attribute.
        The result is cached.
        
        Returns:
            Optional[str]: The value of the lang attribute (e.g., 'en', 'es-MX'), or None if not set or empty.
        
        Example:
            >>> analyzer = Seokar('<html lang="en-US"></html>')
            >>> analyzer.get_html_lang()
            'en-US'
        """
        cache_key = 'html_lang_attr'
        if cache_key not in self._meta_tags_cache:
            html_tag = self.soup.find('html')
            lang_attr = html_tag.get('lang', '').strip() if html_tag and html_tag.get('lang') else None
            self._meta_tags_cache[cache_key] = lang_attr if lang_attr else None
        return self._meta_tags_cache[cache_key] # type: ignore

    def get_favicon_url(self) -> Optional[str]:
        """
        Extracts and returns the favicon URL.
        Checks for common <link rel="..."> tags for favicons.
        If no tag is found and a base URL is available, it constructs a URL for the default '/favicon.ico'.
        The result is cached.
        
        Returns:
            Optional[str]: The absolute URL of the favicon, or None if not found or resolvable.
        
        Example:
            >>> html = '<link rel="icon" href="/fav.png">'
            >>> analyzer = Seokar(f"<html><head>{html}</head></html>", url="https://ex.com")
            >>> analyzer.get_favicon_url()
            'https://ex.com/fav.png'
        """
        cache_key = 'favicon_url_absolute_checked'
        if cache_key not in self._meta_tags_cache:
            favicon_url_from_tag: Optional[str] = None
            # List of common 'rel' values for favicons, ordered by preference
            rels_to_check = ['icon', 'shortcut icon', 'apple-touch-icon', 'apple-touch-icon-precomposed']
            found_tag = None
            for rel_val in rels_to_check:
                # Case-insensitive search for rel value
                found_tag = self.soup.find('link', rel=lambda x: x and x.lower() == rel_val.lower())
                if found_tag: break

            if found_tag and found_tag.get('href'):
                href = found_tag.get('href', '').strip()
                if href: # Ensure href is not empty after stripping
                    favicon_url_from_tag = self._make_absolute_url(href)

            if favicon_url_from_tag:
                self._meta_tags_cache[cache_key] = favicon_url_from_tag
            elif self.url and self._is_valid_url(self.url): # Fallback to default /favicon.ico
                self._meta_tags_cache[cache_key] = urljoin(self.url, "/favicon.ico")
            else:
                self._meta_tags_cache[cache_key] = None
        return self._meta_tags_cache[cache_key] # type: ignore

    def _get_meta_tags_by_prefix(self, attribute_name: str, prefix: str) -> Dict[str, str]:
        """Helper to extract meta tags with a specific attribute name and value prefix."""
        tags_dict: Dict[str, str] = {}
        # Using re.IGNORECASE for the prefix matching
        meta_elements = self.soup.find_all('meta', attrs={attribute_name: re.compile(f'^{re.escape(prefix)}', re.IGNORECASE)})
        for meta in meta_elements:
            attr_val = meta.get(attribute_name) # Should exist due to find_all
            content = meta.get('content', '').strip()
            if attr_val and content: # Ensure both property/name and content exist and are not empty
                tags_dict[attr_val] = content
        return tags_dict

    def get_open_graph_tags(self) -> Dict[str, str]:
        """
        Extracts and returns all Open Graph (og:*) tags as a dictionary.
        These tags are typically identified by the 'property' attribute.
        
        Returns:
            Dict[str, str]: A dictionary where keys are OG property names (e.g., 'og:title')
                             and values are their corresponding content.
        
        Example:
            >>> html = '<meta property="og:title" content="My Page"><meta property="og:type" content="website">'
            >>> analyzer = Seokar(f"<html><head>{html}</head></html>")
            >>> analyzer.get_open_graph_tags()
            {'og:title': 'My Page', 'og:type': 'website'}
        """
        return self._get_meta_tags_by_prefix('property', 'og:')

    def get_twitter_card_tags(self) -> Dict[str, str]:
        """
        Extracts and returns all Twitter Card (twitter:*) tags as a dictionary.
        Checks for tags using both 'name' (standard) and 'property' attributes.
        
        Returns:
            Dict[str, str]: A dictionary of Twitter Card tags, with 'name' attribute values
                             taking precedence in case of duplicate property names.
        
        Example:
            >>> html = '<meta name="twitter:card" content="summary"><meta name="twitter:site" content="@example">'
            >>> analyzer = Seokar(f"<html><head>{html}</head></html>")
            >>> analyzer.get_twitter_card_tags()
            {'twitter:card': 'summary', 'twitter:site': '@example'}
        """
        twitter_tags_by_name = self._get_meta_tags_by_prefix('name', 'twitter:')
        twitter_tags_by_property = self._get_meta_tags_by_prefix('property', 'twitter:')
        # Merge, giving precedence to tags found with 'name' attribute if keys conflict
        merged_tags = twitter_tags_by_property.copy()
        merged_tags.update(twitter_tags_by_name) # Values from twitter_tags_by_name will overwrite
        return merged_tags

    def get_all_headings(self) -> Dict[str, List[str]]:
        """
        Extracts all heading tags (H1-H6) and their non-empty text content, organized by level.
        The result is cached.
        
        Returns:
            Dict[str, List[str]]: A dictionary where keys are heading tag names (e.g., 'h1', 'h2')
                                 and values are lists of their corresponding text content.
                                 Levels without any headings are omitted from the dictionary.
        
        Example:
            >>> analyzer = Seokar("<h1>Main Title</h1><h2>Subtitle 1</h2><h2>Subtitle 2</h2>")
            >>> analyzer.get_all_headings()
            {'h1': ['Main Title'], 'h2': ['Subtitle 1', 'Subtitle 2']}
        """
        if self._all_headings_cache is None:
            self._all_headings_cache = {}
            for i in range(1, 7):
                tag_name = f'h{i}'
                tags = self.soup.find_all(tag_name)
                heading_texts = [h.get_text(strip=True) for h in tags if h.get_text(strip=True)] # Only non-empty
                if heading_texts:
                    self._all_headings_cache[tag_name] = heading_texts
        return self._all_headings_cache

    def get_main_content_text(self) -> str:
        """
        Extracts and returns the text from the main content area of the page.
        Uses heuristics (common selectors for main content areas) or falls back to the body text.
        The result is cached for performance. Text is joined with spaces and stripped.
        
        Returns:
            str: The extracted main content text. Can be an empty string if no content is found or
                 if the body itself is empty.
        """
        if self._main_content_text_cache is None:
            # Ordered list of selectors to try for main content
            selectors = [
                'main', 'article', '[role="main"]', '.entry-content', '.post-content',
                '.main-content', '.page-content', '.content', '#content', '#main', '#primary'
            ]
            for selector in selectors:
                element = self.soup.select_one(selector)
                if element:
                    self._main_content_text_cache = element.get_text(separator=' ', strip=True)
                    return self._main_content_text_cache # Return as soon as a primary content area is found

            # Fallback to the entire body if no specific main content element is identified
            body_tag = self.soup.find('body')
            self._main_content_text_cache = body_tag.get_text(separator=' ', strip=True) if body_tag else ''
        return self._main_content_text_cache

    def get_all_images(self) -> List[Any]: # bs4.element.Tag
        """
        Extracts and returns all <img> tags found in the HTML document.
        The result (a list of BeautifulSoup Tag objects) is cached.
        
        Returns:
            List[bs4.element.Tag]: A list of Tag objects, each representing an <img> element.
        """
        if self._all_images_cache is None:
            self._all_images_cache = self.soup.find_all('img')
        return self._all_images_cache

    def _extract_links(self) -> Dict[str, List[Dict[str, Any]]]:
        """Internal helper to perform the actual link extraction. This method is not thread-safe by itself."""
        internal_links: List[Dict[str, Any]] = []
        external_links: List[Dict[str, Any]] = []
        a_tags = self.soup.find_all('a', href=True)
        for tag in a_tags:
            href_original = tag.get('href') # Get original href before stripping
            if not href_original: continue # Skip if href attribute is missing (though find_all should prevent this)

            href_stripped = href_original.strip()
            # Ignore common non-HTTP links and fragment-only links (but allow href="#")
            if not href_stripped or href_stripped.startswith(('javascript:', 'mailto:', 'tel:')) or \
               (href_stripped.startswith('#') and len(href_stripped) > 1):
                if href_stripped.startswith('#') and len(href_stripped) > 1:
                    logger.debug(f"Ignoring fragment-only link: '{href_stripped}' at URL: {self.url or 'N/A'}")
                continue

            absolute_url = self._make_absolute_url(href_stripped)
            if absolute_url:
                rel_attributes_raw = tag.get('rel', [])
                # Ensure rel_attributes is always a list of strings for consistent processing
                if isinstance(rel_attributes_raw, str):
                    rel_attributes_list = [rel_attributes_raw.lower().strip()]
                elif isinstance(rel_attributes_raw, list):
                    rel_attributes_list = [str(r).lower().strip() for r in rel_attributes_raw]
                else: # Should not happen with bs4, but safeguard
                    rel_attributes_list = []

                link_data = {
                    'url': absolute_url,
                    'text': tag.get_text(strip=True) or "[No Anchor Text]", # Fallback for empty anchor
                    'title_attr': tag.get('title', '').strip() or None, # Store None if empty
                    'is_nofollow': 'nofollow' in rel_attributes_list,
                    'is_sponsored': 'sponsored' in rel_attributes_list,
                    'is_ugc': 'ugc' in rel_attributes_list,
                }
                if self._is_internal_url(absolute_url):
                    internal_links.append(link_data)
                else:
                    external_links.append(link_data)
        return {'internal': internal_links, 'external': external_links}

    def get_all_links(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extracts all <a> tags with href attributes, categorized into 'internal' and 'external'.
        Link data includes the absolute URL, anchor text, title attribute, and relevant 'rel' attributes
        (nofollow, sponsored, ugc). The result is cached and uses a lock for thread-safety.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary with 'internal' and 'external' link lists.
        
        Example:
            >>> html_content = '<a href="/page1">Internal Link</a> <a href="http://external.com">External Site</a>'
            >>> analyzer = Seokar(html_content, url="https://example.com")
            >>> links_info = analyzer.get_all_links()
            >>> print(f"Found {len(links_info['internal'])} internal links.")
            Found 1 internal links.
        """
        if self._all_links_cache is None:
            with self._cache_lock: # Ensure thread-safe access to the cache
                if self._all_links_cache is None:  # Double-check locking pattern
                    self._all_links_cache = self._extract_links()
        return self._all_links_cache

    def get_json_ld_data(self) -> List[Dict[str, Any]]:
        """
        Extracts and returns all JSON-LD structured data blocks from <script type="application/ld+json"> tags.
        Each block is parsed as a dictionary. If a script contains an array of JSON-LD objects,
        each object is returned as a separate item in the list. The result is cached.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a JSON-LD object.
                                 Returns an empty list if no valid JSON-LD is found or parsing errors occur.
        """
        if self._json_ld_cache is None:
            self._json_ld_cache = []
            scripts = self.soup.find_all('script', type='application/ld+json')
            for script_tag in scripts:
                try:
                    script_content = script_tag.string
                    if script_content and script_content.strip():
                        # Remove HTML comments that might be embedded in JSON-LD by mistake
                        content_no_comments = re.sub(r'<!--.*?-->', '', script_content, flags=re.DOTALL)
                        data = json.loads(content_no_comments)
                        # JSON-LD can be a single object or an array of objects at the top level
                        if isinstance(data, dict):
                            self._json_ld_cache.append(data)
                        elif isinstance(data, list): # If it's an array, add each valid dictionary item
                            self._json_ld_cache.extend(item for item in data if isinstance(item, dict))
                        else: # Parsed but not a dict or list of dicts
                             self._add_result(SEOResultLevel.WARNING, "Invalid JSON-LD Top-Level Structure", "JSON-LD",
                                             "Parsed JSON-LD content is not a valid JSON object or an array of JSON objects.",
                                             "Ensure your top-level JSON-LD is a JSON object or an array of JSON objects.")
                    else: # Empty script tag or whitespace only
                        self._add_result(SEOResultLevel.INFO, "Empty JSON-LD Script Tag", "JSON-LD",
                                         "An empty <script type='application/ld+json'> tag was found.",
                                         "Remove empty JSON-LD script tags or populate them with valid structured data.")
                except json.JSONDecodeError as e:
                    logger.warning(
                        f"JSON-LD parsing error. URL: {self.url or 'N/A'}. "
                        f"Snippet: {str(script_tag.string)[:100]}... Error: {e}"
                    )
                    self._add_result(SEOResultLevel.ERROR, "JSON-LD Parsing Error", "JSON-LD",
                                     f"Failed to parse JSON-LD. Error: {e}. "
                                     f"Check content near: {str(script_tag.string)[:70]}...",
                                     "Validate your JSON-LD markup (e.g., using Google's Rich Results Test or Schema Markup Validator).")
        return self._json_ld_cache

    def get_microdata(self) -> List[Dict[str, Any]]:
        """
        Extracts Microdata items from HTML elements with 'itemscope' and 'itemtype' attributes.
        Attempts to capture properties associated with each item.
        
        Note: Full Microdata parsing can be complex, especially with nested items and 'itemref'.
        This implementation provides a good extraction of top-level properties.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a Microdata item
                                 with its 'type' and a 'properties' dictionary.
        """
        microdata_items: List[Dict[str, Any]] = []
        for item_tag in self.soup.find_all(attrs={'itemscope': True}):
            item_props: Dict[str, Any] = {}
            # Iterate over tags that have 'itemprop' and are descendants of the current 'item_tag'
            for prop_tag in item_tag.find_all(attrs={'itemprop': True}):
                # Crucial check: Ensure this prop_tag belongs directly to the current item_tag,
                # not to a nested itemscope element that is also a descendant.
                # The closest parent itemscope should be the current item_tag.
                closest_itemscope_parent = prop_tag.find_parent(attrs={'itemscope': True})
                if closest_itemscope_parent != item_tag:
                    continue # This property belongs to a nested item, not the current one.

                prop_name_list = prop_tag.get('itemprop', '').split() # itemprop can be space-separated list of names
                if not prop_name_list: continue # Should not happen if itemprop attr exists

                prop_value: Optional[Union[str, List[str]]] = None
                if prop_tag.get('itemscope') is not None: # This property is itself an itemscope
                    prop_value = "[Nested Microdata Object]" # Placeholder; full parsing would recurse
                elif prop_tag.name == 'meta':
                    prop_value = prop_tag.get('content')
                elif prop_tag.name in ['img', 'audio', 'video', 'iframe', 'embed', 'object', 'data', 'source', 'track']:
                    prop_value = prop_tag.get('src') or prop_tag.get('data') # common media/data attributes
                elif prop_tag.name in ['a', 'link', 'area']:
                    prop_value = prop_tag.get('href')
                elif prop_tag.name == 'time':
                    prop_value = prop_tag.get('datetime')
                else: # General case: text content of the element
                    prop_value = prop_tag.get_text(strip=True)
                
                if prop_value is not None: # Only add if a value was successfully extracted
                    for prop_name_single in prop_name_list:
                        prop_name = prop_name_single.strip()
                        if not prop_name: continue

                        if prop_name in item_props: # Property already exists, make it a list
                            if not isinstance(item_props[prop_name], list):
                                item_props[prop_name] = [item_props[prop_name]]
                            item_props[prop_name].append(prop_value)
                        else: # New property
                            item_props[prop_name] = prop_value
            
            if item_props: # Only add the Microdata item if it has at least one property
                item_type_str = item_tag.get('itemtype', '').strip()
                microdata_items.append({
                    'type': item_type_str if item_type_str else "[No Type Declared]",
                    'properties': item_props
                })
        return microdata_items

    def get_rdfa_data(self) -> List[Dict[str, Any]]:
        """
        Extracts RDFa Lite data from HTML elements with 'typeof' and 'property' attributes.
        
        Note: Full RDFa parsing is complex. This provides a basic extraction.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing an RDFa item
                                 with its 'type', 'resource_uri', and 'properties'.
        """
        rdfa_items: List[Dict[str, Any]] = []
        # Find all elements that define a new typed resource ('typeof' attribute)
        for item_tag in self.soup.find_all(attrs={'typeof': True}):
            item_props: Dict[str, Any] = {}
            # Find properties associated with this resource.
            # These could be children or the element itself if it also has 'property'.
            
            # Process properties on descendant elements that are explicitly linked to this item_tag
            for prop_tag in item_tag.find_all(attrs={'property': True}):
                # Ensure this prop_tag belongs to the current item_tag, not a nested one
                parent_typed_resource = prop_tag.find_parent(attrs={'typeof': True})
                if parent_typed_resource != item_tag:
                    continue # This property belongs to a nested (or different) typed resource

                prop_name_list = prop_tag.get('property', '').split() # property can be space-separated
                if not prop_name_list: continue

                prop_value: Optional[Union[str, List[str]]] = None
                if prop_tag.get('typeof') is not None and prop_tag != item_tag: # Nested typed resource as property value
                    prop_value = "[Nested RDFa Object]"
                elif prop_tag.get('content'): # Usually for <meta> or when content attribute specifies value
                    prop_value = prop_tag['content']
                elif prop_tag.get('href'): # For <a>, <link>
                    prop_value = prop_tag.get('href')
                elif prop_tag.get('src'): # For <img>, <script>, <iframe>
                    prop_value = prop_tag.get('src')
                elif prop_tag.name == 'time' and prop_tag.get('datetime'):
                    prop_value = prop_tag['datetime']
                else: # Default to text content
                    prop_value = prop_tag.get_text(strip=True)
                
                if prop_value is not None:
                    for prop_name_single in prop_name_list:
                        prop_name = prop_name_single.strip()
                        if not prop_name: continue
                        if prop_name in item_props:
                            if not isinstance(item_props[prop_name], list):
                                item_props[prop_name] = [item_props[prop_name]]
                            item_props[prop_name].append(prop_value)
                        else:
                            item_props[prop_name] = prop_value
            
            # Add the item if it has properties or a specific resource identifier
            resource_uri = item_tag.get('resource', item_tag.get('about', item_tag.get('src', item_tag.get('href'))))
            if item_props or resource_uri:
                rdfa_items.append({
                    'type': item_tag.get('typeof','').strip() or "[No Type Declared]",
                    'resource_uri': resource_uri.strip() if resource_uri else None,
                    'properties': item_props
                })
        return rdfa_items

    def _analyze_basic_seo(self) -> Dict[str, Any]:
        """Analyzes and validates fundamental SEO elements."""
        title = self.get_title()
        description = self.get_meta_description()
        robots = self.get_meta_robots()
        canonical_url = self.get_canonical_url()
        viewport = self.get_viewport()
        charset = self.get_charset()
        html_lang = self.get_html_lang()
        favicon = self.get_favicon_url()

        if not title:
            self._add_result(SEOResultLevel.CRITICAL, "Missing Title Tag", "Title",
                             "The <title> tag is crucial; it's missing.",
                             f"Add a unique, descriptive title ({self.OPTIMAL_TITLE_LENGTH[0]}-{self.OPTIMAL_TITLE_LENGTH[1]} chars).")
        else:
            l = len(title)
            if l < self.OPTIMAL_TITLE_LENGTH[0]: self._add_result(SEOResultLevel.WARNING, "Title Too Short", "Title", f"Length {l} (optimal {self.OPTIMAL_TITLE_LENGTH[0]}-{self.OPTIMAL_TITLE_LENGTH[1]}).", "Expand title.")
            elif l > self.OPTIMAL_TITLE_LENGTH[1]: self._add_result(SEOResultLevel.WARNING, "Title Too Long", "Title", f"Length {l} (optimal {self.OPTIMAL_TITLE_LENGTH[0]}-{self.OPTIMAL_TITLE_LENGTH[1]}).", "Shorten title.")
            else: self._add_result(SEOResultLevel.GOOD, "Optimal Title Length", "Title", f"Length {l} is optimal.", None)

        if not description:
            self._add_result(SEOResultLevel.WARNING, "Missing Meta Description", "Meta Description", "Meta description missing.", f"Add description ({self.OPTIMAL_DESCRIPTION_LENGTH[0]}-{self.OPTIMAL_DESCRIPTION_LENGTH[1]} chars).")
        else:
            l = len(description)
            if l < self.OPTIMAL_DESCRIPTION_LENGTH[0]: self._add_result(SEOResultLevel.WARNING, "Meta Description Too Short", "Meta Description", f"Length {l} (optimal {self.OPTIMAL_DESCRIPTION_LENGTH[0]}-{self.OPTIMAL_DESCRIPTION_LENGTH[1]}).", "Expand description.")
            elif l > self.OPTIMAL_DESCRIPTION_LENGTH[1]: self._add_result(SEOResultLevel.WARNING, "Meta Description Too Long", "Meta Description", f"Length {l} (optimal {self.OPTIMAL_DESCRIPTION_LENGTH[0]}-{self.OPTIMAL_DESCRIPTION_LENGTH[1]}).", "Shorten description.")
            else: self._add_result(SEOResultLevel.GOOD, "Optimal Meta Description Length", "Meta Description", f"Length {l} is optimal.", None)

        if not robots: self._add_result(SEOResultLevel.INFO, "Meta Robots Not Specified", "Meta Robots", "Defaults to 'index, follow'.", "Add if specific directives needed.")
        if 'noindex' in robots: self._add_result(SEOResultLevel.CRITICAL, "Page is NoIndexed", "Meta Robots", "'noindex' present, prevents indexing.", "Remove 'noindex' if page should be indexed.")
        if 'nofollow' in robots: self._add_result(SEOResultLevel.WARNING, "Page is NoFollow", "Meta Robots", "'nofollow' present, links won't be followed.", "Remove 'nofollow' if links should pass equity.")

        if not canonical_url: self._add_result(SEOResultLevel.WARNING, "Missing Canonical URL", "Canonical URL", "No canonical URL specified. Risk of duplicate content.", "Add <link rel='canonical'> pointing to the preferred version.")
        elif self.url and self._is_valid_url(self.url):
            norm_page = self.url.rstrip('/')
            norm_canon = canonical_url.rstrip('/') # Canonical URL is already absolute from getter
            if norm_page != norm_canon: self._add_result(SEOResultLevel.WARNING, "Canonical URL Mismatch", "Canonical URL", f"Page URL ('{self.url}') differs from canonical ('{canonical_url}').", "Ensure canonical points to the correct preferred version if this is not intentional.")
            else: self._add_result(SEOResultLevel.GOOD, "Canonical URL Matches Page URL", "Canonical URL", "Canonical URL correctly points to the current page.", None)
        elif canonical_url: self._add_result(SEOResultLevel.INFO, "Canonical URL Present (No Page URL for Comparison)", "Canonical URL", f"Canonical URL found: {canonical_url}.", None)

        if not viewport: self._add_result(SEOResultLevel.ERROR, "Missing Viewport Meta Tag", "Viewport", "Viewport meta tag is missing, crucial for mobile responsiveness.", "Add '<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">'.")
        elif "width=device-width" not in viewport or "initial-scale=1" not in viewport: self._add_result(SEOResultLevel.WARNING, "Suboptimal Viewport Configuration", "Viewport", f"Content: '{viewport}'. Might not be optimal.", "Ensure 'width=device-width' and 'initial-scale=1.0'.")
        else: self._add_result(SEOResultLevel.GOOD, "Viewport Configured for Mobile", "Viewport", "Viewport appears correctly configured.", None)

        if not charset: self._add_result(SEOResultLevel.ERROR, "Charset Not Declared", "Charset", "Character encoding missing. Can cause display issues.", "Declare <meta charset=\"UTF-8\"> (recommended).")
        elif charset.lower() != 'utf-8': self._add_result(SEOResultLevel.WARNING, "Non-UTF-8 Charset Used", "Charset", f"Charset is '{charset}'. UTF-8 recommended for compatibility.", "Consider switching to UTF-8.")
        else: self._add_result(SEOResultLevel.GOOD, "UTF-8 Charset Declared", "Charset", "Page uses UTF-8 character encoding.", None)

        if not html_lang: self._add_result(SEOResultLevel.WARNING, "HTML Language Not Declared", "HTML Language", "Language not declared in <html> tag. Important for accessibility and SEO.", "Add 'lang' attribute to <html> tag (e.g., <html lang=\"en\">).")
        else: self._add_result(SEOResultLevel.GOOD, "HTML Language Declared", "HTML Language", f"HTML language declared as '{html_lang}'.", None)

        if not favicon: self._add_result(SEOResultLevel.INFO, "Favicon Not Detected or Specified", "Favicon", "No specific favicon link tag found, and default /favicon.ico might not be intended or exist.", "Add a specific favicon link tag for consistent branding.")
        else: self._add_result(SEOResultLevel.GOOD, "Favicon Link/Default Resolved", "Favicon", f"A favicon URL was resolved: {favicon}", None)

        return {
            "title": title, "title_length": len(title or ""),
            "meta_description": description, "meta_description_length": len(description or ""),
            "meta_robots": robots, "canonical_url": canonical_url, "viewport": viewport,
            "charset": charset, "html_lang": html_lang, "favicon_url": favicon
        }

    def _analyze_headings_structure(self) -> Dict[str, Any]:
        """Analyzes heading (H1-H6) structure, hierarchy, and content quality."""
        all_headings = self.get_all_headings()
        h1_tags_content = all_headings.get('h1', [])
        h1_count = len(h1_tags_content)

        if not all_headings:
            self._add_result(SEOResultLevel.WARNING, "No Headings Found", "Headings Structure",
                             "The page does not contain any heading tags (H1-H6).",
                             "Use heading tags (H1-H6) to structure your content logically for users and search engines.")
        else:
            if h1_count == 0:
                self._add_result(SEOResultLevel.ERROR, "Missing H1 Tag", "H1 Tag",
                                 "The page is missing an H1 tag, which is critical for defining the main topic.",
                                 "Add a single, descriptive H1 tag that accurately reflects the page's primary content.")
            elif h1_count > self.MAX_H1_TAGS:
                self._add_result(SEOResultLevel.WARNING, f"Multiple H1 Tags ({h1_count})", "H1 Tag",
                                 f"The page has {h1_count} H1 tags. While HTML5 allows multiple H1s in sectioning elements, for SEO clarity, a single main H1 is generally preferred.",
                                 "Ensure a clear primary H1 for the page. If using multiple H1s per HTML5, verify they are within distinct sectioning content elements and are semantically appropriate.")
            else: # Single H1
                self._add_result(SEOResultLevel.GOOD, "Single H1 Tag Present", "H1 Tag",
                                 "Page has a single H1 tag, which is generally the recommended practice for the main page heading.", None)

            present_levels = sorted([int(h_level[1:]) for h_level in all_headings.keys()])
            hierarchy_is_logical = True
            if present_levels and present_levels[0] != 1: # Check if structure starts with H1
                 self._add_result(SEOResultLevel.WARNING, "Heading Structure Starts Incorrectly", "Headings Hierarchy",
                                 f"The heading structure begins with H{present_levels[0]} instead of H1 (or H1 is missing entirely).",
                                 "The primary page heading should be an H1. Ensure your content's heading structure starts with H1 and follows hierarchically (H1 -> H2 -> H3, etc.).")
                 hierarchy_is_logical = False

            for i in range(len(present_levels) - 1): # Check for skipped levels
                if present_levels[i+1] - present_levels[i] > 1:
                    self._add_result(SEOResultLevel.WARNING, "Skipped Heading Level", "Headings Hierarchy",
                                     f"Heading level H{present_levels[i]+1} appears to be missing between H{present_levels[i]} and H{present_levels[i+1]}.",
                                     "Maintain a logical heading hierarchy without skipping levels (e.g., use H2 after H1, H3 after H2, etc.).")
                    hierarchy_is_logical = False
            
            if hierarchy_is_logical and all_headings : # Only add GOOD if no hierarchy issues and headings exist
                 self._add_result(SEOResultLevel.GOOD, "Logical Heading Hierarchy", "Headings Hierarchy",
                                 "The heading structure appears logical and hierarchical without any skipped levels.", None)

            for level_name, texts_in_level in all_headings.items():
                # Content quality checks for H1, H2, H3 (can be extended)
                if level_name in ['h1', 'h2', 'h3']:
                    for heading_text_content in texts_in_level:
                        # Text is already stripped and non-empty from get_all_headings
                        text_len = len(heading_text_content)
                        word_count = len(heading_text_content.split())

                        if text_len > self.MAX_HEADING_LENGTH:
                            self._add_result(SEOResultLevel.WARNING, f"{level_name.upper()} Too Long", f"{level_name.upper()} Content",
                                             f"The {level_name.upper()} text '{heading_text_content[:30]}...' is {text_len} characters long.",
                                             f"Consider keeping important headings like {level_name.upper()} concise (ideally less than {self.MAX_HEADING_LENGTH} characters).")
                        if word_count > self.MAX_HEADING_WORDS:
                            self._add_result(SEOResultLevel.WARNING, f"{level_name.upper()} Too Wordy", f"{level_name.upper()} Content",
                                             f"The {level_name.upper()} text '{heading_text_content[:30]}...' contains {word_count} words.",
                                             f"Try to make important headings like {level_name.upper()} more focused and to the point (ideally less than {self.MAX_HEADING_WORDS} words).")
        return {
            "all_headings": all_headings, "h1_tags_content": h1_tags_content, "h1_count": h1_count,
            "total_headings_count": sum(len(texts) for texts in all_headings.values())
        }

    def _analyze_content_quality(self) -> Dict[str, Any]:
        """Analyzes main content for length, text/HTML ratio, keyword density, and readability."""
        main_content_text = self.get_main_content_text()
        content_length_chars = len(main_content_text)

        if content_length_chars == 0 and self.html_content.strip(): # HTML exists but no text extracted
            self._add_result(SEOResultLevel.WARNING, "No Main Content Text Extracted", "Content Quality",
                             "Could not extract significant textual content from main content selectors or body.",
                             "Ensure main page content is within standard HTML elements (e.g., <main>, <article>, <p>) and not solely image-based or client-side rendered without fallbacks.")
        elif content_length_chars < self.MIN_CONTENT_LENGTH:
            self._add_result(SEOResultLevel.WARNING, "Thin Content (Low Word Count)", "Content Quality",
                             f"Main content length is approximately {content_length_chars} characters (minimum recommended: {self.MIN_CONTENT_LENGTH}).",
                             "Expand your content to provide more valuable, comprehensive, and relevant information for users and to meet search engine quality guidelines.")
        else:
            self._add_result(SEOResultLevel.GOOD, "Sufficient Content Length", "Content Quality",
                             f"Main content length ({content_length_chars} chars) meets or exceeds the minimum recommendation.", None)

        text_html_ratio = self._calculate_text_to_html_ratio()
        if text_html_ratio < self.MIN_TEXT_HTML_RATIO:
            self._add_result(SEOResultLevel.WARNING, "Low Text-to-HTML Ratio", "Content Quality",
                             f"Text-to-HTML ratio is {text_html_ratio}%. This may indicate excessive code/scripts relative to textual content.",
                             "Review page structure for unnecessary code, inline styles/scripts, or large comment blocks. Ensure there is substantial textual content relevant to the page topic.")
        else:
             self._add_result(SEOResultLevel.GOOD, "Acceptable Text-to-HTML Ratio", "Content Quality",
                             f"Text-to-HTML ratio ({text_html_ratio}%) is within an acceptable range, indicating a good balance of text to code.", None)

        readability_score = self._calculate_flesch_reading_ease(main_content_text)
        if content_length_chars > 50: # Only assess readability if there's some content
            if readability_score < 30:
                self._add_result(SEOResultLevel.ERROR, "Very Low Readability Score", "Content Readability",
                                 f"Flesch Reading Ease score is {readability_score}, indicating content is very difficult for the average user to read.",
                                 "Significantly simplify sentence structure, vocabulary, and use shorter paragraphs. Aim for clarity and conciseness.")
            elif readability_score < 60:
                self._add_result(SEOResultLevel.WARNING, "Low to Moderate Readability Score", "Content Readability",
                                 f"Flesch Reading Ease score is {readability_score}. Content may be challenging for some segments of your audience.",
                                 "Consider simplifying complex language and sentence structures to make the content accessible to a broader audience.")
            else: # Score >= 60
                self._add_result(SEOResultLevel.GOOD, "Good Readability Score", "Content Readability",
                                 f"Flesch Reading Ease score is {readability_score}, indicating content is relatively easy to read for the average user.", None)
        elif content_length_chars > 0 :
             self._add_result(SEOResultLevel.INFO, "Readability Not Assessed (Short Content)", "Content Readability",
                             "Content too short for a reliable readability score.", None)


        return {
            "content_length_chars": content_length_chars,
            "text_to_html_ratio_percent": text_html_ratio,
            "keyword_density_top_10_with_bigrams": self._calculate_keyword_density(main_content_text),
            "flesch_reading_ease_score": readability_score if content_length_chars > 50 else None,
            "paragraph_count": len(self.soup.find_all('p')),
            "has_videos_embedded": bool(self.soup.find_all(['video', 'iframe[src*="youtube.com"]', 'iframe[src*="vimeo.com"]'])),
            "has_tables_present": bool(self.soup.find_all('table'))
        }

    def _analyze_images_alt_text(self) -> Dict[str, Any]:
        """Analyzes <img> tags for alt text: presence, emptiness, length, and decorative marking."""
        images = self.get_all_images() # Uses cached images
        total_images = len(images)
        images_with_alt_attr = 0
        images_missing_alt_attr = 0
        images_with_empty_alt = 0 # alt="" or alt="   "
        images_with_long_alt = 0
        decorative_images_correctly_marked = 0

        if total_images == 0:
            self._add_result(SEOResultLevel.INFO, "No Images Found on Page", "Image SEO",
                             "No <img> tags were found in the HTML content. Images can enhance user engagement.",
                             "If images are relevant to your content, consider adding them with appropriate alt text.")
        
        for img_tag in images:
            alt_text_value = img_tag.get('alt')
            # Try to get a meaningful src, fallback to data-src or a placeholder
            img_src_snippet = (img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-lazy-src') or "[Image source not found]")[:60]

            if alt_text_value is None: # Alt attribute is completely missing
                images_missing_alt_attr += 1
                self._add_result(SEOResultLevel.ERROR, "Missing Alt Attribute", "Image Alt Text",
                                 f"Image '{img_src_snippet}...' is missing the 'alt' attribute entirely. This is an accessibility and SEO issue.",
                                 "Add a descriptive 'alt' attribute to all meaningful images. For purely decorative images, use an empty alt attribute (alt=\"\").")
            else: # Alt attribute exists
                images_with_alt_attr += 1
                alt_text_stripped = alt_text_value.strip()
                if not alt_text_stripped: # alt="" or alt="   "
                    images_with_empty_alt += 1
                    # Check if it's explicitly marked as decorative for accessibility
                    if img_tag.get('role') == 'presentation' or img_tag.get('aria-hidden') == 'true':
                        decorative_images_correctly_marked +=1
                        self._add_result(SEOResultLevel.GOOD, "Decorative Image Correctly Marked", "Image Alt Text",
                                     f"Image '{img_src_snippet}...' has an empty alt attribute (alt=\"\") and is marked with role='presentation' or aria-hidden='true', indicating it's decorative.", None)
                    else:
                        self._add_result(SEOResultLevel.WARNING, "Empty Alt Text for Potentially Non-Decorative Image", "Image Alt Text",
                                     f"Image '{img_src_snippet}...' has an empty alt attribute (alt=\"\"). This implies it's decorative.",
                                     "If the image is informative, provide descriptive alt text. If it's purely decorative and conveys no information, alt=\"\" is appropriate; consider also adding role='presentation' for clarity.")
                elif len(alt_text_stripped) > self.MAX_ALT_TEXT_LENGTH:
                    images_with_long_alt += 1
                    self._add_result(SEOResultLevel.WARNING, "Alt Text Too Long", "Image Alt Text",
                                     f"The alt text for image '{img_src_snippet}...' is {len(alt_text_stripped)} characters long (max recommended: {self.MAX_ALT_TEXT_LENGTH}).",
                                     f"Keep alt text concise yet descriptive, ideally under {self.MAX_ALT_TEXT_LENGTH} characters, focusing on the image's purpose and content.")
        
        if total_images > 0 and images_missing_alt_attr == 0 and \
           (images_with_empty_alt == decorative_images_correctly_marked): # All non-decorative images have proper alt text
             self._add_result(SEOResultLevel.GOOD, "Good Image Alt Text Coverage", "Image Alt Text",
                             "All detected images appear to have appropriate alt text attributes or are correctly marked as decorative.", None)
        elif total_images > 0 and images_missing_alt_attr == 0 and images_with_empty_alt > decorative_images_correctly_marked:
             self._add_result(SEOResultLevel.INFO, "Some Images Have Empty Alt Text", "Image Alt Text",
                             f"{images_with_empty_alt - decorative_images_correctly_marked} image(s) have empty alt text and are not explicitly marked decorative. Review them.", None)


        return {
            "total_images_found": total_images,
            "images_with_alt_attribute": images_with_alt_attr,
            "images_missing_alt_attribute": images_missing_alt_attr,
            "images_with_empty_alt_text": images_with_empty_alt,
            "images_with_long_alt_text": images_with_long_alt,
            "decorative_images_correctly_marked": decorative_images_correctly_marked
        }

    def _analyze_page_links(self) -> Dict[str, Any]:
        """Analyzes internal/external links, nofollow attributes, and anchor text distribution."""
        all_links_data = self.get_all_links() # Uses cached links
        internal_links = all_links_data['internal']
        external_links = all_links_data['external']
        
        total_internal = len(internal_links)
        total_external = len(external_links)

        nofollow_internal_count = sum(1 for link in internal_links if link['is_nofollow'])
        nofollow_external_count = sum(1 for link in external_links if link['is_nofollow'])

        if total_internal == 0 and self.url : # If it's a page (has URL) and no internal links
             self._add_result(SEOResultLevel.WARNING, "No Internal Links Found", "Link Structure",
                             "The page does not appear to have any internal links to other pages on the same site.",
                             "Add relevant internal links to improve site navigation, distribute link equity, and help search engines discover other content on your site.")
        
        if nofollow_internal_count > 0:
            self._add_result(SEOResultLevel.INFO, f"{nofollow_internal_count} Internal Nofollow Links", "Link Structure",
                             f"{nofollow_internal_count} internal links have the 'nofollow' attribute. This typically prevents link equity from flowing through these links.",
                             "Review internal nofollow links. Generally, internal links should not be 'nofollow' unless for specific reasons (e.g., links to login pages, user-generated content sections not endorsed).")
        
        # Heuristic for a high ratio of external links which might dilute page focus or appear spammy
        total_links = total_internal + total_external
        if total_links > 0 and total_external > 20 and (total_external / total_links) > 0.6:
            self._add_result(SEOResultLevel.INFO, "High Ratio of External Links", "Link Structure",
                             f"The page has {total_external} external links out of {total_links} total links. This is a significant proportion.",
                             "Ensure all external links are high-quality, relevant, and add value to your users. Consider if 'nofollow' or 'sponsored' attributes are appropriate for some external links.")

        return {
            "total_links_found": total_links,
            "internal_links_count": total_internal,
            "external_links_count": total_external,
            "nofollow_internal_links_count": nofollow_internal_count,
            "nofollow_external_links_count": nofollow_external_count,
            "anchor_text_distribution_percent": self._calculate_anchor_text_distribution(internal_links + external_links),
        }

    def _get_social_media_tags_data(self) -> Dict[str, Any]:
        """Extracts and validates basic Open Graph and Twitter Card meta tags."""
        og_tags = self.get_open_graph_tags() # Uses public getter (which uses _get_meta_tags_by_prefix)
        twitter_tags = self.get_twitter_card_tags() # Uses public getter

        # Open Graph Basic Validation
        required_og_tags = ['og:title', 'og:type', 'og:image', 'og:url']
        missing_og = [req for req in required_og_tags if not og_tags.get(req)] # Check if key exists and has a non-empty value
        if missing_og:
            self._add_result(SEOResultLevel.WARNING, "Missing Essential Open Graph Tags", "Open Graph",
                             f"Missing or empty essential OG tags: {', '.join(missing_og)}. These are important for how content appears when shared on social platforms like Facebook.",
                             "Implement all essential Open Graph tags (og:title, og:type, og:image, og:url) with appropriate content for optimal social sharing.")
        elif not og_tags.get('og:description'): # og:description is highly recommended
             self._add_result(SEOResultLevel.INFO, "Missing Recommended Open Graph Description", "Open Graph",
                             "The og:description tag is missing or empty. It's highly recommended for a more complete social snippet.",
                             "Add an og:description tag to control the summary text when your page is shared on social media platforms.")
        elif og_tags: # All required present and non-empty
             self._add_result(SEOResultLevel.GOOD, "Essential Open Graph Tags Present", "Open Graph",
                             "Essential Open Graph tags (title, type, image, url) are present and have content.", None)

        # Twitter Card Basic Validation
        if twitter_tags:
            card_type = twitter_tags.get('twitter:card')
            if not card_type:
                self._add_result(SEOResultLevel.WARNING, "Missing Twitter Card Type", "Twitter Card",
                                 "The 'twitter:card' tag, specifying the card type (e.g., 'summary', 'summary_large_image'), is missing or empty.",
                                 "Specify a Twitter Card type using the 'twitter:card' meta tag for optimal display on Twitter.")
            # For most card types, title and image are crucial. Description is also highly recommended.
            elif not twitter_tags.get('twitter:title') or not twitter_tags.get('twitter:image'):
                 self._add_result(SEOResultLevel.WARNING, "Potentially Incomplete Twitter Card Tags", "Twitter Card",
                                 "Twitter Card type is specified, but other important tags like twitter:title or twitter:image might be missing or empty.",
                                 "Ensure your Twitter Card includes twitter:title, twitter:description (recommended), and twitter:image for optimal display and engagement on Twitter.")
            else: # Card type and other essentials seem present
                 self._add_result(SEOResultLevel.GOOD, "Twitter Card Tags Appear Configured", "Twitter Card",
                                 f"Twitter Card type '{card_type}' is specified and essential tags (title, image) seem present.", None)
        else: # No twitter tags at all
            self._add_result(SEOResultLevel.INFO, "No Twitter Card Tags Found", "Twitter Card",
                             "No Twitter Card meta tags were found on the page.",
                             "Consider adding Twitter Card tags for optimized display and engagement when your content is shared on Twitter.")
            
        return {
            "open_graph_tags": og_tags,
            "twitter_card_tags": twitter_tags,
        }

    def _get_all_structured_data_info(self) -> Dict[str, Any]:
        """Detects and extracts various types of structured data (JSON-LD, Microdata, RDFa) and identified Schema.org types."""
        json_ld_data_list = self.get_json_ld_data() # Uses cached JSON-LD
        microdata_items_list = self.get_microdata() # Recalculates (or could be cached if made a getter)
        rdfa_items_list = self.get_rdfa_data()       # Recalculates (or could be cached if made a getter)
        
        detected_schema_types: List[str] = []
        # Extract types from JSON-LD
        for item_group_or_dict in json_ld_data_list:
            # JSON-LD can be a single dict or a list of dicts (e.g. @graph)
            items_to_check = [item_group_or_dict] if isinstance(item_group_or_dict, dict) else item_group_or_dict
            if isinstance(items_to_check, list): # Ensure it's iterable list of dicts
                for item_dict in items_to_check:
                    if isinstance(item_dict, dict):
                        type_val = item_dict.get('@type')
                        if isinstance(type_val, str):
                            detected_schema_types.append(type_val)
                        elif isinstance(type_val, list): # @type can be an array of types
                            detected_schema_types.extend(str(t) for t in type_val if isinstance(t, str))
        
        # Extract types from Microdata (itemtype)
        for md_item in microdata_items_list:
            item_type = md_item.get('type') # This is the itemtype URL
            if item_type and isinstance(item_type, str) and item_type != "[No Type Declared]":
                 # Typically, we'd want the last part of the schema.org URL, e.g., "Product" from "http://schema.org/Product"
                 parsed_type = urlparse(item_type)
                 if parsed_type.path:
                     detected_schema_types.append(parsed_type.path.split('/')[-1])


        # Extract types from RDFa (typeof) - similar to Microdata
        for rdf_item in rdfa_items_list:
            item_type = rdf_item.get('type') # This is the typeof CURIE or URL
            if item_type and isinstance(item_type, str) and item_type != "[No Type Declared]":
                # RDFa types can be CURIEs (e.g., "schema:Product") or full URLs
                if ':' in item_type and not item_type.startswith('http'): # Likely a CURIE
                    detected_schema_types.append(item_type.split(':')[-1])
                else: # Assume URL
                    parsed_type = urlparse(item_type)
                    if parsed_type.path:
                        detected_schema_types.append(parsed_type.path.split('/')[-1])
            
        unique_schema_types = sorted(list(set(s_type.strip() for s_type in detected_schema_types if s_type.strip())))

        if not json_ld_data_list and not microdata_items_list and not rdfa_items_list:
            self._add_result(SEOResultLevel.INFO, "No Common Structured Data Detected", "Structured Data",
                             "No common structured data formats (JSON-LD, Microdata, RDFa) were found on the page.",
                             "Consider adding structured data (Schema.org markup, typically via JSON-LD) to help search engines understand your content better and potentially enable rich results in SERPs.")
        else:
            if json_ld_data_list:
                 self._add_result(SEOResultLevel.GOOD, "JSON-LD Data Found", "Structured Data (JSON-LD)",
                                 f"{len(json_ld_data_list)} JSON-LD script block(s) or top-level objects detected.",
                                 "Review the detected JSON-LD data for correctness, completeness, and opportunities for richer data representation according to Schema.org guidelines.")
            if microdata_items_list:
                 self._add_result(SEOResultLevel.INFO, "Microdata Found", "Structured Data (Microdata)",
                                 f"{len(microdata_items_list)} Microdata item(s) detected within the HTML.",
                                 "Microdata is present. While still supported, JSON-LD is now more commonly recommended by Google for new implementations of Schema.org markup.")
            if rdfa_items_list:
                 self._add_result(SEOResultLevel.INFO, "RDFa Data Found", "Structured Data (RDFa)",
                                 f"{len(rdfa_items_list)} RDFa item(s) (elements with 'typeof') detected.",
                                 "RDFa is present. Similar to Microdata, JSON-LD is often the preferred method for implementing Schema.org due to ease of management.")

        return {
            "json_ld_data_blocks": json_ld_data_list,
            "microdata_items": microdata_items_list,
            "rdfa_items": rdfa_items_list,
            "detected_schema_org_types": unique_schema_types, # Consolidates types from all sources
        }

    def _calculate_seo_health_score(self) -> Dict[str, Any]:
        """Calculates an overall SEO health score based on the severity of identified issues."""
        score: int = 100
        critical_issues: int = 0
        error_issues: int = 0
        warning_issues: int = 0

        for result in self._results:
            if result.level == SEOResultLevel.CRITICAL:
                score -= 10 # Higher penalty for critical issues
                critical_issues += 1
            elif result.level == SEOResultLevel.ERROR:
                score -= 5  # Medium penalty for errors
                error_issues += 1
            elif result.level == SEOResultLevel.WARNING:
                score -= 2  # Lower penalty for warnings
                warning_issues += 1
        
        score = max(0, score) # Ensure score doesn't go below 0
        
        return {
            "score": score,
            "total_issues_found": critical_issues + error_issues + warning_issues,
            "critical_issues_count": critical_issues,
            "error_issues_count": error_issues,
            "warning_issues_count": warning_issues,
        }

    def _get_all_actionable_recommendations(self) -> List[str]:
        """Extracts all unique, actionable recommendations from high-severity analysis results."""
        # Only include recommendations for WARNING, ERROR, CRITICAL issues
        unique_recommendations: Set[str] = set()
        for res in self._results:
            if res.recommendation and res.level.value >= SEOResultLevel.WARNING.value:
                unique_recommendations.add(res.recommendation)
        return sorted(list(unique_recommendations)) # Return as a sorted list

    def _calculate_text_to_html_ratio(self) -> float:
        """Calculates the ratio of textual content length to total HTML source length."""
        text_content_length = len(self.get_main_content_text()) # Uses cached content
        html_source_length = len(self.html_content)
        if html_source_length == 0:
            return 0.0
        return round((text_content_length / html_source_length) * 100, 2)

    def _calculate_keyword_density(self, text: str, top_n: int = 10) -> Dict[str, float]:
        """
        Calculates keyword density for top N single words and bigrams from the provided text.
        Excludes common stop words and words shorter than KEYWORD_DENSITY_MIN_WORD_LEN.
        Only includes terms with density >= KEYWORD_DENSITY_MIN_THRESHOLD_PERCENT.
        """
        if not text or not text.strip():
            return {}

        text_lower = text.lower()
        # Improved regex for word tokenization, handles hyphens and apostrophes within words.
        words = re.findall(r'\b[a-z0-9]+(?:[-’\'][a-z0-9]+)*[a-z0-9]*\b', text_lower)
        
        # Filter by minimum length and exclude stop words
        filtered_single_words = [
            w for w in words 
            if len(w) >= self.KEYWORD_DENSITY_MIN_WORD_LEN and w not in self.STOP_WORDS
        ]
        
        if not filtered_single_words: # If no meaningful single words, cannot calculate density
            return {}

        # Generate bigrams from the filtered single words for more contextual phrases
        # Ensure there are at least two words to form a bigram
        bigrams = [' '.join(bg_pair) for bg_pair in zip(filtered_single_words, filtered_single_words[1:])]
        
        # Combine single filtered words and generated bigrams for frequency counting
        terms_to_count = filtered_single_words + bigrams
        if not terms_to_count: # Should not happen if filtered_single_words is not empty
            return {}
            
        # Base the density calculation on the count of single, filtered words.
        # This provides a more stable denominator than using the count of combined terms.
        base_denominator_for_density = len(filtered_single_words)
        
        term_frequencies = defaultdict(int)
        for term in terms_to_count:
            term_frequencies[term] += 1
            
        keyword_density_results: Dict[str, float] = {}
        for term, count in term_frequencies.items():
            # Density = (Occurrences of Term / Total Meaningful Single Words) * 100
            density_percentage = (count / base_denominator_for_density) * 100
            # Compare density percentage directly with the threshold percentage
            if density_percentage >= self.KEYWORD_DENSITY_MIN_THRESHOLD_PERCENT:
                 keyword_density_results[term] = round(density_percentage, 2)
        
        # Sort the results by density (descending) then by term (alphabetically ascending for ties)
        # and then take the top_n if needed. Current logic returns all above threshold.
        # If top_n is desired for the final list of terms meeting the threshold:
        sorted_results_by_density = sorted(keyword_density_results.items(), key=lambda item: (-item[1], item[0]))
        return dict(sorted_results_by_density[:top_n]) # Return top_n of those terms meeting the threshold
        # return keyword_density_results # Or return all terms meeting the density threshold without top_n cut-off


    def _count_syllables_in_word(self, word: str) -> int:
        """Estimates the number of syllables in a given word. (Simplified heuristic)."""
        word = word.lower().strip()
        if not word: return 0
        
        # Simple cases
        if len(word) <= 3: return 1 # e.g. "the", "cat", "dog"

        # Remove common suffixes that don't usually add a syllable if preceded by a vowel sound
        # Be careful with these rules, as they can be oversimplified.
        if word.endswith(('es', 'ed')) and len(word) > 4 :
             # if word ends with 'tes' or 'des', like 'tested', 'fades'
             if word[-3] in 'tds': # and if the letter before 'es' or 'ed' is t, d, or s
                 # check if removing 'es'/'ed' leaves a valid word part with vowels
                 temp_word = word[:-2]
                 if len(re.findall(r'[aeiouy]+', temp_word)) > 0:
                     word = temp_word
        elif word.endswith('e') and not word.endswith('le'): # silent 'e'
            # only remove if not the only vowel and not 'le'
            if len(re.findall(r'[aeiouy]+', word[:-1])) > 0:
                word = word[:-1]
        
        vowel_groups = re.findall(r'[aeiouy]+', word) # Find groups of consecutive vowels
        syllable_count = len(vowel_groups)

        # Adjustment for words ending in 'le' if preceded by a consonant
        if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
            # check if 'le' was already counted as part of a vowel group ending in 'e'
            if not (len(vowel_groups)>0 and vowel_groups[-1].endswith('e') and word.endswith(vowel_groups[-1]+'le')):
                 syllable_count += 1
        
        return max(1, syllable_count) # Ensure at least one syllable for any word

    def _calculate_flesch_reading_ease(self, text: str) -> float:
        """Calculates the Flesch Reading Ease score for the provided text."""
        if not text or not text.strip(): # Check for empty or whitespace-only text
            logger.debug("Flesch: Input text is empty.")
            return 0.0

        # Simple sentence tokenization: split by common sentence-ending punctuation.
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        # Word tokenization: find sequences of alphanumeric characters (basic).
        words = re.findall(r'\b\w+\b', text)

        num_sentences = len(sentences)
        num_words = len(words)
        
        if num_sentences == 0 or num_words < 5: # Need some words and sentences for meaningful score
            logger.debug(f"Flesch: Insufficient sentences ({num_sentences}) or words ({num_words}) for reliable score.")
            return 0.0

        num_syllables = sum(self._count_syllables_in_word(word) for word in words)
        # If syllable count is zero for all words (highly unlikely for num_words > 0 but possible with flawed syllable counter)
        if num_syllables == 0 and num_words > 0 :
            logger.warning(f"Flesch: Syllable count resulted in zero for {num_words} words. Readability score may be inaccurate.")
            return 0.0 # Or handle as error / undefined

        try:
            # Flesch Reading Ease formula:
            # Score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
            score = 206.835 - (1.015 * (num_words / num_sentences)) - (84.6 * (num_syllables / num_words))
        except ZeroDivisionError: # Should be caught by earlier checks, but as a final safeguard
            logger.error("Flesch: ZeroDivisionError during score calculation despite initial checks.")
            return 0.0
            
        # Clamp score to typical 0-100 range
        return round(max(0.0, min(100.0, score)), 1)

    def _calculate_anchor_text_distribution(self, links: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyzes and categorizes the anchor texts of the provided links."""
        # Filter out links that have "[No Anchor Text]" or are effectively empty
        anchor_texts_data = [
            link['text'] for link in links 
            if link.get('text') and link['text'] != "[No Anchor Text]" and link['text'].strip()
        ]
        total_valid_anchor_texts = len(anchor_texts_data)
        
        if total_valid_anchor_texts == 0:
            return {}

        distribution: Dict[str, int] = defaultdict(int)
        generic_anchors_lower = {
            'click here', 'read more', 'learn more', 'here', 'more', 'link', 
            'this link', 'website', 'this', 'continue reading', 'details'
        }
        
        page_domain_main_part = None
        if self.url and self._is_valid_url(self.url):
            try:
                parsed_url = urlparse(self.url)
                # Extract main part of the domain, e.g., "example" from "www.example.com"
                domain_parts = parsed_url.netloc.replace('www.', '', 1).split('.')
                if domain_parts and len(domain_parts) > 0:
                    # Heuristic: take the part before the TLD (e.g., "example" from "example.co.uk")
                    page_domain_main_part = domain_parts[0].lower()
            except Exception as e:
                logger.debug(f"Could not parse page domain from URL '{self.url}' for branded anchor text check: {e}")

        for text_content in anchor_texts_data:
            text_lower_stripped = text_content.lower().strip()
            # Categorization logic
            if text_lower_stripped in generic_anchors_lower:
                distribution['generic'] += 1
            elif page_domain_main_part and page_domain_main_part in text_lower_stripped:
                distribution['branded'] += 1
            # Heuristic for keyword-like (short, specific phrases)
            elif len(text_lower_stripped.split()) <= 3 and len(text_lower_stripped) <= 30:
                distribution['keyword_like_or_short_phrase'] += 1
            else: # Longer phrases, likely descriptive
                distribution['descriptive_long_phrase'] += 1
        
        # Convert counts to percentages
        return {
            key: round((count / total_valid_anchor_texts) * 100, 1) 
            for key, count in distribution.items()
        }

    def _make_absolute_url(self, href: Optional[str]) -> Optional[str]:
        """
        Converts a relative HREFeference to an absolute URL.
        Considers the page's <base href="..."> tag if present, otherwise uses self.url.
        Handles various edge cases in URL resolution.
        """
        if not href or not href.strip(): # Handles None, empty string, or whitespace-only string
            return None
        
        href_stripped = href.strip()
        
        # If href is already absolute (has a scheme like http, https) or another scheme (mailto, tel)
        parsed_href = urlparse(href_stripped)
        if parsed_href.scheme:
            if parsed_href.scheme in ['http', 'https'] and parsed_href.netloc:
                return href_stripped # Already a full HTTP/HTTPS URL
            elif parsed_href.scheme not in ['http', 'https']:
                return href_stripped # Other schemes like mailto:, tel:, ftp:, file:
            # Else, scheme is http/https but no netloc (e.g., "http:") - treat as relative or invalid.

        # Determine the base URL to use for joining
        base_tag = self.soup.find('base', href=True)
        effective_base_url: Optional[str] = None

        if base_tag and base_tag.get('href'):
            base_tag_href_stripped = base_tag['href'].strip()
            if not base_tag_href_stripped: # <base href=""> or <base href=" ">
                logger.debug(f"<base> tag found with empty or whitespace-only href. Using page URL ('{self.url}') as base if available and valid.")
                effective_base_url = self.url if self.url and self._is_valid_url(self.url) else None
            else:
                parsed_base_tag_href = urlparse(base_tag_href_stripped)
                if parsed_base_tag_href.scheme and parsed_base_tag_href.netloc: # <base> href is absolute
                    effective_base_url = base_tag_href_stripped
                elif self.url and self._is_valid_url(self.url): # <base> href is relative, requires valid self.url
                    try:
                        effective_base_url = urljoin(self.url, base_tag_href_stripped)
                    except ValueError as e:
                        logger.warning(f"Error joining page URL ('{self.url}') with <base> href ('{base_tag_href_stripped}'): {e}. Falling back to page URL if valid.")
                        effective_base_url = self.url # Fallback to page URL
                else: # <base> href is relative, but no valid self.url to resolve it against
                     logger.warning(f"<base> href ('{base_tag_href_stripped}') is relative, but no valid page URL (self.url) provided to resolve it. Cannot make '{href_stripped}' absolute using this <base> tag.")
                     effective_base_url = None # Cannot form an absolute base from this <base> tag
        elif self.url and self._is_valid_url(self.url): # No <base> tag, use self.url if valid
            effective_base_url = self.url
        
        if not effective_base_url: # Still no valid base_url to join with
             logger.debug(f"Could not determine an effective base URL for joining with '{href_stripped}'. Returning as is if root-relative, else None.")
             # If href is root-relative (e.g., "/path/to/page.html"), it implies domain of effective_base_url.
             # Without effective_base_url, it's not truly absolute.
             return href_stripped if href_stripped.startswith('/') else None

        try:
            # urljoin correctly handles:
            # - joining a relative path (href_stripped) with an absolute base (effective_base_url)
            # - returning href_stripped if it's already absolute (http/https)
            absolute_url = urljoin(effective_base_url, href_stripped)
            return absolute_url
        except ValueError as e: # Should be rare if effective_base_url and href_stripped are reasonable strings
            logger.error(f"URL joining failed using base '{effective_base_url}' and href '{href_stripped}': {e}")
            return None # Or return href_stripped as a last resort if it seems plausible

    def _is_internal_url(self, url_to_check: Optional[str]) -> bool:
        """
        Determines if a given URL is internal relative to the page's effective base URL (self.url).
        A URL is considered internal if its domain matches the domain of self.url, or if it's a relative path.
        """
        # The "internality" should primarily be judged against the original page's domain (self.url),
        # not necessarily the <base> tag's domain, as the <base> tag only affects resolution of relative paths.
        # An absolute link to "another-domain.com" is external even if <base href="another-domain.com"> exists.
        
        if not self.url or not url_to_check or not self._is_valid_url(self.url):
            # Cannot determine internality if base page URL is missing/invalid or URL to check is missing
            if not url_to_check or not urlparse(url_to_check).scheme : # If url_to_check looks relative, assume internal if no base context
                 logger.debug(f"Assuming relative-looking URL '{url_to_check}' is internal due to missing/invalid base page URL context.")
                 return True
            return False

        try:
            base_parsed = urlparse(self.url)
            target_parsed = urlparse(url_to_check)
            
            # Normalize domains: remove 'www.' prefix and convert to lowercase for comparison
            norm_base_domain = base_parsed.netloc.replace('www.', '', 1).lower()
            norm_target_domain = target_parsed.netloc.replace('www.', '', 1).lower()

            # If target_parsed has no netloc, it means it's a relative path (e.g., "/page.html", "image.jpg")
            # Such paths are always resolved relative to some base, and thus considered internal to that base.
            if not target_parsed.netloc:
                return True 
            
            # If target_parsed has a netloc, compare it to the base_parsed netloc
            return norm_target_domain == norm_base_domain
        except Exception as e: # Broad exception for any URL parsing issues
            logger.error(f"Error comparing URLs for internality ('{self.url}', '{url_to_check}'): {e}")
            return False # Default to not internal on error
