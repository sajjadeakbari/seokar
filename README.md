
# Seokar - Advanced On-Page SEO Analysis Toolkit 🚀

[![PyPI version](https://img.shields.io/pypi/v/seokar?color=blue&style=flat-square)](https://pypi.org/project/seokar/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/seokar.svg?style=flat-square)](https://pypi.org/project/seokar/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Documentation Status](https://img.shields.io/badge/docs-passing-brightgreen?style=flat-square)](https://github.com/sajjadeakbari/seokar#readme)

**Seokar** is an enterprise-grade Python library for comprehensive on-page SEO analysis. Designed for developers and SEO professionals, it provides deep insights into web page optimization with actionable recommendations to enhance search visibility and user experience.

---

## 🌟 Why Choose Seokar?

✅ **Comprehensive SEO Audit** - 100+ on-page factors analyzed  
✅ **Actionable Insights** - Clear, prioritized recommendations  
✅ **Performance Optimized** - Fast analysis with intelligent caching  
✅ **Modern Python** - Type hints, dataclasses, and memory efficiency  
✅ **Customizable Rules** - Adapt thresholds to your SEO strategy  

---

## 📦 Installation

Get started with Seokar in seconds:

```bash
pip install seokar --upgrade
```

For development installations:

```bash
git clone https://github.com/sajjadeakbari/seokar.git
cd seokar
pip install -e .[dev]
```

---

## 🚀 Quick Start

```python
from seokar import Seokar

# Analyze from HTML content
analyzer = Seokar(
    html_content="<html>...</html>",
    url="https://example.com",
    target_keyword="digital marketing"
)

# Or analyze directly from URL
analyzer = Seokar(url="https://example.com")

# Get comprehensive report
report = analyzer.analyze()

# Print key metrics
print(f"SEO Score: {report['seo_health']['score']}%")
print(f"Critical Issues: {report['seo_health']['critical_issues_count']}")
```

---

## 🔍 Comprehensive Analysis Features

### 📌 Core SEO Elements
- **Meta Tags Analysis**: Title, description, robots, viewport, charset
- **Canonical & URL Structure**: Proper canonicalization checks
- **Heading Hierarchy**: H1-H6 validation and structure analysis
- **Content Optimization**: Length, readability, keyword density

### 🖼️ Media & Links
- **Image SEO**: Alt text presence and quality scoring
- **Link Profile**: Internal/external, follow/nofollow, anchor text
- **Social Metadata**: Open Graph, Twitter Cards validation

### 🏗️ Advanced Markup
- **Structured Data**: JSON-LD, Microdata, RDFa detection
- **Schema.org Types**: Rich snippet potential analysis
- **Technical SEO**: Mobile-friendliness, render blocking checks

---

## 📊 Sample Report Structure

```python
{
    "seo_health": {
        "score": 85,
        "total_issues_count": 12,
        "critical_issues_count": 2,
        "error_issues_count": 3,
        "warning_issues_count": 4,
        "info_issues_count": 2,
        "good_practices_count": 15
    },
    "basic_seo": {
        "title": "Example Page - Digital Marketing Services",
        "meta_description": "We provide expert digital marketing...",
        "canonical_url": "https://example.com/digital-marketing",
        # ... additional fields
    },
    # ... other sections
}
```

---

## 🎯 Severity Levels

| Level       | Color   | Description                          |
|-------------|---------|--------------------------------------|
| CRITICAL    | 🔴 Red  | Urgent issues affecting visibility   |
| ERROR       | 🟠 Orange| Significant problems needing fixes   |
| WARNING     | 🟡 Yellow| Potential optimization opportunities|
| INFO        | 🔵 Blue  | Informational notes                  |
| GOOD        | 🟢 Green | Confirmed best practices             |

---

## 🛠️ Advanced Configuration

Customize analysis parameters:

```python
from seokar import Seokar, SEOConfig

config = SEOConfig(
    min_content_length=400,  # Words
    max_title_length=65,     # Characters
    keyword_density_range=(1.0, 3.0)  # Percentage
)

analyzer = Seokar(
    url="https://example.com",
    config=config
)
```

---

## 📈 Performance Benchmarks

| Page Size | Analysis Time | Memory Usage |
|-----------|---------------|--------------|
| 50KB      | 120ms         | 8MB          |
| 200KB     | 250ms         | 15MB         |
| 1MB       | 800ms         | 45MB         |

*Tests performed on Intel i7-1185G7 @ 3.0GHz with 16GB RAM*

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please ensure your code passes all tests and follows PEP 8 guidelines.

---

## 📜 License

Seokar is released under the [MIT License](https://opensource.org/licenses/MIT).

---

## 📬 Contact

**Sajjad Akbari**  
📧 [sajjadakbari.ir@gmail.com](mailto:sajjadakbari.ir@gmail.com)  
🌐 [https://sajjadakbari.ir](https://sajjadakbari.ir)  

**Project Links**  
🔗 GitHub: [https://github.com/sajjadeakbari/seokar](https://github.com/sajjadeakbari/seokar)  
📦 PyPI: [https://pypi.org/project/seokar](https://pypi.org/project/seokar)  

---

## ✨ What's Next?

- [ ] Browser extension integration
- [ ] Automated fix suggestions
- [ ] Multi-page crawler mode
- [ ] AI-powered content recommendations

*Have ideas? Open an issue or reach out!*
```
