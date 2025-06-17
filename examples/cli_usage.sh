#!/bin/bash
# SeoKar Pro CLI usage examples

# Basic analysis
seokar analyze https://example.com --format html --output report.html

# Competitor comparison
seokar compare https://your-site.com https://competitor1.com https://competitor2.com --output comparison.json

# With API keys
export AHREFS_API_KEY="your-key"
export SEMRUSH_API_KEY="your-key"
seokar analyze https://example.com --backlinks --pagespeed
