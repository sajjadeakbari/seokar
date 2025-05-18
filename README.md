# Seokar - Comprehensive On-Page SEO Analysis Library 🐍

[![PyPI version](https://badge.fury.io/py/seokar.svg)](https://badge.fury.io/py/seokar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/seokar)

**Seokar** is a powerful and comprehensive Python library designed for in-depth on-page SEO analysis of HTML content. It helps developers and SEO professionals audit web pages, identify issues, and get actionable recommendations to improve search engine visibility and user experience.

---

## ✨ Key Features

- **Comprehensive Analysis:** Covers a wide range of on-page SEO factors:
  - **Meta Tags:** Title, Meta Description, Meta Robots, Canonical URL, Viewport, Charset, HTML Language
  - **Favicon:** Detection of favicon link or default
  - **Heading Structure:** H1-H6 tags count, hierarchy, and content quality
  - **Content Quality:** Length, thin content detection, Text-to-HTML ratio, Readability (Flesch Reading Ease), Keyword Density
  - **Image SEO:** `alt` text presence and quality
  - **Link Analysis:** Internal/external links, `nofollow`, `sponsored`, `ugc` attributes, anchor text types
  - **Social Media Tags:** Open Graph (og:*) and Twitter Card (twitter:*) tags validation
  - **Structured Data:** JSON-LD, Microdata, RDFa detection with Schema.org types

- **Actionable Recommendations:** Clear, severity-based suggestions to fix issues (INFO, GOOD, WARNING, ERROR, CRITICAL)

- **SEO Health Score:** Overall score (0-100%) based on found issues severity

- **Detailed Reporting:** Well-structured dictionary with all results, issues, and recommendations

- **Thread-Safe Caching:** Optimizes repeated analysis with safe caching

- **Modern Python:** Strict typing, `dataclasses`, `__slots__` for memory optimization

- **Customizable Constants:** Easily adjust SEO thresholds and stop words

---

## 🚀 Installation

```bash
pip install seokar
```
---

## 🛠️ Basic Usage


```python
from seokar import Seokar, SEOResultLevel, __version__
```


# Seokar - Comprehensive On-Page SEO Analysis Library ً

[![PyPI version](https://badge.fury.io/py/seokar.svg)](https://badge.fury.io/py/seokar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/seokar)

**Seokar** is a powerful and comprehensive Python library designed for in-depth on-page SEO analysis of HTML content. It helps developers and SEO professionals audit web pages, identify issues, and get actionable recommendations to improve search engine visibility and user experience.

---

## âœ¨ Key Features

- **Comprehensive Analysis:** Covers a wide range of on-page SEO factors:
  - **Meta Tags:** Title, Meta Description, Meta Robots, Canonical URL, Viewport, Charset, HTML Language
  - **Favicon:** Detection of favicon link or default
  - **Heading Structure:** H1-H6 tags count, hierarchy, and content quality
  - **Content Quality:** Length, thin content detection, Text-to-HTML ratio, Readability (Flesch Reading Ease), Keyword Density
  - **Image SEO:** `alt` text presence and quality
  - **Link Analysis:** Internal/external links, `nofollow`, `sponsored`, `ugc` attributes, anchor text types
  - **Social Media Tags:** Open Graph (og:*) and Twitter Card (twitter:*) tags validation
  - **Structured Data:** JSON-LD, Microdata, RDFa detection with Schema.org types

- **Actionable Recommendations:** Clear, severity-based suggestions to fix issues (INFO, GOOD, WARNING, ERROR, CRITICAL)

- **SEO Health Score:** Overall score (0-100%) based on found issues severity

- **Detailed Reporting:** Well-structured dictionary with all results, issues, and recommendations

- **Thread-Safe Caching:** Optimizes repeated analysis with safe caching

- **Modern Python:** Strict typing, `dataclasses`, `__slots__` for memory optimization

- **Customizable Constants:** Easily adjust SEO thresholds and stop words

---



## 📊 Understanding the Report

The analysis report returned by `Seokar.analyze()` is a structured dictionary containing multiple sections:

| Section Name      | Description                                                                                      |
|-------------------|--------------------------------------------------------------------------------------------------|
| `seo_health`      | Overall SEO health summary with score (0-100), and count of issues by severity                   |
| `basic_seo`       | Basic metadata extracted from the page like title, meta description, canonical URL, and language |
| `headings`        | Details about headings (h1-h6) including counts and hierarchy correctness                         |
| `content_quality` | Content length, text-to-HTML ratio, readability score, thin content warnings                      |
| `image_seo`       | Image analysis for presence and quality of `alt` attributes                                     |
| `links`           | Internal and external links details, attributes like nofollow, sponsored, ugc                    |
| `social_tags`     | Open Graph and Twitter Card tags validation                                                     |
| `structured_data` | Structured data found like JSON-LD, Microdata, RDFa along with schema.org types                   |
| `issues`          | List of all issues found, each with severity, message, affected element type, and recommendations|

---

### SEO Result Levels

| Level Name  | Description                         |
|-------------|-----------------------------------|
| INFO        | Informational notes, no issues     |
| GOOD        | Good practice, positive signals    |
| WARNING     | Potential issues, should review    |
| ERROR       | Definite issues that need fixing   |
| CRITICAL    | Severe problems, very urgent fixes |

---

## 🔍 Detailed Tables

### 1. Meta Tags Summary

| Tag            | Found | Value Example                         | Importance                      |
|----------------|-------|-------------------------------------|--------------------------------|
| Title          | Yes   | "My Awesome Test Page - SEO Analysis" | Very High                     |
| Meta Description | Yes | "A short but sweet description..."  | High                           |
| Meta Robots    | No    | N/A                                 | Medium                        |
| Canonical URL  | Yes   | https://example.com/test-page        | Very High                     |
| Viewport      | Yes   | width=device-width, initial-scale=1.0 | High                        |
| Charset       | Yes   | UTF-8                               | High                           |
| HTML Language | Yes   | en                                  | Medium                        |

---

### 2. Heading Tags Overview

| Tag  | Count | Expected | Status         | Notes                            |
|-------|-------|----------|----------------|---------------------------------|
| H1    | 1     | 1        | Good           | Perfect number of main headings |
| H2    | 1     | ≥ 0      | Good           | Appropriate subheading count    |
| H3-H6 | 0     | ≥ 0      | Good           | No problem                      |

---

### 3. Content Quality Metrics

| Metric            | Value          | Recommended Range       | Status       |
|-------------------|----------------|------------------------|--------------|
| Text Length       | 180 words      | > 300 words preferred   | Warning      |
| Text-to-HTML Ratio| 45%            | > 25%                  | Good         |
| Flesch Reading Ease| 60.0          | 50-70 (easy to read)    | Good         |
| Thin Content      | No             | No                     | Good         |
| Keyword Density   | 1.5%           | 1-3% optimal           | Good         |

---

### 4. Image SEO Summary

| Check             | Count Found | Count Passed | Status         |
|-------------------|-------------|--------------|----------------|
| Images with Alt    | 2           | 1            | Warning        |
| Images Missing Alt | 1           | N/A          | Needs Fix      |

---

### 5. Links Analysis

| Type           | Count | Notes                                     |
|----------------|-------|-------------------------------------------|
| Internal Links | 1     | Good internal linking structure           |
| External Links | 1     | One link marked nofollow (OK for SEO)     |
| Nofollow Attr  | 1     | Proper use of nofollow attribute           |
| Sponsored/UGC  | 0     | No sponsored or UGC links detected         |

---

### 6. Social Media Tags

| Tag Type    | Found | Status       |
|-------------|-------|--------------|
| Open Graph  | Yes   | Good         |
| Twitter Card| Yes   | Good         |

---

### 7. Structured Data Types

| Type          | Found | Notes                    |
|---------------|-------|--------------------------|
| JSON-LD       | Yes   | Schema.org WebPage type   |
| Microdata     | No    |                          |
| RDFa          | No    |                          |

---

## 📚 References & Resources

- [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Mozilla Developer Network - SEO Basics](https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Cross_browser_testing/SEO)
- [Schema.org Structured Data](https://schema.org/docs/gs.html)

---

## 📝 License

Seokar is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 📬 Contact & Support

For issues, suggestions, or contributions, please open an issue or pull request on the [GitHub repository](https://github.com/yourusername/seokar).

Thank you for using Seokar!  
Happy SEO analyzing!
