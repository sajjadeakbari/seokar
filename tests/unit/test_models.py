from datetime import datetime
from seokar.core.models import (
    SEOReport,
    PageSpeedMetrics,
    BacklinkInfo,
    CompetitorAnalysisResult,
    KeywordAnalysis
)
from pydantic import ValidationError
import pytest

def test_seo_report_validation():
    valid_data = {
        "url": "https://example.com",
        "title": "Test Page",
        "meta_description": "Test description",
        "links_count": 10,
        "images_without_alt": 2
    }
    
    # Test valid data
    report = SEOReport(**valid_data)
    assert report.url == "https://example.com"
    assert report.seo_score > 0  # Should be auto-calculated
    
    # Test invalid URL
    with pytest.raises(ValidationError):
        SEOReport(**{**valid_data, "url": "not-a-url"})
        
    # Test negative counts
    with pytest.raises(ValidationError):
        SEOReport(**{**valid_data, "links_count": -1})

def test_pagespeed_metrics():
    # Test valid score
    metrics = PageSpeedMetrics(load_time=2.5, score=85)
    assert metrics.score == 85
    
    # Test score bounds
    with pytest.raises(ValidationError):
        PageSpeedMetrics(load_time=2.5, score=101)
        
    with pytest.raises(ValidationError):
        PageSpeedMetrics(load_time=2.5, score=-1)

def test_backlink_info():
    backlink = BacklinkInfo(
        url="https://backlink.example.com",
        domain_authority=75,
        spam_score=20,
        anchor_text="Example Anchor"
    )
    assert backlink.spam_score == 20
    
    # Test domain authority bounds
    with pytest.raises(ValidationError):
        BacklinkInfo(
            url="https://test.com",
            domain_authority=101,
            spam_score=0,
            anchor_text="test"
        )

def test_competitor_analysis_result():
    result = CompetitorAnalysisResult(
        url="https://competitor.com",
        seo_score=80,
        top_keywords=["test", "example"],
        backlink_count=100
    )
    assert result.seo_score == 80
    
    # Test missing required fields
    with pytest.raises(ValidationError):
        CompetitorAnalysisResult(url="https://test.com")

def test_keyword_analysis():
    keyword = KeywordAnalysis(
        keyword="test",
        density=0.05,
        positions=[10, 25],
        score=75
    )
    assert keyword.keyword == "test"
    
    # Test density validation
    with pytest.raises(ValidationError):
        KeywordAnalysis(
            keyword="test",
            density=-0.1,
            positions=[],
            score=0
        )
