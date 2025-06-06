import pytest
from seokar.constants.local import LocalSeo, ContactInfo


def test_local_seo_constants():
    """Tests the values of constants in LocalSeo."""
    assert LocalSeo.NAP_CONSISTENCY_SCORE_THRESHOLD == 0.9
    assert LocalSeo.MIN_GOOGLE_BUSINESS_REVIEWS == 10
    assert LocalSeo.MIN_AVERAGE_RATING == 4.0
    assert LocalSeo.SCHEMA_LOCAL_BUSINESS_TYPES == ["LocalBusiness", "Organization", "Restaurant", "Store"]


def test_contact_info_constants():
    """Tests the values of constants in ContactInfo."""
    assert ContactInfo.PHONE_NUMBER_FORMAT_REGEX == r"^\+?\d{1,3}?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
    assert ContactInfo.EMAIL_FORMAT_REGEX == r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
