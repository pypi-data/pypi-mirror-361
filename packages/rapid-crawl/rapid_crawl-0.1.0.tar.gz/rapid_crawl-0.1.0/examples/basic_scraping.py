#!/usr/bin/env python3
"""
Basic web scraping example using RapidCrawl.

This example demonstrates how to:
- Scrape a single URL
- Get content in multiple formats
- Handle errors gracefully
- Extract structured data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import RapidCrawlError


def basic_scrape():
    """Basic scraping example."""
    print("=== Basic Scraping Example ===\n")
    
    # Initialize the app
    app = RapidCrawlApp()
    
    # Scrape a URL
    url = "https://example.com"
    print(f"Scraping {url}...")
    
    try:
        result = app.scrape_url(url)
        
        if result.success:
            print(f"✓ Successfully scraped!")
            print(f"  Title: {result.title}")
            print(f"  Content length: {len(result.content.get('markdown', ''))} chars")
            print(f"  Load time: {result.load_time:.2f}s")
            
            # Save markdown content
            with open("example_content.md", "w") as f:
                f.write(result.content["markdown"])
            print("  Saved content to example_content.md")
        else:
            print(f"✗ Failed to scrape: {result.error}")
    
    except RapidCrawlError as e:
        print(f"Error: {e}")


def multiple_formats():
    """Get content in multiple formats."""
    print("\n=== Multiple Formats Example ===\n")
    
    app = RapidCrawlApp()
    
    result = app.scrape_url(
        "https://example.com",
        formats=["markdown", "html", "text", "links"]
    )
    
    if result.success:
        print("Available formats:")
        for format_name, content in result.content.items():
            if isinstance(content, str):
                print(f"  - {format_name}: {len(content)} chars")
            elif isinstance(content, list):
                print(f"  - {format_name}: {len(content)} items")
        
        # Show first 5 links
        if result.links:
            print("\nFirst 5 links found:")
            for link in result.links[:5]:
                print(f"  - {link}")


def extract_structured_data():
    """Extract structured data from a page."""
    print("\n=== Structured Data Extraction ===\n")
    
    app = RapidCrawlApp()
    
    # Define extraction schema
    schema = [
        {"name": "title", "selector": "h1"},
        {"name": "paragraphs", "selector": "p", "type": "array"},
        {"name": "links", "selector": "a", "attribute": "href", "type": "array"}
    ]
    
    result = app.scrape_url(
        "https://example.com",
        extract_schema=schema
    )
    
    if result.success and result.structured_data:
        print("Extracted data:")
        for field, value in result.structured_data.items():
            if isinstance(value, list):
                print(f"  {field}: {len(value)} items")
            else:
                print(f"  {field}: {value}")


def scrape_with_options():
    """Scrape with various options."""
    print("\n=== Advanced Options Example ===\n")
    
    app = RapidCrawlApp()
    
    # Scrape with custom headers and mobile viewport
    result = app.scrape_url(
        "https://example.com",
        headers={
            "User-Agent": "RapidCrawl Example Bot",
            "Accept-Language": "en-US"
        },
        mobile=True,
        timeout=60000,  # 60 seconds
        only_main_content=True
    )
    
    if result.success:
        print("✓ Successfully scraped with custom options")
        print(f"  Mobile view: Yes")
        print(f"  Main content only: Yes")
        
        # Check metadata
        if result.metadata:
            print("\nPage metadata:")
            for key, value in result.metadata.items():
                print(f"  {key}: {value}")


def batch_scraping():
    """Scrape multiple URLs."""
    print("\n=== Batch Scraping Example ===\n")
    
    app = RapidCrawlApp()
    
    urls = [
        "https://example.com",
        "https://example.org",
        "https://httpbin.org/html"
    ]
    
    results = []
    for url in urls:
        print(f"Scraping {url}...")
        try:
            result = app.scrape_url(url, formats=["markdown"])
            results.append({
                "url": url,
                "success": result.success,
                "title": result.title if result.success else None,
                "error": result.error if not result.success else None
            })
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "title": None,
                "error": str(e)
            })
    
    # Summary
    print("\nSummary:")
    successful = sum(1 for r in results if r["success"])
    print(f"  Successful: {successful}/{len(urls)}")
    
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {result['url']}")
        if result["title"]:
            print(f"     Title: {result['title']}")
        if result["error"]:
            print(f"     Error: {result['error']}")


if __name__ == "__main__":
    # Run all examples
    try:
        basic_scrape()
        multiple_formats()
        extract_structured_data()
        scrape_with_options()
        batch_scraping()
        
        print("\n✓ All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")