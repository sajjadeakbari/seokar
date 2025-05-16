# Seokar - Comprehensive On-Page SEO Analysis Library 🐍

[![PyPI version](https://badge.fury.io/py/seokar.svg)](https://badge.fury.io/py/seokar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/seokar)

**Seokar** is a powerful and comprehensive Python library designed for in-depth on-page SEO analysis of HTML content. It helps developers and SEO professionals to audit web pages, identify issues, and get actionable recommendations to improve search engine visibility and user experience.

The library is thread-safe, memory-efficient, and provides detailed insights into meta tags, content quality, page structure, links, social media presence, and structured data.

## ✨ Key Features

*   **Comprehensive Analysis:** Covers a wide range of on-page SEO factors including:
    *   **Meta Tags:** Title (length, presence), Meta Description (length, presence), Meta Robots (directives like `noindex`, `nofollow`), Canonical URL (presence, correctness), Viewport (configuration for mobile), Charset (declaration, UTF-8 recommendation), HTML Language (declaration).
    *   **Favicon:** Detection of favicon link or default.
    *   **Heading Structure:** H1-H6 hierarchy, count (especially H1s), logical order, content length and word count for important headings.
    *   **Content Quality:** Main content length (thin content detection), Text-to-HTML ratio, Readability (Flesch Reading Ease score), Keyword Density (single words and bigrams, excluding stop words).
    *   **Image SEO:** Alt text presence, empty alt text (distinguishing decorative vs. missing), alt text length.
    *   **Link Analysis:** Internal and external links, `nofollow`, `sponsored`, `ugc` attributes, anchor text distribution (generic, branded, keyword-like).
    *   **Social Media Tags:** Open Graph (og:*) tags and Twitter Card (twitter:*) tags validation for essential properties.
    *   **Structured Data:** Detection and extraction of JSON-LD, Microdata, and RDFa, along with identified Schema.org types.
*   **Actionable Recommendations:** Provides clear, specific suggestions for fixing identified issues, categorized by severity (INFO, GOOD, WARNING, ERROR, CRITICAL).
*   **SEO Health Score:** Calculates an overall score (0-100%) based on the severity and number of issues found.
*   **Detailed Reporting:** Returns a well-structured dictionary containing all analysis results, issues, and recommendations.
*   **Thread-Safe Caching:** Implements an intelligent caching mechanism for page elements (meta tags, headings, links, etc.) to optimize performance on repeated access, with thread-safety.
*   **Robust & Reliable:** Includes strict input validation and advanced URL handling, properly resolving relative URLs and considering the page's `<base>` tag.
*   **Modern Python:** Utilizes strict type hinting (including `Literal` for Enums) for enhanced code quality and IDE support, and `dataclasses` for structured results. Optimized for memory usage with `__slots__`.
*   **Customizable Constants:** Allows for easy adjustment of SEO best practice thresholds (e.g., optimal title length, stop words) via class attributes.

## 🚀 Installation

You can install Seokar using pip:

```bash
pip install seokar
```
*(Note: Ensure the package name `seokar` is available on PyPI or use your chosen unique name).*

## 🛠️ Basic Usage

Here's a simple example of how to use Seokar:

```python
from seokar import Seokar, SEOResultLevel, __version__

# Sample HTML content (can be fetched from a URL using requests or other libraries)
html_document = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Awesome Test Page - SEO Analysis Example</title>
    <meta name="description" content="A short but sweet description for this testing page. It aims to be optimal.">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="canonical" href="https://example.com/test-page">
    <!-- <meta name="robots" content="noindex"> -->
</head>
<body>
    <h1>Main Heading for the Page: SEO Rocks!</h1>
    <p>This is some paragraph text. It's important for content quality analysis. We need enough content to pass the minimum length requirement and to check readability.</p>
    <h2>A Subheading Here</h2>
    <p>More content goes here. Links are also important.</p>
    <img src="image.png" alt="A descriptive alt text for the image example">
    <img src="decorative.gif" alt=""> <!-- Decorative image -->
    <p>
        An internal link: <a href="/internal-page">Click Here</a><br>
        An external link: <a href="https://externalsite.com" rel="nofollow">External Site</a>
    </p>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "My Awesome Test Page"
    }
    </script>
</body>
</html>
"""
page_url = "https://example.com/test-page"

# Initialize the analyzer
analyzer = Seokar(html_content=html_document, url=page_url)

# Get the library version
print(f"Using Seokar version: {__version__}") # or analyzer.get_version()

# Perform the analysis
report = analyzer.analyze()

# Print the overall SEO Health Score
print(f"\nOverall SEO Health Score: {report['seo_health']['score']}%")
print(f"Critical Issues: {report['seo_health']['critical_issues_count']}")
print(f"Error Issues: {report['seo_health']['error_issues_count']}")
print(f"Warning Issues: {report['seo_health']['warning_issues_count']}")

# Print some basic SEO info
print(f"\nPage Title: {report['basic_seo']['title']}")
print(f"Meta Description: {report['basic_seo']['meta_description']}")
print(f"Canonical URL: {report['basic_seo']['canonical_url']}")

# Print issues with WARNING level or higher
print("\nIdentified Issues (Warning or higher):")
for issue in report['issues']:
    # The issue['level'] is a dictionary representation of the SEOResultLevel enum
    # Access 'value' for numeric comparison or 'name' for string representation
    if issue['level']['value'] >= SEOResultLevel.WARNING.value:
        print(f"- Type: {issue['element_type']}, Level: {issue['level']['name']}")
        print(f"  Message: {issue['message']}")
        if issue['details']:
            print(f"  Details: {issue['details']}")
        if issue['recommendation']:
            print(f"  Recommendation: {issue['recommendation']}")

# Example: Accessing keyword density
# print("\nTop Keywords (Content Quality):")
# for term, density in report['content_quality'].get('keyword_density_top_10_with_bigrams', {}).items():
#    print(f"- '{term}': {density}%")
```

## 📊 Understanding the Report

The `analyze()` method returns a dictionary containing a comprehensive breakdown of the SEO analysis. Key top-level keys in the report include:

*   `analyzer_version`: Version of Seokar used.
*   `url`: The URL analyzed.
*   `basic_seo`: Information on title, meta description, robots, canonical, viewport, charset, language, favicon.
*   `headings`: Data on H1-H6 tags, including their content, count, and hierarchy assessment.
*   `content_quality`: Analysis of content length, text-to-HTML ratio, readability score, and keyword density.
*   `images`: Findings related to image `alt` texts.
*   `links`: Details about internal and external links, `nofollow` attributes, and anchor text patterns.
*   `social_media_tags`: Extracted Open Graph and Twitter Card tags.
*   `structured_data`: Detected JSON-LD, Microdata, and RDFa, including Schema.org types.
*   `seo_health`: The overall SEO score and counts of critical, error, and warning issues.
*   `issues`: A list of all individual findings (dictionaries representing `SEOResult` objects, including severity level, message, details, and recommendation).
*   `recommendations`: A consolidated list of unique, actionable recommendations for high-severity issues.

Each sub-dictionary contains more granular data relevant to that specific SEO aspect.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project on GitHub ([https://github.com/sajjadeakbari/seokar](https://github.com/sajjadeakbari/seokar)).
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

Please make sure to update documentation or tests as appropriate and follow the existing code style. You can also simply open an issue with the tag "enhancement" or "bug".
Don't forget to give the project a star! Thanks again!

## 📜 License

Distributed under the MIT License. See `LICENSE` file for more information.

[Link to LICENSE file](LICENSE)

## 📧 Contact

Sajjad Akbari - [sajjadakbari.ir@email.com](mailto:sajjadakbari.ir@email.com)

Project Link: [https://github.com/sajjadeakbari/seokar](https://github.com/sajjadeakbari/seokar)
