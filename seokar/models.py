from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class CoreWebVitalsMetrics:
    """Encapsulates Core Web Vitals scores."""
    lcp: Optional[float] = None  # Largest Contentful Paint in seconds
    cls: Optional[float] = None  # Cumulative Layout Shift
    inp: Optional[float] = None  # Interaction to Next Paint in milliseconds


@dataclass
class ContentMetrics:
    """Encapsulates content analysis metrics."""
    word_count: Optional[int] = None
    readability_score: Optional[float] = None  # e.g., Flesch-Kincaid score
    keyword_density: Dict[str, float] = field(default_factory=dict)  # Mapping of keywords to their density percentage


@dataclass
class SEOResult:
    """Represents the SEO analysis result for a single page."""
    url: str
    status_code: int
    page_size_bytes: Optional[int] = None
    loading_time_ms: Optional[float] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    robots_tag: Optional[str] = None
    technical_issues: List[str] = field(default_factory=list)  # e.g., 'Missing Alt Text', 'Broken Link'
    security_headers: Dict[str, str] = field(default_factory=dict)  # Mapping of header name to its value
    schema_present: bool = False
    core_web_vitals: Optional[CoreWebVitalsMetrics] = None
    content_metrics: Optional[ContentMetrics] = None
    analysis_timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the analysis result,
        excluding fields with None values.
        """
        raw_dict = asdict(self)
        return self._remove_none_values_recursively(raw_dict)

    @staticmethod
    def _remove_none_values_recursively(data: Any) -> Any:
        """Helper to recursively remove None values from dicts."""
        if isinstance(data, dict):
            return {k: SEOResult._remove_none_values_recursively(v)
                    for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            # Recursively process elements within lists, but don't remove None elements from the list itself
            return [SEOResult._remove_none_values_recursively(elem) for elem in data]
        else:
            return data

    def to_markdown(self) -> str:
        """Returns a human-readable Markdown report of the SEO result."""
        report = []
        report.append(f"# SEO Analysis Report: {self.url}\n")
        report.append(f"**Analysis Timestamp:** {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # General Information
        report.append("## General Information\n")
        report.append(f"- **URL:** `{self.url}`")
        report.append(f"- **Status Code:** `{self.status_code}`")
        if self.page_size_bytes is not None:
            report.append(f"- **Page Size:** {self.page_size_bytes / 1024:.2f} KB")
        if self.loading_time_ms is not None:
            report.append(f"- **Loading Time:** {self.loading_time_ms:.2f} ms")
        report.append("\n")

        # SEO Elements
        report.append("## SEO Elements\n")
        report.append(f"- **Title:** {self.title if self.title else 'N/A'}")
        report.append(f"- **Meta Description:** {self.meta_description if self.meta_description else 'N/A'}")
        report.append(f"- **H1 Tags:** {', '.join(self.h1_tags) if self.h1_tags else 'N/A'}")
        report.append(f"- **Canonical URL:** {self.canonical_url if self.canonical_url else 'N/A'}")
        report.append(f"- **Robots Tag:** {self.robots_tag if self.robots_tag else 'N/A'}")
        report.append(f"- **Schema Present:** {'Yes' if self.schema_present else 'No'}")
        report.append("\n")

        # Technical Issues
        report.append("## Technical Issues\n")
        if self.technical_issues:
            for issue in self.technical_issues:
                report.append(f"- {issue}")
        else:
            report.append("- No significant technical issues found.")
        report.append("\n")

        # Security Headers
        report.append("## Security Headers\n")
        if self.security_headers:
            for header, value in self.security_headers.items():
                report.append(f"- **{header}:** `{value}`")
        else:
            report.append("- No custom security headers found.")
        report.append("\n")

        # Core Web Vitals
        report.append("## Core Web Vitals\n")
        if self.core_web_vitals:
            report.append(f"- **LCP (Largest Contentful Paint):** {self.core_web_vitals.lcp:.2f} s" if self.core_web_vitals.lcp is not None else "- LCP: N/A")
            report.append(f"- **CLS (Cumulative Layout Shift):** {self.core_web_vitals.cls:.3f}" if self.core_web_vitals.cls is not None else "- CLS: N/A")
            report.append(f"- **INP (Interaction to Next Paint):** {self.core_web_vitals.inp:.2f} ms" if self.core_web_vitals.inp is not None else "- INP: N/A")
        else:
            report.append("- Core Web Vitals data not available.")
        report.append("\n")

        # Content Metrics
        report.append("## Content Metrics\n")
        if self.content_metrics:
            report.append(f"- **Word Count:** {self.content_metrics.word_count}" if self.content_metrics.word_count is not None else "- Word Count: N/A")
            report.append(f"- **Readability Score:** {self.content_metrics.readability_score:.2f}" if self.content_metrics.readability_score is not None else "- Readability Score: N/A")
            if self.content_metrics.keyword_density:
                report.append("- **Keyword Density:**")
                for keyword, density in self.content_metrics.keyword_density.items():
                    report.append(f"  - `{keyword}`: {density:.2%}")
            else:
                report.append("- Keyword Density: N/A")
        else:
            report.append("- Content metrics not available.")
        report.append("\n")

        return "\n".join(report)


@dataclass
class SEOSummaryReport:
    """Represents a summary report of SEO analysis for multiple pages."""
    results: List[SEOResult] = field(default_factory=list)
    total_pages_analyzed: int = field(init=False)
    overall_score: Optional[float] = None
    report_timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Calculates total_pages_analyzed after initialization."""
        self.total_pages_analyzed = len(self.results)

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the summary report."""
        raw_dict = asdict(self)
        return SEOResult._remove_none_values_recursively(raw_dict)

    def to_markdown(self) -> str:
        """Returns a human-readable Markdown summary report."""
        report = []
        report.append(f"# Seokar Summary Report\n")
        report.append(f"**Report Timestamp:** {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

        report.append("## General Summary\n")
        report.append(f"- **Total Pages Analyzed:** {self.total_pages_analyzed}")
        if self.overall_score is not None:
            report.append(f"- **Overall Score:** {self.overall_score:.2f}")
        report.append("\n")

        if not self.results:
            report.append("No analysis results to summarize.")
            return "\n".join(report)

        # Aggregate data
        total_loading_time = 0.0
        loading_time_count = 0
        total_word_count = 0
        word_count_count = 0
        total_readability_score = 0.0
        readability_score_count = 0
        status_code_distribution: Dict[int, int] = {}
        all_technical_issues: Dict[str, int] = {}
        missing_titles = 0
        missing_meta_descriptions = 0
        multiple_h1_pages = 0
        pages_with_schema = 0

        lcp_values = []
        cls_values = []
        inp_values = []

        for res in self.results:
            status_code_distribution[res.status_code] = status_code_distribution.get(res.status_code, 0) + 1

            if res.loading_time_ms is not None:
                total_loading_time += res.loading_time_ms
                loading_time_count += 1
            if not res.title:
                missing_titles += 1
            if not res.meta_description:
                missing_meta_descriptions += 1
            if len(res.h1_tags) > 1:
                multiple_h1_pages += 1
            if res.schema_present:
                pages_with_schema += 1
            
            for issue in res.technical_issues:
                all_technical_issues[issue] = all_technical_issues.get(issue, 0) + 1

            if res.core_web_vitals:
                if res.core_web_vitals.lcp is not None:
                    lcp_values.append(res.core_web_vitals.lcp)
                if res.core_web_vitals.cls is not None:
                    cls_values.append(res.core_web_vitals.cls)
                if res.core_web_vitals.inp is not None:
                    inp_values.append(res.core_web_vitals.inp)

            if res.content_metrics:
                if res.content_metrics.word_count is not None:
                    total_word_count += res.content_metrics.word_count
                    word_count_count += 1
                if res.content_metrics.readability_score is not None:
                    total_readability_score += res.content_metrics.readability_score
                    readability_score_count += 1

        report.append("## Performance Summary\n")
        if loading_time_count > 0:
            report.append(f"- **Average Loading Time:** {total_loading_time / loading_time_count:.2f} ms")
        else:
            report.append("- Average Loading Time: N/A")

        if lcp_values:
            report.append(f"- **Average LCP:** {sum(lcp_values) / len(lcp_values):.2f} s")
        if cls_values:
            report.append(f"- **Average CLS:** {sum(cls_values) / len(cls_values):.3f}")
        if inp_values:
            report.append(f"- **Average INP:** {sum(inp_values) / len(inp_values):.2f} ms")
        report.append("\n")

        report.append("## Content Summary\n")
        if word_count_count > 0:
            report.append(f"- **Average Word Count:** {total_word_count / word_count_count:.0f}")
        else:
            report.append("- Average Word Count: N/A")
        if readability_score_count > 0:
            report.append(f"- **Average Readability Score:** {total_readability_score / readability_score_count:.2f}")
        else:
            report.append("- Average Readability Score: N/A")
        report.append("\n")

        report.append("## SEO Elements Summary\n")
        report.append(f"- **Pages with Missing Title:** {missing_titles}")
        report.append(f"- **Pages with Missing Meta Description:** {missing_meta_descriptions}")
        report.append(f"- **Pages with Multiple H1s:** {multiple_h1_pages}")
        report.append(f"- **Pages with Schema Present:** {pages_with_schema}")
        report.append("\n")

        report.append("## Technical Overview\n")
        if all_technical_issues:
            report.append("- **Common Technical Issues:**")
            for issue, count in sorted(all_technical_issues.items(), key=lambda item: item[1], reverse=True):
                report.append(f"  - {issue}: {count} pages")
        else:
            report.append("- No common technical issues found across pages.")
        report.append("\n")
        
        report.append("## Status Code Distribution\n")
        if status_code_distribution:
            for code, count in sorted(status_code_distribution.items()):
                report.append(f"- `{code}`: {count} pages")
        else:
            report.append("- No status code data available.")
        report.append("\n")

        return "\n".join(report)
