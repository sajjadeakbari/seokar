class SchemaTypes:
    """Common Schema.org types relevant for SEO."""
    WEBPAGE: str = "WebPage"
    ARTICLE: str = "Article"
    PRODUCT: str = "Product"
    ORGANIZATION: str = "Organization"
    LOCAL_BUSINESS: str = "LocalBusiness"
    BREADCRUMBLIST: str = "BreadcrumbList"
    REVIEW: str = "Review"
    FAQPAGE: str = "FAQPage"


class SchemaProperties:
    """Common Schema.org properties."""
    NAME: str = "name"
    DESCRIPTION: str = "description"
    IMAGE: str = "image"
    URL: str = "url"
    AUTHOR: str = "author"
    PUBLISH_DATE: str = "datePublished"
    REVIEW_COUNT: str = "reviewCount"
    AGGREGATE_RATING: str = "aggregateRating"


class SchemaUrls:
    """Base URLs for Schema.org and JSON-LD contexts."""
    SCHEMA_ORG_BASE: str = "http://schema.org/"
    JSON_LD_CONTEXT: str = "https://schema.org"
