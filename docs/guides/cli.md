# CLI Usage Guide

## Installation

```bash
pip install seokar[cli]
```

## Basic Analysis

```bash
seokar analyze https://example.com
```

Options:
- `--output`: Save report to file
- `--format`: Output format (json/text/markdown/html)
- `--no-backlinks`: Exclude backlink analysis
- `--ahrefs-key`: Ahrefs API key

## Competitor Comparison

```bash
seokar compare https://your-site.com https://competitor1.com https://competitor2.com
```

## Environment Variables

Set default API keys:

```bash
export AHREFS_API_KEY="your-key"
export SEMRUSH_API_KEY="your-key"
```

## Output Formats

### JSON
```bash
seokar analyze https://example.com --format json
```

### HTML
```bash
seokar analyze https://example.com --format html --output report.html
```

### Markdown
```bash
seokar analyze https://example.com --format markdown
```
