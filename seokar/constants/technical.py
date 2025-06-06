class CoreWebVitals:
    """Thresholds for Core Web Vitals metrics."""
    LCP_GOOD: float = 2.5  # seconds
    LCP_NEEDS_IMPROVEMENT: float = 4.0  # seconds
    CLS_GOOD: float = 0.1
    CLS_NEEDS_IMPROVEMENT: float = 0.25
    INP_GOOD: float = 200  # milliseconds
    INP_NEEDS_IMPROVEMENT: float = 500  # milliseconds


class PageSpeed:
    """Thresholds and limits for page performance metrics."""
    GOOD_LOADING_TIME_MS: float = 1000  # milliseconds
    ACCEPTABLE_LOADING_TIME_MS: float = 3000  # milliseconds
    MAX_PAGE_SIZE_BYTES: int = 300 * 1024  # 300KB


class TechnicalIssues:
    """Standardized strings for common technical SEO issues."""
    MISSING_TITLE: str = "Missing Title"
    MISSING_META_DESCRIPTION: str = "Missing Meta Description"
    MULTIPLE_H1: str = "Multiple H1 Tags"
    NO_CANONICAL: str = "No Canonical URL"
    BROKEN_LINK: str = "Broken Internal Link"
    MISSING_ALT_TEXT: str = "Missing Alt Text on Image"
    HTTP_TO_HTTPS_REDIRECT: str = "HTTP to HTTPS Redirect Missing or Incorrect"
    MIXED_CONTENT: str = "Mixed Content (HTTP resources on HTTPS page)"
