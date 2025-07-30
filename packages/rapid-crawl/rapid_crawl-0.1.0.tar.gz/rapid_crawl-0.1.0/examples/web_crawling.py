#!/usr/bin/env python3
"""
Web crawling example using RapidCrawl.

This example demonstrates how to:
- Crawl websites recursively
- Filter URLs with patterns
- Handle large crawls efficiently
- Extract data during crawling
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import RapidCrawlError


def basic_crawl():
    """Basic website crawling."""
    print("=== Basic Crawling Example ===\n")
    
    app = RapidCrawlApp()
    
    # Crawl a small website
    url = "https://example.com"
    print(f"Crawling {url}...")
    print("(Limited to 10 pages for demo)\n")
    
    try:
        result = app.crawl_url(
            url,
            max_pages=10,
            max_depth=2
        )
        
        print(f"Crawl completed!")
        print(f"  Status: {result.status}")
        print(f"  Pages crawled: {result.pages_crawled}")
        print(f"  Pages failed: {result.pages_failed}")
        print(f"  Duration: {result.duration:.2f}s")
        
        # Show first few pages
        print("\nFirst 5 pages crawled:")
        for page in result.pages[:5]:
            if page.success:
                print(f"  ✓ {page.url}")
                print(f"    Title: {page.title}")
            else:
                print(f"  ✗ {page.url}")
                print(f"    Error: {page.error}")
    
    except RapidCrawlError as e:
        print(f"Crawl error: {e}")


def filtered_crawl():
    """Crawl with URL filtering."""
    print("\n=== Filtered Crawling Example ===\n")
    
    app = RapidCrawlApp()
    
    # Crawl only specific sections
    result = app.crawl_url(
        "https://example.com",
        max_pages=20,
        include_patterns=[
            r"/docs/.*",      # Documentation pages
            r"/blog/.*",      # Blog posts
            r"/tutorials/.*"  # Tutorials
        ],
        exclude_patterns=[
            r".*\.pdf$",      # Skip PDFs
            r".*/print/.*",   # Skip print versions
            r".*\?.*"         # Skip URLs with query params
        ]
    )
    
    print(f"Filtered crawl completed!")
    print(f"  Pages found: {result.total_pages}")
    print(f"  Pages crawled: {result.pages_crawled}")
    
    # Group by section
    sections = {}
    for page in result.pages:
        if page.success:
            if "/docs/" in page.url:
                section = "docs"
            elif "/blog/" in page.url:
                section = "blog"
            elif "/tutorials/" in page.url:
                section = "tutorials"
            else:
                section = "other"
            
            if section not in sections:
                sections[section] = []
            sections[section].append(page.url)
    
    print("\nPages by section:")
    for section, urls in sections.items():
        print(f"  {section}: {len(urls)} pages")


async def async_crawl():
    """Asynchronous crawling for better performance."""
    print("\n=== Async Crawling Example ===\n")
    
    app = RapidCrawlApp()
    
    # Crawl multiple sites concurrently
    sites = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]
    
    print("Crawling multiple sites concurrently...")
    
    async def crawl_site(url):
        try:
            result = await app.crawl_url_async(
                url,
                max_pages=10,
                max_depth=2
            )
            return {
                "url": url,
                "success": True,
                "pages_crawled": result.pages_crawled,
                "duration": result.duration
            }
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    # Run crawls concurrently
    tasks = [crawl_site(url) for url in sites]
    results = await asyncio.gather(*tasks)
    
    print("\nResults:")
    for result in results:
        if result["success"]:
            print(f"  ✓ {result['url']}")
            print(f"    Pages: {result['pages_crawled']}")
            print(f"    Time: {result['duration']:.2f}s")
        else:
            print(f"  ✗ {result['url']}")
            print(f"    Error: {result['error']}")


def crawl_with_extraction():
    """Crawl and extract data from pages."""
    print("\n=== Crawl with Data Extraction ===\n")
    
    app = RapidCrawlApp()
    
    # Define extraction schema for product pages
    product_schema = [
        {"name": "title", "selector": "h1"},
        {"name": "price", "selector": ".price", "type": "number"},
        {"name": "description", "selector": ".description"},
        {"name": "image", "selector": ".product-image", "attribute": "src"}
    ]
    
    # Crawl product pages and extract data
    result = app.crawl_url(
        "https://shop.example.com",
        max_pages=20,
        include_patterns=[r"/product/.*"],
        extract_schema=product_schema
    )
    
    # Collect extracted products
    products = []
    for page in result.pages:
        if page.success and page.structured_data:
            product = page.structured_data
            product["url"] = page.url
            products.append(product)
    
    print(f"Found {len(products)} products")
    
    # Save to JSON
    if products:
        with open("extracted_products.json", "w") as f:
            json.dump(products, f, indent=2)
        print("Saved products to extracted_products.json")
        
        # Show sample
        print("\nSample product:")
        sample = products[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")


def crawl_with_progress():
    """Crawl with progress tracking."""
    print("\n=== Crawl with Progress Tracking ===\n")
    
    app = RapidCrawlApp()
    
    # Large crawl with webhook for progress
    # In real usage, set up a webhook endpoint
    print("Starting large crawl...")
    print("(In production, use webhook_url for real-time progress)\n")
    
    start_time = datetime.now()
    
    result = app.crawl_url(
        "https://example.com",
        max_pages=50,
        max_depth=3,
        # webhook_url="https://your-server.com/crawl-progress"
    )
    
    # Simulate progress tracking
    print(f"Crawl completed in {result.duration:.2f}s")
    print(f"  Total pages found: {result.total_pages}")
    print(f"  Pages crawled: {result.pages_crawled}")
    print(f"  Success rate: {(result.pages_crawled - result.pages_failed) / result.pages_crawled * 100:.1f}%")
    
    # Analyze crawl speed
    pages_per_second = result.pages_crawled / result.duration
    print(f"  Speed: {pages_per_second:.2f} pages/second")
    
    # Find deepest pages
    depth_counts = {}
    for page in result.pages:
        if page.success:
            depth = page.url.count('/') - 2  # Rough depth estimate
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
    
    print("\nPages by depth:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Level {depth}: {depth_counts[depth]} pages")


def save_crawl_results():
    """Save crawl results in various formats."""
    print("\n=== Save Crawl Results ===\n")
    
    app = RapidCrawlApp()
    
    # Crawl and save results
    result = app.crawl_url(
        "https://example.com",
        max_pages=20,
        formats=["markdown", "text"]
    )
    
    # Create output directory
    output_dir = Path("crawl_results")
    output_dir.mkdir(exist_ok=True)
    
    # Save URLs list
    with open(output_dir / "urls.txt", "w") as f:
        for page in result.pages:
            if page.success:
                f.write(f"{page.url}\n")
    
    # Save sitemap
    with open(output_dir / "sitemap.json", "w") as f:
        sitemap = []
        for page in result.pages:
            if page.success:
                sitemap.append({
                    "url": page.url,
                    "title": page.title,
                    "links": len(page.links or []),
                    "scraped_at": page.scraped_at.isoformat()
                })
        json.dump(sitemap, f, indent=2)
    
    # Save content
    for i, page in enumerate(result.pages[:5]):  # First 5 pages
        if page.success and page.content:
            # Save markdown
            if "markdown" in page.content:
                filename = f"page_{i+1}.md"
                with open(output_dir / filename, "w") as f:
                    f.write(f"# {page.title}\n")
                    f.write(f"URL: {page.url}\n\n")
                    f.write(page.content["markdown"])
    
    print(f"Results saved to {output_dir}/")
    print(f"  - urls.txt: List of all URLs")
    print(f"  - sitemap.json: Structured sitemap")
    print(f"  - page_*.md: Content of first 5 pages")


if __name__ == "__main__":
    try:
        # Run sync examples
        basic_crawl()
        filtered_crawl()
        crawl_with_extraction()
        crawl_with_progress()
        save_crawl_results()
        
        # Run async example
        print("\nRunning async example...")
        asyncio.run(async_crawl())
        
        print("\n✓ All crawling examples completed!")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")