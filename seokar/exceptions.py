class SeokarError(Exception):
    """Base exception for all custom Seokar errors."""
    pass


class SeokarHTTPError(SeokarError):
    """Exception for HTTP-related errors within the Seokar library."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
