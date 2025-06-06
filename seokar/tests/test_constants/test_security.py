import pytest
from seokar.constants.security import SecurityHeaders, RecommendedSecurityValues


def test_security_headers_constants():
    """Tests the values of constants in SecurityHeaders."""
    assert SecurityHeaders.STRICT_TRANSPORT_SECURITY == "Strict-Transport-Security"
    assert SecurityHeaders.CONTENT_SECURITY_POLICY == "Content-Security-Policy"
    assert SecurityHeaders.X_CONTENT_TYPE_OPTIONS == "X-Content-Type-Options"
    assert SecurityHeaders.X_FRAME_OPTIONS == "X-Frame-Options"
    assert SecurityHeaders.REFERRER_POLICY == "Referrer-Policy"
    assert SecurityHeaders.PERMISSIONS_POLICY == "Permissions-Policy"


def test_recommended_security_values_constants():
    """Tests the values of constants in RecommendedSecurityValues."""
    assert RecommendedSecurityValues.HSTS_MIN_AGE == 31536000
    assert RecommendedSecurityValues.X_CONTENT_TYPE_OPTIONS_VALUE == "nosniff"
    assert RecommendedSecurityValues.X_FRAME_OPTIONS_VALUE == "DENY"
    assert RecommendedSecurityValues.REFERRER_POLICY_VALUE == "no-referrer-when-downgrade"
    assert RecommendedSecurityValues.CSP_RECOMMENDED_DIRECTIVES == ["default-src 'self'", "script-src 'self'", "img-src 'self' data:", "style-src 'self' 'unsafe-inline'"]
