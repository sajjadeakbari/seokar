# seokar/models.py
# CHANGE: Imported timezone for robust timestamping.
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional

@dataclass(frozen=True)
class CoreWebVitalsMetrics:
    """Encapsulates Core Web Vitals scores. Immutable."""
    lcp: Optional[float] = None  # Largest Contentful Paint in seconds
    cls: Optional[float] = None  # Cumulative Layout Shift
    inp: Optional[float] = None  # Interaction to Next Paint in milliseconds

@dataclass(frozen=True)
class ContentMetrics:
    """Encapsulates content analysis metrics. Immutable."""
    word_count: Optional[int] = None
    # NOTE: Readability score is highly language-dependent. 
    # The 'textstat' library is only suitable for English.
    readability_score: Optional[float] = None
    keyword_density: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True)
class SEOResult:
    """
    Represents the SEO analysis result for a single page.
    This object is immutable; once created, it cannot be changed.
    """
    url: str
    status_code: Optional[int]
    page_size_bytes: Optional[int] = None
    loading_time_ms: Optional[float] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    robots_tag: Optional[str] = None
    technical_issues: List[str] = field(default_factory=list)
    security_headers: Dict[str, str] = field(default_factory=dict)
    schema_present: bool = False
    core_web_vitals: Optional[CoreWebVitalsMetrics] = None
    content_metrics: Optional[ContentMetrics] = None
    # CHANGE: Using timezone-aware datetime for reliability.
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass(frozen=True)
class SEOSummaryReport:
    """
    Represents a summary report of SEO analysis for multiple pages. Immutable.
    """
    results: List[SEOResult]
    report_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    # CHANGE: Made total_pages_analyzed a property for cleaner access.
    
    @property
    def total_pages_analyzed(self) -> int:
        """Returns the total number of pages analyzed."""
        return len(self.results)
