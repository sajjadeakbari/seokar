from typing import List


class LocalSeo:
    """Constants and thresholds for Local SEO standards."""
    NAP_CONSISTENCY_SCORE_THRESHOLD: float = 0.9
    MIN_GOOGLE_BUSINESS_REVIEWS: int = 10
    MIN_AVERAGE_RATING: float = 4.0
    SCHEMA_LOCAL_BUSINESS_TYPES: List[str] = ["LocalBusiness", "Organization", "Restaurant", "Store"]


class ContactInfo:
    """Regular expressions for validating common contact information formats."""
    PHONE_NUMBER_FORMAT_REGEX: str = r"^\+?\d{1,3}?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
    EMAIL_FORMAT_REGEX: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
