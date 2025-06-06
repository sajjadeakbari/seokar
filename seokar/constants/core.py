class SeoLimits:
    """Core SEO recommended limits and thresholds."""
    TITLE_MAX_LENGTH: int = 60
    META_DESCRIPTION_MAX_LENGTH: int = 160
    H1_MAX_COUNT: int = 1
    BODY_MIN_WORD_COUNT: int = 300


class StatusCode:
    """Common HTTP status codes relevant to SEO."""
    OK: int = 200
    MOVED_PERMANENTLY: int = 301
    FOUND: int = 302
    NOT_FOUND: int = 404
    FORBIDDEN: int = 403
    INTERNAL_SERVER_ERROR: int = 500


class RobotsTxt:
    """Constants for robots.txt directives."""
    ALLOWED: str = "allow"
    DISALLOWED: str = "disallow"
    NOINDEX: str = "noindex"
    NOFOLLOW: str = "nofollow"
