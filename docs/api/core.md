# Core Module API Reference

## SEOAnalyzer Class

The main analyzer class that performs SEO analysis.

### Methods

#### `analyze(url: HttpUrl) -> SEOReport`
Perform comprehensive SEO analysis of a URL.

```python
analyzer = SEOAnalyzer()
report = await analyzer.analyze("https://example.com")
```

#### `analyze_competitors(target: HttpUrl, competitors: List[HttpUrl]) -> Dict[HttpUrl, CompetitorAnalysisResult]`
Compare target URL with multiple competitors.

```python
results = await analyzer.analyze_competitors(
    "https://your-site.com",
    ["https://competitor1.com", "https://competitor2.com"]
)
```

### Configuration

Configure analysis behavior using `AnalysisConfig`:

```python
config = AnalysisConfig(
    include_backlinks=True,
    include_pagespeed=True,
    max_concurrent=5
)
analyzer = SEOAnalyzer(config)
```

## Models

### SEOReport
Contains all SEO analysis results for a single URL.

Key fields:
- `url`: The analyzed URL
- `seo_score`: Overall SEO score (0-100)
- `title`: Page title
- `meta_description`: Meta description
- `page_speed`: PageSpeedMetrics object
- `backlinks`: List of BacklinkInfo objects

### PageSpeedMetrics
Page speed performance metrics:
- `load_time`: Page load time in seconds
- `score`: Performance score (0-100)
- `issues`: List of performance issues

### BacklinkInfo
Backlink information:
- `url`: Backlink URL
- `domain_authority`: Domain authority score (0-100)
- `spam_score`: Spam score (0-100)
- `anchor_text`: Anchor text

### CompetitorAnalysisResult
Competitor comparison result:
- `url`: Competitor URL
- `seo_score`: Competitor's SEO score
- `content_gaps`: Content gaps compared to target
- `technical_advantages`: Technical advantages over target
