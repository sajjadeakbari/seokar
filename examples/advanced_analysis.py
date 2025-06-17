#!/usr/bin/env python3
"""
Advanced SEO analysis example using SeoKar Pro 2.0
"""
import asyncio
from seokar import SEOAnalyzer
from seokar.plugins import AhrefsPlugin, GooglePagespeedPlugin

async def main():
    # Initialize analyzer with plugins
    analyzer = SEOAnalyzer()
    analyzer.plugins.register("ahrefs", AhrefsPlugin(api_key="your-ahrefs-key"))
    analyzer.plugins.register("pagespeed", GooglePagespeedPlugin(api_key="your-google-key"))
    
    # Analyze main site
    target = "https://example.com"
    competitors = [
        "https://competitor1.com",
        "https://competitor2.com"
    ]
    
    print(f"Analyzing {target}...")
    target_report = await analyzer.analyze(target)
    
    print(f"\nSEO Score: {target_report.seo_score:.1f}/100")
    print(f"PageSpeed Score: {target_report.page_speed.score if target_report.page_speed else 'N/A'}")
    
    # Compare with competitors
    print("\nComparing with competitors...")
    comparison = await analyzer.analyze_competitors(target, competitors)
    
    for url, result in comparison.items():
        print(f"\n{url}:")
        print(f"  SEO Score: {result.seo_score:.1f}")
        print(f"  Content Gaps: {len(result.content_gaps)}")
        print(f"  Technical Advantages: {len(result.technical_advantages)}")

if __name__ == "__main__":
    asyncio.run(main())
