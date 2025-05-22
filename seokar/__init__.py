"""
Seokar SEO Analysis Library (v2.0.0)

A comprehensive Python library for advanced on-page SEO analysis and optimization.

Key Features:
- Complete on-page SEO analysis
- Technical SEO auditing
- Content quality evaluation
- Structured data validation
- Multi-threaded processing

Usage:
    >>> from seokar import analyze_page, SEOResultLevel
    >>> report = analyze_page(html_content, url="https://example.com")
    >>> print(report.summary)

Developed by: Sajjad Akbari
Website: https://sajjadakbari.ir
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Sajjad Akbari"
__license__ = "MIT"
__website__ = "https://sajjadakbari.ir"

import logging
from typing import Optional, Dict, Any

from .analyzer import SeokarAnalyzer
from .models import SEOResult, SEOResultLevel, SEOSummaryReport
from .constants import (
    SeoLimits,
    TechnicalSeo,
    ContentQuality,
    LocalSeo,
    SchemaMarkup,
    SecuritySeo,
    CoreWebVitals
)
from .exceptions import SeoValidationError, SeoAnalysisWarning

# Configure package-level logger
logging.getLogger(__name__).addHandler(logging.NullHandler())

def analyze_page(
    html_content: str,
    url: Optional[str] = None,
    timeout: float = 10.0,
    analyze_options: Optional[Dict[str, Any]] = None
) -> SEOSummaryReport:
    """
    Main entry point for SEO analysis.
    
    Args:
        html_content: Raw HTML content to analyze
        url: Optional base URL for resolution
        timeout: Analysis timeout in seconds
        analyze_options: Advanced analysis configuration
        
    Returns:
        SEOSummaryReport: Comprehensive analysis results
        
    Raises:
        SeoValidationError: For invalid inputs
        TimeoutError: If analysis exceeds timeout
        
    Example:
        >>> with open('page.html') as f:
        ...     report = analyze_page(f.read(), url="https://example.com")
        >>> print(report.score)
        87.5
    """
    analyzer = SeokarAnalyzer(html_content, url)
    return analyzer.analyze()

def quick_analyze(url: str, timeout: float = 30.0) -> SEOSummaryReport:
    """
    Fetch and analyze a web page in one step.
    
    Args:
        url: URL to fetch and analyze
        timeout: Total operation timeout
        
    Returns:
        SEOSummaryReport: Analysis results
        
    Note:
        Requires 'requests' extra: pip install seokar[network]
    """
    try:
        from .utils.network import fetch_page
    except ImportError as e:
        raise ImportError(
            "Network features require 'requests' package. "
            "Install with: pip install seokar[network]"
        ) from e
        
    html = fetch_page(url, timeout)
    return analyze_page(html, url)

# Public API exports
__all__ = [
    # Core functions
    'analyze_page',
    'quick_analyze',
    
    # Models
    'SEOResult',
    'SEOResultLevel',
    'SEOSummaryReport',
    
    # Constants
    'SeoLimits',
    'TechnicalSeo',
    'ContentQuality',
    'LocalSeo',
    'SchemaMarkup',
    'SecuritySeo',
    'CoreWebVitals',
    
    # Exceptions
    'SeoValidationError',
    'SeoAnalysisWarning'
]

# Version compatibility check
import sys
if sys.version_info < (3, 8):
    raise ImportError("Seokar requires Python 3.8 or higher")
