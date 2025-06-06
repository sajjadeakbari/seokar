import pytest
from seokar.constants.schema import SchemaTypes, SchemaProperties, SchemaUrls


def test_schema_types_constants():
    """Tests the values of constants in SchemaTypes."""
    assert SchemaTypes.WEBPAGE == "WebPage"
    assert SchemaTypes.ARTICLE == "Article"
    assert SchemaTypes.PRODUCT == "Product"
    assert SchemaTypes.ORGANIZATION == "Organization"
    assert SchemaTypes.LOCAL_BUSINESS == "LocalBusiness"
    assert SchemaTypes.BREADCRUMBLIST == "BreadcrumbList"
    assert SchemaTypes.REVIEW == "Review"
    assert SchemaTypes.FAQPAGE == "FAQPage"


def test_schema_properties_constants():
    """Tests the values of constants in SchemaProperties."""
    assert SchemaProperties.NAME == "name"
    assert SchemaProperties.DESCRIPTION == "description"
    assert SchemaProperties.IMAGE == "image"
    assert SchemaProperties.URL == "url"
    assert SchemaProperties.AUTHOR == "author"
    assert SchemaProperties.PUBLISH_DATE == "datePublished"
    assert SchemaProperties.REVIEW_COUNT == "reviewCount"
    assert SchemaProperties.AGGREGATE_RATING == "aggregateRating"


def test_schema_urls_constants():
    """Tests the values of constants in SchemaUrls."""
    assert SchemaUrls.SCHEMA_ORG_BASE == "http://schema.org/"
    assert SchemaUrls.JSON_LD_CONTEXT == "https://schema.org"
