# seokar/core/models.py

from typing import Optional, List, Dict, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class PageSpeedMetrics(BaseModel):
    load_time: float = Field(..., description="Page load time in seconds")
    score: int = Field(..., ge=0, le=100, description="Overall performance score (0-100)")
    issues: List[str] = Field(default_factory=list, description="List of performance issues")

class BacklinkInfo(BaseModel):
    url: HttpUrl = Field(..., description="Backlink URL")
    domain_authority: float = Field(..., ge=0, le=100, description="Domain authority score")
    spam_score: float = Field(..., ge=0, le=100, description="Spam score")
    anchor_text: str = Field(..., description="Anchor text used in backlink")
    first_seen: Optional[datetime] = Field(None, description="First seen date")

class KeywordAnalysis(BaseModel):
    keyword: str = Field(..., description="Keyword text")
    density: float = Field(..., ge=0, description="Keyword density")
    positions: List[int] = Field(default_factory=list, description="Positions in text")
    score: float = Field(..., ge=0, le=100, description="Relevance score")

class CompetitorAnalysisResult(BaseModel):
    url: HttpUrl = Field(..., description="Competitor URL")
    seo_score: float = Field(..., ge=0, le=100, description="Overall SEO score")
    top_keywords: List[str] = Field(default_factory=list, description="Top keywords")
    backlink_count: int = Field(0, ge=0, description="Number of backlinks")
    content_gaps: List[str] = Field(default_factory=list, description="Content gaps")
    technical_advantages: List[str] = Field(default_factory=list, description="Technical advantages")

class SEOReport(BaseModel):
    url: HttpUrl = Field(..., description="Analyzed URL")
    title: Optional[str] = Field(None, description="Page title")
    meta_description: Optional[str] = Field(None, description="Meta description")
    meta_tags: Dict[str, str] = Field(default_factory=dict, description="All meta tags")
    headers: Dict[str, List[str]] = Field(default_factory=dict, description="Header tags")
    keyword_analysis: List[KeywordAnalysis] = Field(default_factory=list, description="Keyword analysis")
    links_count: int = Field(0, ge=0, description="Total links count")
    images_without_alt: int = Field(0, ge=0, description="Images without alt text")
    page_speed: Optional[PageSpeedMetrics] = Field(None, description="Page speed metrics")
    backlinks: List[BacklinkInfo] = Field(default_factory=list, description="Backlinks info")
    structured_data: List[Dict[str, Union[str, List]]] = Field(default_factory=list, description="Structured data")
    canonical_url: Optional[HttpUrl] = Field(None, description="Canonical URL")
    hreflang: List[Dict[str, str]] = Field(default_factory=list, description="Hreflang tags")
    
    # FIX: Added seo_score field to resolve major bug
    seo_score: float = Field(0.0, ge=0, le=100, description="Overall SEO score calculated after analysis")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Report creation time")

    # FIX: Updated to Pydantic v2 syntax
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )
