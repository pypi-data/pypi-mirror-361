#!/usr/bin/env python3
"""
Search and URL mapping examples using RapidCrawl.

This example demonstrates how to:
- Search the web and scrape results
- Map all URLs from a website
- Filter and analyze URL structures
- Combine search with scraping
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
from collections import defaultdict

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import RapidCrawlError


def basic_search():
    """Basic web search example."""
    print("=== Basic Search Example ===\n")
    
    app = RapidCrawlApp()
    
    # Search for Python tutorials
    query = "Python web scraping tutorial"
    print(f"Searching for: {query}")
    
    try:
        result = app.search(query, num_results=10)
        
        if result.success:
            print(f"\nFound {len(result.results)} results:")
            for item in result.results:
                print(f"\n{item.position}. {item.title}")
                print(f"   URL: {item.url}")
                print(f"   Snippet: {item.snippet[:100]}...")
        else:
            print(f"Search failed: {result.error}")
    
    except RapidCrawlError as e:
        print(f"Search error: {e}")


def search_with_scraping():
    """Search and scrape the results."""
    print("\n=== Search with Scraping Example ===\n")
    
    app = RapidCrawlApp()
    
    # Search and scrape results
    query = "latest AI news"
    print(f"Searching and scraping: {query}")
    
    result = app.search(
        query,
        num_results=5,
        scrape_results=True,
        formats=["markdown", "text"]
    )
    
    if result.success:
        print(f"\nProcessing {len(result.results)} results:")
        
        articles = []
        for item in result.results:
            print(f"\n{item.position}. {item.title}")
            
            if item.scraped_content and item.scraped_content.success:
                content = item.scraped_content.content.get("text", "")
                word_count = len(content.split())
                
                print(f"   ✓ Scraped successfully")
                print(f"   Word count: {word_count}")
                
                articles.append({
                    "title": item.title,
                    "url": item.url,
                    "word_count": word_count,
                    "preview": content[:200] + "..."
                })
            else:
                print(f"   ✗ Scraping failed")
        
        # Save articles
        if articles:
            with open("search_results.json", "w") as f:
                json.dump(articles, f, indent=2)
            print(f"\nSaved {len(articles)} articles to search_results.json")


def advanced_search():
    """Advanced search with filters."""
    print("\n=== Advanced Search Example ===\n")
    
    app = RapidCrawlApp()
    
    # Search with date range
    print("Searching for recent content...")
    
    result = app.search(
        "machine learning breakthroughs",
        num_results=10,
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        engine="google"  # or "bing", "duckduckgo"
    )
    
    if result.success:
        print(f"\nFound {len(result.results)} recent results")
        
        # Group by domain
        by_domain = defaultdict(list)
        for item in result.results:
            domain = urlparse(item.url).netloc
            by_domain[domain].append(item)
        
        print("\nResults by domain:")
        for domain, items in sorted(by_domain.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {domain}: {len(items)} results")


def basic_url_mapping():
    """Map all URLs from a website."""
    print("\n=== Basic URL Mapping Example ===\n")
    
    app = RapidCrawlApp()
    
    # Map URLs from a website
    url = "https://example.com"
    print(f"Mapping URLs from {url}...")
    
    try:
        result = app.map_url(url, limit=100)
        
        if result.success:
            print(f"\nMapping completed!")
            print(f"  Total URLs found: {result.total_urls}")
            print(f"  Sitemap found: {'Yes' if result.sitemap_found else 'No'}")
            print(f"  Duration: {result.duration:.2f}s")
            
            # Analyze URL structure
            url_parts = defaultdict(int)
            for url in result.urls:
                path = urlparse(url).path
                parts = path.strip('/').split('/')
                if parts and parts[0]:
                    url_parts[parts[0]] += 1
            
            print("\nTop URL sections:")
            for section, count in sorted(url_parts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  /{section}/: {count} URLs")
            
            # Save URL list
            with open("sitemap.txt", "w") as f:
                for url in sorted(result.urls):
                    f.write(f"{url}\n")
            print(f"\nSaved {len(result.urls)} URLs to sitemap.txt")
    
    except RapidCrawlError as e:
        print(f"Mapping error: {e}")


def filtered_mapping():
    """Map URLs with filtering."""
    print("\n=== Filtered URL Mapping Example ===\n")
    
    app = RapidCrawlApp()
    
    # Map only product URLs
    result = app.map_url(
        "https://shop.example.com",
        search="product",
        limit=200
    )
    
    if result.success:
        print(f"Found {len(result.urls)} product URLs")
        
        # Categorize URLs
        categories = {
            "products": [],
            "categories": [],
            "pages": [],
            "other": []
        }
        
        for url in result.urls:
            if "/product/" in url:
                categories["products"].append(url)
            elif "/category/" in url:
                categories["categories"].append(url)
            elif "/page/" in url:
                categories["pages"].append(url)
            else:
                categories["other"].append(url)
        
        print("\nURL breakdown:")
        for category, urls in categories.items():
            print(f"  {category}: {len(urls)} URLs")
            
            # Show samples
            if urls:
                print(f"    Sample: {urls[0]}")


def map_with_subdomains():
    """Map URLs including subdomains."""
    print("\n=== Subdomain Mapping Example ===\n")
    
    app = RapidCrawlApp()
    
    # Map with subdomains
    result = app.map_url(
        "https://example.com",
        include_subdomains=True,
        limit=500
    )
    
    if result.success:
        # Group by subdomain
        subdomains = defaultdict(list)
        
        for url in result.urls:
            domain = urlparse(url).netloc
            subdomains[domain].append(url)
        
        print(f"Found {len(subdomains)} unique domains:")
        for domain, urls in sorted(subdomains.items()):
            print(f"  {domain}: {len(urls)} URLs")
        
        # Find deepest URLs
        deepest_urls = sorted(result.urls, key=lambda x: x.count('/'), reverse=True)[:5]
        
        print("\nDeepest URLs:")
        for url in deepest_urls:
            depth = url.count('/') - 2
            print(f"  Depth {depth}: {url}")


def combine_search_and_map():
    """Combine search with URL mapping."""
    print("\n=== Combined Search and Map Example ===\n")
    
    app = RapidCrawlApp()
    
    # First, search for interesting sites
    print("Step 1: Searching for Python tutorial sites...")
    search_result = app.search(
        "best Python tutorial sites",
        num_results=5
    )
    
    if not search_result.success:
        print("Search failed!")
        return
    
    # Extract domains from search results
    domains = []
    for item in search_result.results:
        domain = urlparse(item.url).scheme + "://" + urlparse(item.url).netloc
        if domain not in domains:
            domains.append(domain)
    
    print(f"\nFound {len(domains)} unique domains")
    
    # Map each domain
    print("\nStep 2: Mapping tutorial URLs from each domain...")
    
    all_tutorials = []
    for domain in domains[:3]:  # Limit to first 3 for demo
        print(f"\nMapping {domain}...")
        
        try:
            map_result = app.map_url(
                domain,
                search="tutorial",
                limit=50
            )
            
            if map_result.success:
                tutorial_urls = [
                    url for url in map_result.urls
                    if any(keyword in url.lower() for keyword in ["tutorial", "guide", "learn"])
                ]
                
                print(f"  Found {len(tutorial_urls)} tutorial URLs")
                all_tutorials.extend(tutorial_urls)
        
        except Exception as e:
            print(f"  Error mapping {domain}: {e}")
    
    print(f"\nTotal tutorial URLs found: {len(all_tutorials)}")
    
    # Save combined results
    if all_tutorials:
        with open("tutorial_urls.json", "w") as f:
            json.dump({
                "search_query": "best Python tutorial sites",
                "domains_searched": domains[:3],
                "tutorial_urls": all_tutorials[:50],  # Limit for file size
                "total_found": len(all_tutorials),
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print("Saved results to tutorial_urls.json")


if __name__ == "__main__":
    try:
        # Run all examples
        basic_search()
        search_with_scraping()
        advanced_search()
        basic_url_mapping()
        filtered_mapping()
        map_with_subdomains()
        combine_search_and_map()
        
        print("\n✓ All search and mapping examples completed!")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")