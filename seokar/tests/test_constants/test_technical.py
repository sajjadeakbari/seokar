import pytest
from seokar.constants.technical import CoreWebVitals, PageSpeed, TechnicalIssues


def test_core_web_vitals_constants():
    """Tests the values of constants in CoreWebVitals."""
    assert CoreWebVitals.LCP_GOOD == 2.5
    assert CoreWebVitals.LCP_NEEDS_IMPROVEMENT == 4.0
    assert CoreWebVitals.CLS_GOOD == 0.1
    assert CoreWebVitals.CLS_NEEDS_IMPROVEMENT == 0.25
    assert CoreWebVitals.INP_GOOD == 200
    assert CoreWebVitals.INP_NEEDS_IMPROVEMENT == 500


def test_page_speed_constants():
    """Tests the values of constants in PageSpeed."""
    assert PageSpeed.GOOD_LOADING_TIME_MS == 1000
    assert PageSpeed.ACCEPTABLE_LOADING_TIME_MS == 3000
    assert PageSpeed.MAX_PAGE_SIZE_BYTES == 300 * 1024


def test_technical_issues_constants():
    """Tests the values of constants in TechnicalIssues."""
    assert TechnicalIssues.MISSING_TITLE == "Missing Title"
    assert TechnicalIssues.MISSING_META_DESCRIPTION == "Missing Meta Description"
    assert TechnicalIssues.MULTIPLE_H1 == "Multiple H1 Tags"
    assert TechnicalIssues.NO_CANONICAL == "No Canonical URL"
    assert TechnicalIssues.BROKEN_LINK == "Broken Internal Link"
    assert TechnicalIssues.MISSING_ALT_TEXT == "Missing Alt Text on Image"
    assert TechnicalIssues.HTTP_TO_HTTPS_REDIRECT == "HTTP to HTTPS Redirect Missing or Incorrect"
    assert TechnicalIssues.MIXED_CONTENT == "Mixed Content (HTTP resources on HTTPS page)"
