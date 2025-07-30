# RapidCrawl Examples

This document provides comprehensive examples for using RapidCrawl in various scenarios.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Web Scraping Examples](#web-scraping-examples)
- [Crawling Examples](#crawling-examples)
- [URL Mapping Examples](#url-mapping-examples)
- [Search Examples](#search-examples)
- [Data Extraction Examples](#data-extraction-examples)
- [Real-World Use Cases](#real-world-use-cases)
- [Performance Optimization](#performance-optimization)
- [Error Handling](#error-handling)

---

## Basic Usage

### Simple Setup

```python
from rapidcrawl import RapidCrawlApp

# Basic initialization
app = RapidCrawlApp()

# With configuration
app = RapidCrawlApp(
    api_key="your-api-key",
    timeout=60.0,
    debug=True
)

# Using environment variables
import os
os.environ["RAPIDCRAWL_API_KEY"] = "your-api-key"
app = RapidCrawlApp()
```

### Context Manager

```python
# Automatic cleanup with context manager
with RapidCrawlApp() as app:
    result = app.scrape_url("https://example.com")
    print(result.content["markdown"])
```

---

## Web Scraping Examples

### Basic Scraping

```python
# Scrape a URL and get markdown
result = app.scrape_url("https://example.com")

if result.success:
    print(f"Title: {result.title}")
    print(f"Content: {result.content['markdown'][:500]}...")
else:
    print(f"Error: {result.error}")
```

### Multiple Output Formats

```python
# Get content in multiple formats
result = app.scrape_url(
    "https://example.com",
    formats=["markdown", "html", "text", "screenshot"]
)

# Access different formats
markdown_content = result.content["markdown"]
html_content = result.content["html"]
text_content = result.content["text"]
screenshot_base64 = result.content["screenshot"]

# Save screenshot
import base64
with open("screenshot.png", "wb") as f:
    f.write(base64.b64decode(screenshot_base64))
```

### Dynamic Content Handling

```python
# Wait for specific element to load
result = app.scrape_url(
    "https://example.com",
    wait_for=".dynamic-content",
    timeout=60000  # 60 seconds
)

# Interact with the page
result = app.scrape_url(
    "https://example.com",
    actions=[
        {"type": "click", "selector": ".cookie-accept"},
        {"type": "wait", "value": 1000},
        {"type": "click", "selector": ".load-more"},
        {"type": "wait", "selector": ".new-content"},
        {"type": "scroll", "value": 1000}
    ]
)
```

### Mobile Scraping

```python
# Scrape with mobile viewport
result = app.scrape_url(
    "https://example.com",
    mobile=True,
    formats=["screenshot", "markdown"]
)
```

### Custom Headers and Authentication

```python
# With custom headers
result = app.scrape_url(
    "https://api.example.com/data",
    headers={
        "Authorization": "Bearer your-token",
        "X-API-Key": "your-api-key",
        "User-Agent": "Custom Bot 1.0"
    }
)

# Basic authentication
import base64
auth = base64.b64encode(b"username:password").decode()
result = app.scrape_url(
    "https://example.com/protected",
    headers={"Authorization": f"Basic {auth}"}
)
```

---

## Crawling Examples

### Basic Website Crawling

```python
# Crawl a website
result = app.crawl_url(
    "https://example.com",
    max_pages=50,
    max_depth=3
)

print(f"Crawled {result.pages_crawled} pages")
print(f"Failed: {result.pages_failed}")
print(f"Duration: {result.duration:.2f} seconds")

# Process crawled pages
for page in result.pages:
    if page.success:
        print(f"URL: {page.url}")
        print(f"Title: {page.title}")
        print(f"Links found: {len(page.links or [])}")
        print("---")
```

### Filtered Crawling

```python
# Crawl only specific sections
result = app.crawl_url(
    "https://example.com",
    include_patterns=[
        r"/blog/.*",
        r"/news/\d{4}/.*",
        r"/docs/.*"
    ],
    exclude_patterns=[
        r".*\.pdf$",
        r".*/tag/.*",
        r".*/author/.*",
        r".*\?print=true"
    ]
)

# Crawl with subdomains
result = app.crawl_url(
    "https://example.com",
    allow_subdomains=True,
    max_pages=100
)
```

### Async Crawling for Performance

```python
import asyncio

async def crawl_multiple_sites(urls):
    async with RapidCrawlApp() as app:
        tasks = []
        for url in urls:
            task = app.crawl_url_async(url, max_pages=20)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# Run async crawl
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
results = asyncio.run(crawl_multiple_sites(urls))
```

### Crawl with Progress Webhook

```python
# Set up webhook endpoint to receive progress
result = app.crawl_url(
    "https://example.com",
    max_pages=1000,
    webhook_url="https://your-server.com/crawl-progress"
)

# Webhook will receive POST requests with CrawlProgress data:
# {
#   "job_id": "uuid",
#   "status": "running",
#   "pages_crawled": 150,
#   "pages_found": 500,
#   "current_url": "https://example.com/page",
#   "depth": 2,
#   "duration": 45.2
# }
```

### Extract Data During Crawl

```python
# Define extraction schema
product_schema = [
    {"name": "title", "selector": "h1.product-name"},
    {"name": "price", "selector": ".price", "type": "number"},
    {"name": "availability", "selector": ".stock-status"},
    {"name": "image", "selector": ".product-image", "attribute": "src"}
]

# Crawl and extract
result = app.crawl_url(
    "https://shop.example.com",
    include_patterns=[r"/product/.*"],
    extract_schema=product_schema,
    max_pages=100
)

# Collect extracted data
products = []
for page in result.pages:
    if page.success and page.structured_data:
        products.append({
            "url": page.url,
            "data": page.structured_data
        })

print(f"Extracted data from {len(products)} products")
```

---

## URL Mapping Examples

### Basic URL Discovery

```python
# Map all URLs on a website
result = app.map_url("https://example.com")

print(f"Found {result.total_urls} URLs")
print(f"Sitemap used: {result.sitemap_found}")

# Save URLs to file
with open("urls.txt", "w") as f:
    for url in result.urls:
        f.write(f"{url}\n")
```

### Filtered Mapping

```python
# Find specific URLs
result = app.map_url(
    "https://example.com",
    search="product",
    limit=1000
)

# Filter product URLs
product_urls = [url for url in result.urls if "/product/" in url]
print(f"Found {len(product_urls)} product pages")
```

### Map with Subdomains

```python
# Include all subdomains
result = app.map_url(
    "https://example.com",
    include_subdomains=True,
    limit=10000
)

# Group by subdomain
from collections import defaultdict
by_subdomain = defaultdict(list)

for url in result.urls:
    domain = urlparse(url).netloc
    by_subdomain[domain].append(url)

for domain, urls in by_subdomain.items():
    print(f"{domain}: {len(urls)} URLs")
```

---

## Search Examples

### Basic Web Search

```python
# Simple search
result = app.search("python web scraping tutorial")

for item in result.results:
    print(f"{item.position}. {item.title}")
    print(f"   URL: {item.url}")
    print(f"   Snippet: {item.snippet}")
    print()
```

### Search with Content Scraping

```python
# Search and scrape results
result = app.search(
    "machine learning news",
    num_results=10,
    scrape_results=True,
    formats=["markdown", "text"]
)

# Process scraped content
articles = []
for item in result.results:
    if item.scraped_content and item.scraped_content.success:
        articles.append({
            "title": item.title,
            "url": item.url,
            "content": item.scraped_content.content["markdown"],
            "word_count": len(item.scraped_content.content["text"].split())
        })

print(f"Successfully scraped {len(articles)} articles")
```

### Search with Filters

```python
from datetime import datetime, timedelta

# Search with date range
result = app.search(
    "AI breakthroughs",
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    num_results=20
)

# Search with location
result = app.search(
    "restaurants near me",
    location="San Francisco",
    num_results=15
)

# Search with different engines
for engine in ["google", "bing", "duckduckgo"]:
    result = app.search(
        "python tutorials",
        engine=engine,
        num_results=5
    )
    print(f"\n{engine.upper()} Results:")
    for item in result.results:
        print(f"  - {item.title}")
```

---

## Data Extraction Examples

### Extract Structured Data

```python
# Define extraction schema
schema = [
    {"name": "title", "selector": "h1"},
    {"name": "author", "selector": ".author-name"},
    {"name": "date", "selector": "time", "attribute": "datetime"},
    {"name": "content", "selector": ".article-body"},
    {"name": "tags", "selector": ".tag", "type": "array"}
]

# Extract from single URL
result = app.extract("https://blog.example.com/article", schema=schema)
print(result.structured_data)
```

### Batch Extraction

```python
# Extract from multiple URLs
urls = [
    "https://shop.example.com/product/1",
    "https://shop.example.com/product/2",
    "https://shop.example.com/product/3"
]

schema = [
    {"name": "name", "selector": "h1"},
    {"name": "price", "selector": ".price", "type": "number", "regex": r"[\d.]+"},
    {"name": "in_stock", "selector": ".availability", "type": "boolean"},
    {"name": "images", "selector": "img.product-img", "attribute": "src", "type": "array"}
]

results = app.extract(urls, schema=schema)

# Process results
products = []
for i, result in enumerate(results):
    if result.success and result.structured_data:
        product = result.structured_data
        product["url"] = urls[i]
        products.append(product)

# Save to JSON
import json
with open("products.json", "w") as f:
    json.dump(products, f, indent=2)
```

### Extract with Natural Language Prompt

```python
# Use AI to extract (when available)
result = app.extract(
    "https://recipe.example.com/chocolate-cake",
    prompt="Extract the recipe ingredients, cooking time, and serving size"
)
```

---

## Real-World Use Cases

### E-commerce Price Monitoring

```python
import json
from datetime import datetime

class PriceMonitor:
    def __init__(self):
        self.app = RapidCrawlApp()
        self.schema = [
            {"name": "name", "selector": "h1"},
            {"name": "price", "selector": ".price-now", "type": "number"},
            {"name": "original_price", "selector": ".price-was", "type": "number"},
            {"name": "availability", "selector": ".stock-info"},
            {"name": "rating", "selector": ".rating", "type": "number"}
        ]
    
    def check_prices(self, product_urls):
        results = []
        
        for url in product_urls:
            result = self.app.scrape_url(url, extract_schema=self.schema)
            
            if result.success and result.structured_data:
                data = result.structured_data
                data["url"] = url
                data["checked_at"] = datetime.now().isoformat()
                
                # Calculate discount
                if data.get("original_price") and data.get("price"):
                    data["discount"] = round(
                        (1 - data["price"] / data["original_price"]) * 100, 2
                    )
                
                results.append(data)
        
        return results
    
    def save_results(self, results, filename="prices.json"):
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

# Usage
monitor = PriceMonitor()
urls = [
    "https://shop.example.com/product/laptop",
    "https://shop.example.com/product/phone",
]
results = monitor.check_prices(urls)
monitor.save_results(results)
```

### News Aggregator

```python
class NewsAggregator:
    def __init__(self):
        self.app = RapidCrawlApp()
        self.sources = {
            "tech": ["AI", "machine learning", "robotics"],
            "science": ["quantum computing", "space", "biology"],
            "business": ["startups", "finance", "economy"]
        }
    
    def aggregate_news(self):
        all_articles = []
        
        for category, queries in self.sources.items():
            for query in queries:
                # Search for news
                result = self.app.search(
                    query,
                    num_results=5,
                    scrape_results=True,
                    formats=["markdown", "text"]
                )
                
                # Process results
                for item in result.results:
                    if item.scraped_content and item.scraped_content.success:
                        article = {
                            "category": category,
                            "query": query,
                            "title": item.title,
                            "url": item.url,
                            "content": item.scraped_content.content["text"][:500],
                            "scraped_at": item.scraped_content.scraped_at
                        }
                        all_articles.append(article)
        
        return all_articles
    
    def generate_summary(self, articles):
        from collections import defaultdict
        by_category = defaultdict(list)
        
        for article in articles:
            by_category[article["category"]].append(article)
        
        summary = []
        for category, items in by_category.items():
            summary.append(f"\n## {category.upper()} NEWS\n")
            for article in items[:3]:  # Top 3 per category
                summary.append(f"**{article['title']}**")
                summary.append(f"{article['content']}")
                summary.append(f"[Read more]({article['url']})\n")
        
        return "\n".join(summary)

# Usage
aggregator = NewsAggregator()
articles = aggregator.aggregate_news()
summary = aggregator.generate_summary(articles)
print(summary)
```

### SEO Analyzer

```python
class SEOAnalyzer:
    def __init__(self):
        self.app = RapidCrawlApp()
    
    def analyze_page(self, url):
        result = self.app.scrape_url(
            url,
            formats=["html", "text", "links"],
            include_links=True,
            include_images=True
        )
        
        if not result.success:
            return None
        
        soup = BeautifulSoup(result.content["html"], "html.parser")
        
        analysis = {
            "url": url,
            "title": result.title,
            "title_length": len(result.title) if result.title else 0,
            "description": result.description,
            "description_length": len(result.description) if result.description else 0,
            "h1_count": len(soup.find_all("h1")),
            "h2_count": len(soup.find_all("h2")),
            "images_total": len(result.images or []),
            "images_without_alt": len([img for img in soup.find_all("img") if not img.get("alt")]),
            "internal_links": len([l for l in result.links or [] if url in l]),
            "external_links": len([l for l in result.links or [] if url not in l]),
            "word_count": len(result.content["text"].split()),
            "load_time": result.load_time
        }
        
        # Check meta tags
        meta_tags = {}
        for meta in soup.find_all("meta"):
            if meta.get("name"):
                meta_tags[meta["name"]] = meta.get("content", "")
            elif meta.get("property"):
                meta_tags[meta["property"]] = meta.get("content", "")
        
        analysis["meta_tags"] = meta_tags
        
        # SEO score (simple calculation)
        score = 100
        if analysis["title_length"] < 30 or analysis["title_length"] > 60:
            score -= 10
        if analysis["description_length"] < 120 or analysis["description_length"] > 160:
            score -= 10
        if analysis["h1_count"] != 1:
            score -= 15
        if analysis["images_without_alt"] > 0:
            score -= 5 * min(analysis["images_without_alt"], 5)
        if analysis["word_count"] < 300:
            score -= 20
        
        analysis["seo_score"] = max(0, score)
        
        return analysis

# Usage
analyzer = SEOAnalyzer()
result = analyzer.analyze_page("https://example.com/blog/article")
print(json.dumps(result, indent=2))
```

### Content Change Monitor

```python
import hashlib
import pickle
from datetime import datetime

class ChangeMonitor:
    def __init__(self, storage_file="monitor_data.pkl"):
        self.app = RapidCrawlApp()
        self.storage_file = storage_file
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.storage_file, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}
    
    def save_data(self):
        with open(self.storage_file, "wb") as f:
            pickle.dump(self.data, f)
    
    def check_page(self, url, selector=None):
        result = self.app.scrape_url(url, formats=["text", "html"])
        
        if not result.success:
            return None
        
        # Extract specific content if selector provided
        if selector:
            soup = BeautifulSoup(result.content["html"], "html.parser")
            element = soup.select_one(selector)
            content = element.get_text() if element else ""
        else:
            content = result.content["text"]
        
        # Calculate hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check for changes
        changed = False
        previous = self.data.get(url)
        
        if previous and previous["hash"] != content_hash:
            changed = True
        
        # Update data
        self.data[url] = {
            "hash": content_hash,
            "last_checked": datetime.now(),
            "changed": changed,
            "previous_hash": previous["hash"] if previous else None
        }
        
        self.save_data()
        
        return {
            "url": url,
            "changed": changed,
            "content": content if changed else None
        }
    
    def monitor_multiple(self, urls_config):
        results = []
        
        for config in urls_config:
            url = config["url"]
            selector = config.get("selector")
            
            result = self.check_page(url, selector)
            if result:
                result["name"] = config.get("name", url)
                results.append(result)
        
        return results

# Usage
monitor = ChangeMonitor()

# Define pages to monitor
pages = [
    {"name": "Product Price", "url": "https://shop.example.com/product", "selector": ".price"},
    {"name": "News Page", "url": "https://news.example.com", "selector": "main"},
    {"name": "Status Page", "url": "https://status.example.com", "selector": ".status-indicator"}
]

# Check for changes
changes = monitor.monitor_multiple(pages)

for change in changes:
    if change["changed"]:
        print(f"CHANGED: {change['name']} - {change['url']}")
        # Send notification, save diff, etc.
    else:
        print(f"No change: {change['name']}")
```

---

## Performance Optimization

### Concurrent Scraping

```python
import asyncio
from typing import List

async def scrape_many_urls(urls: List[str], max_concurrent: int = 10):
    app = RapidCrawlApp()
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_with_limit(url):
        async with semaphore:
            # Simulate async scraping (in real implementation, use async client)
            return await asyncio.to_thread(app.scrape_url, url)
    
    tasks = [scrape_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

# Usage
urls = ["https://example.com/page1", "https://example.com/page2", ...]
results = asyncio.run(scrape_many_urls(urls))
```

### Caching Results

```python
from functools import lru_cache
import pickle
import hashlib

class CachedScraper:
    def __init__(self, cache_file="scrape_cache.pkl"):
        self.app = RapidCrawlApp()
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self):
        try:
            with open(self.cache_file, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}
    
    def save_cache(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)
    
    def get_cache_key(self, url, options):
        key_data = f"{url}:{str(sorted(options.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def scrape_with_cache(self, url, max_age_hours=24, **options):
        cache_key = self.get_cache_key(url, options)
        
        # Check cache
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            age_hours = (datetime.now() - cached["time"]).total_seconds() / 3600
            
            if age_hours < max_age_hours:
                print(f"Using cached result for {url}")
                return cached["result"]
        
        # Scrape fresh
        print(f"Scraping fresh content for {url}")
        result = self.app.scrape_url(url, **options)
        
        # Cache result
        self.cache[cache_key] = {
            "result": result,
            "time": datetime.now()
        }
        self.save_cache()
        
        return result
```

### Rate Limiting

```python
import time
from collections import deque

class RateLimitedScraper:
    def __init__(self, requests_per_second=1):
        self.app = RapidCrawlApp()
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.request_times = deque(maxlen=requests_per_second)
    
    def scrape_url(self, url, **kwargs):
        # Check rate limit
        now = time.time()
        
        if len(self.request_times) == self.requests_per_second:
            oldest = self.request_times[0]
            time_passed = now - oldest
            
            if time_passed < 1.0:
                sleep_time = 1.0 - time_passed
                print(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        # Make request
        result = self.app.scrape_url(url, **kwargs)
        self.request_times.append(time.time())
        
        return result

# Usage
scraper = RateLimitedScraper(requests_per_second=2)
for url in urls:
    result = scraper.scrape_url(url)
```

---

## Error Handling

### Comprehensive Error Handling

```python
from rapidcrawl.exceptions import (
    RapidCrawlError,
    ValidationError,
    RateLimitError,
    ScrapingError,
    TimeoutError,
    NetworkError
)

def safe_scrape(url, max_retries=3):
    app = RapidCrawlApp()
    
    for attempt in range(max_retries):
        try:
            result = app.scrape_url(url)
            
            if result.success:
                return result
            else:
                print(f"Scraping failed: {result.error}")
                
        except ValidationError as e:
            print(f"Invalid URL: {e.message}")
            break  # Don't retry validation errors
            
        except RateLimitError as e:
            wait_time = e.retry_after or 60
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except TimeoutError as e:
            print(f"Timeout after {e.timeout}s. Attempt {attempt + 1}/{max_retries}")
            
        except NetworkError as e:
            print(f"Network error: {e.message}. Attempt {attempt + 1}/{max_retries}")
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except RapidCrawlError as e:
            print(f"Unexpected error: {e.message}")
            break
    
    return None

# Usage with fallback
result = safe_scrape("https://example.com")
if not result:
    print("Failed to scrape after all retries")
```

### Logging Errors

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rapidcrawl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('rapidcrawl')

class LoggingScraper:
    def __init__(self):
        self.app = RapidCrawlApp(debug=True)
    
    def scrape_url(self, url):
        logger.info(f"Starting scrape of {url}")
        
        try:
            result = self.app.scrape_url(url)
            
            if result.success:
                logger.info(f"Successfully scraped {url} in {result.load_time:.2f}s")
            else:
                logger.error(f"Failed to scrape {url}: {result.error}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Exception while scraping {url}")
            raise

# Usage
scraper = LoggingScraper()
result = scraper.scrape_url("https://example.com")
```

---

These examples demonstrate the flexibility and power of RapidCrawl for various web scraping and crawling tasks. For more specific use cases or advanced features, refer to the [API documentation](API.md) or [advanced usage guide](ADVANCED.md).