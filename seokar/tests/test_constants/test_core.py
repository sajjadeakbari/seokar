import pytest
from seokar.constants.core import SeoLimits, StatusCode, RobotsTxt


def test_seo_limits_constants():
    """Tests the values of constants in SeoLimits."""
    assert SeoLimits.TITLE_MAX_LENGTH == 60
    assert SeoLimits.META_DESCRIPTION_MAX_LENGTH == 160
    assert SeoLimits.H1_MAX_COUNT == 1
    assert SeoLimits.BODY_MIN_WORD_COUNT == 300


def test_status_code_constants():
    """Tests the values of constants in StatusCode."""
    assert StatusCode.OK == 200
    assert StatusCode.MOVED_PERMANENTLY == 301
    assert StatusCode.FOUND == 302
    assert StatusCode.NOT_FOUND == 404
    assert StatusCode.FORBIDDEN == 403
    assert StatusCode.INTERNAL_SERVER_ERROR == 500


def test_robots_txt_constants():
    """Tests the values of constants in RobotsTxt."""
    assert RobotsTxt.ALLOWED == "allow"
    assert RobotsTxt.DISALLOWED == "disallow"
    assert RobotsTxt.NOINDEX == "noindex"
    assert RobotsTxt.NOFOLLOW == "nofollow"
