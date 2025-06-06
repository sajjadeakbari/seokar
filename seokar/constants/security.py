from typing import List


class SecurityHeaders:
    """Standard HTTP security header names relevant for SEO and web security."""
    STRICT_TRANSPORT_SECURITY: str = "Strict-Transport-Security"
    CONTENT_SECURITY_POLICY: str = "Content-Security-Policy"
    X_CONTENT_TYPE_OPTIONS: str = "X-Content-Type-Options"
    X_FRAME_OPTIONS: str = "X-Frame-Options"
    REFERRER_POLICY: str = "Referrer-Policy"
    PERMISSIONS_POLICY: str = "Permissions-Policy"


class RecommendedSecurityValues:
    """Recommended values and thresholds for HTTP security headers."""
    HSTS_MIN_AGE: int = 31536000  # 1 year in seconds
    X_CONTENT_TYPE_OPTIONS_VALUE: str = "nosniff"
    X_FRAME_OPTIONS_VALUE: str = "DENY"  # or SAMEORIGIN
    REFERRER_POLICY_VALUE: str = "no-referrer-when-downgrade"  # or strict-origin-when-cross-origin
    CSP_RECOMMENDED_DIRECTIVES: List[str] = ["default-src 'self'", "script-src 'self'", "img-src 'self' data:", "style-src 'self' 'unsafe-inline'"]
