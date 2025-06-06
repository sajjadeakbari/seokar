import pytest
from datetime import datetime, timedelta
import json
from unittest.mock import patch

from seokar.models import CoreWebVitalsMetrics, ContentMetrics, SEOResult, SEOSummaryReport


@pytest.fixture
def sample_core_web_vitals_metrics():
    """Provides a sample CoreWebVitalsMetrics instance."""
    return CoreWebVitalsMetrics(lcp=2.1, cls=0.05, inp=150.0)


@pytest.fixture
def sample_content_metrics():
    """Provides a sample ContentMetrics instance."""
    return ContentMetrics(
        word_count=750,
        readability_score=68.5,
        keyword_density={"seo": 0.015, "analysis": 0.007}
    )


@pytest.fixture
def sample_seo_result(sample_core_web_vitals_metrics, sample_content_metrics):
    """Provides a fully populated SEOResult instance."""
    return SEOResult(
        url="https://www.example.com/test-page",
        status_code=200,
        page_size_bytes=150000,
        loading_time_ms=850.5,
        title="Sample SEO Result Page Title",
        meta_description="This is a sample meta description for the SEO result.",
        h1_tags=["Main Heading", "Secondary Heading"],
        canonical_url="https://www.example.com/test-page-canonical",
        robots_tag="index, follow",
        technical_issues=["Missing Alt Text", "Broken Internal Link"],
        security_headers={"Strict-Transport-Security": "max-age=31536000"},
        schema_present=True,
        core_web_vitals=sample_core_web_vitals_metrics,
        content_metrics=sample_content_metrics,
        analysis_timestamp=datetime(2023, 1, 15, 10, 30, 0)
    )


@pytest.fixture
def sample_seo_result_partial():
    """Provides a partially populated SEOResult instance with None values."""
    return SEOResult(
        url="https://www.example.com/partial-data",
        status_code=404,
        title="Page Not Found",
        meta_description=None,  # This should be omitted in to_dict
        h1_tags=[],
        canonical_url=None,  # This should be omitted in to_dict
        technical_issues=["Missing Meta Description", "No Canonical URL"],
        security_headers={},
        schema_present=False,
        core_web_vitals=None,  # This should be omitted in to_dict
        content_metrics=None,  # This should be omitted in to_dict
        analysis_timestamp=datetime(2023, 1, 16, 11, 0, 0)
    )


def test_core_web_vitals_metrics_init():
    """Test CoreWebVitalsMetrics initialization."""
    metrics = CoreWebVitalsMetrics()
    assert metrics.lcp is None
    assert metrics.cls is None
    assert metrics.inp is None

    metrics_full = CoreWebVitalsMetrics(lcp=2.0, cls=0.1, inp=250.0)
    assert metrics_full.lcp == 2.0
    assert metrics_full.cls == 0.1
    assert metrics_full.inp == 250.0


def test_content_metrics_init():
    """Test ContentMetrics initialization."""
    metrics = ContentMetrics()
    assert metrics.word_count is None
    assert metrics.readability_score is None
    assert metrics.keyword_density == {}

    metrics_full = ContentMetrics(word_count=500, readability_score=70.0, keyword_density={"test": 0.01})
    assert metrics_full.word_count == 500
    assert metrics_full.readability_score == 70.0
    assert metrics_full.keyword_density == {"test": 0.01}


def test_seo_result_init(sample_seo_result):
    """Test SEOResult initialization with full data."""
    result = sample_seo_result
    assert result.url == "https://www.example.com/test-page"
    assert result.status_code == 200
    assert result.page_size_bytes == 150000
    assert result.loading_time_ms == 850.5
    assert result.title == "Sample SEO Result Page Title"
    assert result.meta_description == "This is a sample meta description for the SEO result."
    assert result.h1_tags == ["Main Heading", "Secondary Heading"]
    assert result.canonical_url == "https://www.example.com/test-page-canonical"
    assert result.robots_tag == "index, follow"
    assert result.technical_issues == ["Missing Alt Text", "Broken Internal Link"]
    assert result.security_headers == {"Strict-Transport-Security": "max-age=31536000"}
    assert result.schema_present is True
    assert result.core_web_vitals.lcp == 2.1
    assert result.content_metrics.word_count == 750
    assert result.analysis_timestamp == datetime(2023, 1, 15, 10, 30, 0)

    # Test default analysis_timestamp
    with patch('seokar.models.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 2, 1, 12, 0, 0)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs) # Ensure constructor calls original datetime
        default_timestamp_result = SEOResult(url="http://example.com", status_code=200)
        assert default_timestamp_result.analysis_timestamp == datetime(2023, 2, 1, 12, 0, 0)


def test_seo_result_to_dict_full_data(sample_seo_result):
    """Test SEOResult.to_dict() with all fields populated."""
    result_dict = sample_seo_result.to_dict()

    assert isinstance(result_dict, dict)
    assert result_dict["url"] == "https://www.example.com/test-page"
    assert result_dict["status_code"] == 200
    assert result_dict["page_size_bytes"] == 150000
    assert result_dict["loading_time_ms"] == 850.5
    assert result_dict["title"] == "Sample SEO Result Page Title"
    assert result_dict["meta_description"] == "This is a sample meta description for the SEO result."
    assert result_dict["h1_tags"] == ["Main Heading", "Secondary Heading"]
    assert result_dict["canonical_url"] == "https://www.example.com/test-page-canonical"
    assert result_dict["robots_tag"] == "index, follow"
    assert result_dict["technical_issues"] == ["Missing Alt Text", "Broken Internal Link"]
    assert result_dict["security_headers"] == {"Strict-Transport-Security": "max-age=31536000"}
    assert result_dict["schema_present"] is True

    # Check nested dataclasses
    assert result_dict["core_web_vitals"]["lcp"] == 2.1
    assert result_dict["core_web_vitals"]["cls"] == 0.05
    assert result_dict["core_web_vitals"]["inp"] == 150.0

    assert result_dict["content_metrics"]["word_count"] == 750
    assert result_dict["content_metrics"]["readability_score"] == 68.5
    assert result_dict["content_metrics"]["keyword_density"] == {"seo": 0.015, "analysis": 0.007}

    # Ensure analysis_timestamp is present and correctly formatted (though type is datetime, not str)
    assert isinstance(result_dict["analysis_timestamp"], datetime)
    assert result_dict["analysis_timestamp"] == datetime(2023, 1, 15, 10, 30, 0)

    # Ensure no None values are present
    assert None not in json.dumps(result_dict) # Simple way to check recursively for None


def test_seo_result_to_dict_partial_data(sample_seo_result_partial):
    """Test SEOResult.to_dict() with some fields as None."""
    result_dict = sample_seo_result_partial.to_dict()

    assert isinstance(result_dict, dict)
    assert result_dict["url"] == "https://www.example.com/partial-data"
    assert result_dict["status_code"] == 404
    assert result_dict["title"] == "Page Not Found"
    assert result_dict["h1_tags"] == []
    assert result_dict["technical_issues"] == ["Missing Meta Description", "No Canonical URL"]
    assert result_dict["security_headers"] == {}
    assert result_dict["schema_present"] is False

    # Assert None fields are NOT present
    assert "meta_description" not in result_dict
    assert "canonical_url" not in result_dict
    assert "core_web_vitals" not in result_dict
    assert "content_metrics" not in result_dict
    assert "page_size_bytes" not in result_dict
    assert "loading_time_ms" not in result_dict

    # Check that lists and dicts that are empty are kept (not None)
    assert result_dict["h1_tags"] == []
    assert result_dict["security_headers"] == {}


def test_seo_result_to_markdown(sample_seo_result):
    """Test SEOResult.to_markdown() produces a well-formatted report."""
    markdown_report = sample_seo_result.to_markdown()

    assert isinstance(markdown_report, str)
    assert "# SEO Analysis Report: https://www.example.com/test-page" in markdown_report
    assert "Analysis Timestamp: 2023-01-15 10:30:00" in markdown_report
    assert "## General Information" in markdown_report
    assert "- **Status Code:** `200`" in markdown_report
    assert "- **Page Size:** 146.48 KB" in markdown_report
    assert "- **Loading Time:** 850.50 ms" in markdown_report
    assert "## SEO Elements" in markdown_report
    assert "- **Title:** Sample SEO Result Page Title" in markdown_report
    assert "- **Meta Description:** This is a sample meta description for the SEO result." in markdown_report
    assert "- **H1 Tags:** Main Heading, Secondary Heading" in markdown_report
    assert "- **Canonical URL:** https://www.example.com/test-page-canonical" in markdown_report
    assert "- **Robots Tag:** index, follow" in markdown_report
    assert "- **Schema Present:** Yes" in markdown_report
    assert "## Technical Issues" in markdown_report
    assert "- Missing Alt Text" in markdown_report
    assert "- Broken Internal Link" in markdown_report
    assert "## Security Headers" in markdown_report
    assert "- **Strict-Transport-Security:** `max-age=31536000`" in markdown_report
    assert "## Core Web Vitals" in markdown_report
    assert "- **LCP (Largest Contentful Paint):** 2.10 s" in markdown_report
    assert "- **CLS (Cumulative Layout Shift):** 0.050" in markdown_report
    assert "- **INP (Interaction to Next Paint):** 150.00 ms" in markdown_report
    assert "## Content Metrics" in markdown_report
    assert "- **Word Count:** 750" in markdown_report
    assert "- **Readability Score:** 68.50" in markdown_report
    assert "- **Keyword Density:**" in markdown_report
    assert "  - `seo`: 1.50%" in markdown_report
    assert "  - `analysis`: 0.70%" in markdown_report


def test_seo_summary_report_init(sample_seo_result, sample_seo_result_partial):
    """Test SEOSummaryReport initialization."""
    results = [sample_seo_result, sample_seo_result_partial]
    report = SEOSummaryReport(results=results, overall_score=85.0)

    assert report.results == results
    assert report.total_pages_analyzed == 2
    assert report.overall_score == 85.0
    assert isinstance(report.report_timestamp, datetime)

    # Test with default results list
    empty_report = SEOSummaryReport()
    assert empty_report.results == []
    assert empty_report.total_pages_analyzed == 0
    assert empty_report.overall_score is None


def test_seo_summary_report_to_dict(sample_seo_result):
    """Test SEOSummaryReport.to_dict()."""
    # Create a couple of results to ensure the list is handled
    result1 = SEOResult(url="url1", status_code=200, title="Title 1")
    result2 = SEOResult(url="url2", status_code=404, title="Title 2")
    results = [result1, result2]
    
    report_timestamp = datetime(2023, 3, 1, 9, 0, 0)
    report = SEOSummaryReport(results=results, overall_score=90.0, report_timestamp=report_timestamp)
    summary_dict = report.to_dict()

    assert isinstance(summary_dict, dict)
    assert len(summary_dict["results"]) == 2
    assert summary_dict["results"][0]["url"] == "url1"
    assert summary_dict["results"][1]["status_code"] == 404
    assert summary_dict["total_pages_analyzed"] == 2
    assert summary_dict["overall_score"] == 90.0
    assert summary_dict["report_timestamp"] == report_timestamp

    # Test with no results
    empty_report = SEOSummaryReport()
    empty_summary_dict = empty_report.to_dict()
    assert empty_summary_dict["total_pages_analyzed"] == 0
    assert empty_summary_dict["results"] == []


def test_seo_summary_report_to_markdown():
    """Test SEOSummaryReport.to_markdown() produces a summarized report."""
    result1 = SEOResult(
        url="https://good.com",
        status_code=200,
        page_size_bytes=100000,
        loading_time_ms=500.0,
        title="Good Page",
        meta_description="Good meta",
        h1_tags=["H1"],
        technical_issues=[],
        security_headers={"Strict-Transport-Security": "present"},
        schema_present=True,
        core_web_vitals=CoreWebVitalsMetrics(lcp=1.0, cls=0.01, inp=100.0),
        content_metrics=ContentMetrics(word_count=600, readability_score=70.0, keyword_density={"good": 0.01}),
        analysis_timestamp=datetime(2023, 4, 1, 10, 0, 0)
    )
    result2 = SEOResult(
        url="https://bad.com",
        status_code=404, # Will not be explicitly counted in technical issues
        page_size_bytes=400000, # Too large
        loading_time_ms=4000.0, # Slow
        title=None, # Missing
        meta_description=None, # Missing
        h1_tags=["H1 A", "H1 B"], # Multiple
        canonical_url=None, # No canonical
        robots_tag="noindex", # Noindex
        technical_issues=["Missing Alt Text", "Page Size Too Large"],
        security_headers={},
        schema_present=False,
        core_web_vitals=CoreWebVitalsMetrics(lcp=3.0, cls=0.3, inp=600.0), # Needs improvement/bad
        content_metrics=ContentMetrics(word_count=200, readability_score=40.0, keyword_density={}), # Low word count, bad readability
        analysis_timestamp=datetime(2023, 4, 1, 10, 10, 0)
    )
    result3 = SEOResult(
        url="https://mixed.com",
        status_code=200,
        page_size_bytes=150000,
        loading_time_ms=1500.0, # Acceptable
        title="Mixed Content Page",
        meta_description="Mixed content example",
        h1_tags=["H1"],
        canonical_url="https://mixed.com",
        robots_tag="index, follow",
        technical_issues=["Mixed Content (HTTP resources on HTTPS page)"], # Mixed content
        security_headers={"X-Content-Type-Options": "nosniff"},
        schema_present=True,
        core_web_vitals=CoreWebVitalsMetrics(lcp=2.0, cls=0.05, inp=180.0),
        content_metrics=ContentMetrics(word_count=800, readability_score=65.0, keyword_density={"mixed": 0.005}),
        analysis_timestamp=datetime(2023, 4, 1, 10, 20, 0)
    )

    results = [result1, result2, result3]
    report_timestamp = datetime(2023, 4, 1, 11, 0, 0)
    summary_report = SEOSummaryReport(results=results, overall_score=75.0, report_timestamp=report_timestamp)
    markdown_output = summary_report.to_markdown()

    assert isinstance(markdown_output, str)
    assert "# Seokar Summary Report" in markdown_output
    assert "Report Timestamp: 2023-04-01 11:00:00" in markdown_output
    assert "## General Summary" in markdown_output
    assert "- **Total Pages Analyzed:** 3" in markdown_output
    assert "- **Overall Score:** 75.00" in markdown_output

    assert "## Performance Summary" in markdown_output
    assert "- **Average Loading Time:** 2000.00 ms" in markdown_output # (500+4000+1500)/3 = 2000
    assert "- **Average LCP:** 2.00 s" in markdown_output # (1+3+2)/3 = 2
    assert "- **Average CLS:** 0.127" in markdown_output # (0.01+0.3+0.05)/3 = 0.12
    assert "- **Average INP:** 293.33 ms" in markdown_output # (100+600+180)/3 = 293.33

    assert "## Content Summary" in markdown_output
    assert "- **Average Word Count:** 533" in markdown_output # (600+200+800)/3 = 533.33
    assert "- **Average Readability Score:** 58.00" in markdown_output # (70+40+65)/3 = 58.33

    assert "## SEO Elements Summary" in markdown_output
    assert "- **Pages with Missing Title:** 1" in markdown_output
    assert "- **Pages with Missing Meta Description:** 1" in markdown_output
    assert "- **Pages with Multiple H1s:** 1" in markdown_output
    assert "- **Pages with Schema Present:** 2" in markdown_output

    assert "## Technical Overview" in markdown_output
    assert "- **Common Technical Issues:**" in markdown_output
    assert "  - Page Size Too Large: 1 pages" in markdown_output
    assert "  - Missing Alt Text: 1 pages" in markdown_output # From result2.technical_issues (assumed it's added by analyzer, not hardcoded in result)
    assert "  - Mixed Content (HTTP resources on HTTPS page): 1 pages" in markdown_output

    assert "## Status Code Distribution" in markdown_output
    assert "- `200`: 2 pages" in markdown_output
    assert "- `404`: 1 pages" in markdown_output

    # Test empty report
    empty_summary_report = SEOSummaryReport()
    empty_markdown_output = empty_summary_report.to_markdown()
    assert "No analysis results to summarize." in empty_markdown_output
    assert "- **Total Pages Analyzed:** 0" in empty_markdown_output
