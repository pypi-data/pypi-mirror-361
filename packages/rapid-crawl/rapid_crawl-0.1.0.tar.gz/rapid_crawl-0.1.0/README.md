# RapidCrawl

<p align="center">
  <img src="https://img.shields.io/pypi/v/rapid-crawl.svg" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/rapid-crawl.svg" alt="Python versions">
  <img src="https://img.shields.io/github/license/aoneahsan/rapid-crawl.svg" alt="License">
  <img src="https://img.shields.io/github/stars/aoneahsan/rapid-crawl.svg" alt="Stars">
</p>

A powerful Python SDK for web scraping, crawling, and data extraction. RapidCrawl provides a comprehensive toolkit for extracting data from websites, handling dynamic content, and converting web pages into clean, structured formats suitable for AI and LLM applications.

## 🚀 Features

- **🔍 Scrape**: Convert any URL into clean markdown, HTML, text, or structured data
- **🕷️ Crawl**: Recursively crawl websites with depth control and filtering
- **🗺️ Map**: Quickly discover all URLs on a website
- **🔎 Search**: Web search with automatic result scraping
- **📸 Screenshot**: Capture full-page screenshots
- **🎭 Dynamic Content**: Handle JavaScript-rendered pages with Playwright
- **📄 Multiple Formats**: Support for Markdown, HTML, PDF, images, and more
- **🚄 Async Support**: High-performance asynchronous operations
- **🛡️ Error Handling**: Comprehensive error handling and retry logic
- **📦 CLI Tool**: Feature-rich command-line interface

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Features](#-features-1)
  - [Scraping](#scraping)
  - [Crawling](#crawling)
  - [Mapping](#mapping)
  - [Searching](#searching)
- [CLI Usage](#-cli-usage)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Examples](#-examples)
- [Advanced Usage](#-advanced-usage)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)
- [Support](#-support)

## 📦 Installation

### Using pip

```bash
pip install rapid-crawl
```

### Using pip with all optional dependencies

```bash
pip install rapid-crawl[dev]
```

### From source

```bash
git clone https://github.com/aoneahsan/rapid-crawl.git
cd rapid-crawl
pip install -e .
```

### Install Playwright browsers (required for dynamic content)

```bash
playwright install chromium
```

## 🚀 Quick Start

### Python SDK

```python
from rapidcrawl import RapidCrawlApp

# Initialize the client
app = RapidCrawlApp()

# Scrape a single page
result = app.scrape_url("https://example.com")
print(result.content["markdown"])

# Crawl a website
crawl_result = app.crawl_url(
    "https://example.com",
    max_pages=10,
    max_depth=2
)

# Map all URLs
map_result = app.map_url("https://example.com")
print(f"Found {map_result.total_urls} URLs")

# Search and scrape
search_result = app.search(
    "python web scraping",
    num_results=5,
    scrape_results=True
)
```

### Command Line

```bash
# Scrape a URL
rapidcrawl scrape https://example.com

# Crawl a website
rapidcrawl crawl https://example.com --max-pages 10

# Map URLs
rapidcrawl map https://example.com --limit 100

# Search
rapidcrawl search "python tutorials" --scrape
```

## 🎯 Features

### Scraping

Convert any web page into clean, structured data:

```python
from rapidcrawl import RapidCrawlApp, OutputFormat

app = RapidCrawlApp()

# Basic scraping
result = app.scrape_url("https://example.com")

# Multiple formats
result = app.scrape_url(
    "https://example.com",
    formats=["markdown", "html", "screenshot"],
    wait_for=".content",  # Wait for element
    timeout=60000,        # 60 seconds timeout
)

# Extract structured data
result = app.scrape_url(
    "https://example.com/product",
    extract_schema=[
        {"name": "title", "selector": "h1"},
        {"name": "price", "selector": ".price", "type": "number"},
        {"name": "description", "selector": ".description"}
    ]
)

print(result.structured_data)
# {'title': 'Product Name', 'price': 29.99, 'description': '...'}

# Mobile viewport
result = app.scrape_url(
    "https://example.com",
    mobile=True
)

# With actions (click, type, scroll)
result = app.scrape_url(
    "https://example.com",
    actions=[
        {"type": "click", "selector": ".load-more"},
        {"type": "wait", "value": 2000},
        {"type": "scroll", "value": 1000}
    ]
)
```

### Crawling

Recursively crawl websites with advanced filtering:

```python
# Basic crawling
result = app.crawl_url(
    "https://example.com",
    max_pages=50,
    max_depth=3
)

# With URL filtering
result = app.crawl_url(
    "https://example.com",
    include_patterns=[r"/blog/.*", r"/docs/.*"],
    exclude_patterns=[r".*\.pdf$", r".*/tag/.*"]
)

# Async crawling for better performance
import asyncio

async def crawl_async():
    result = await app.crawl_url_async(
        "https://example.com",
        max_pages=100,
        max_depth=5,
        allow_subdomains=True
    )
    return result

result = asyncio.run(crawl_async())

# With webhook notifications
result = app.crawl_url(
    "https://example.com",
    webhook_url="https://your-webhook.com/progress"
)
```

### Mapping

Quickly discover all URLs on a website:

```python
# Basic mapping
result = app.map_url("https://example.com")
print(f"Found {result.total_urls} URLs")

# Filter URLs by search term
result = app.map_url(
    "https://example.com",
    search="product",
    limit=1000
)

# Include subdomains
result = app.map_url(
    "https://example.com",
    include_subdomains=True,
    ignore_sitemap=False  # Use sitemap.xml if available
)

# Access the URLs
for url in result.urls[:10]:
    print(url)
```

### Searching

Search the web and optionally scrape results:

```python
# Basic search
result = app.search("python web scraping tutorial")

# Search with scraping
result = app.search(
    "latest AI news",
    num_results=10,
    scrape_results=True,
    formats=["markdown", "text"]
)

# Access results
for item in result.results:
    print(f"{item.position}. {item.title}")
    print(f"   URL: {item.url}")
    if item.scraped_content:
        print(f"   Content: {item.scraped_content.content['markdown'][:200]}...")

# Different search engines
result = app.search(
    "machine learning",
    engine="duckduckgo",  # or "google", "bing"
    num_results=20
)

# With date filtering
from datetime import datetime, timedelta

result = app.search(
    "tech news",
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now()
)
```

## 💻 CLI Usage

RapidCrawl provides a comprehensive command-line interface:

### Setup Wizard

```bash
# Interactive setup
rapidcrawl setup
```

### Scraping

```bash
# Basic scrape
rapidcrawl scrape https://example.com

# Save to file
rapidcrawl scrape https://example.com -o output.md

# Multiple formats
rapidcrawl scrape https://example.com -f markdown -f html -f screenshot

# Wait for element
rapidcrawl scrape https://example.com --wait-for ".content"

# Extract structured data
rapidcrawl scrape https://example.com \
  --extract-schema '[{"name": "title", "selector": "h1"}]'
```

### Crawling

```bash
# Basic crawl
rapidcrawl crawl https://example.com

# Advanced crawl
rapidcrawl crawl https://example.com \
  --max-pages 100 \
  --max-depth 3 \
  --include "*/blog/*" \
  --exclude "*.pdf" \
  --output ./crawl-results/
```

### Mapping

```bash
# Map all URLs
rapidcrawl map https://example.com

# Filter and save
rapidcrawl map https://example.com \
  --search "product" \
  --limit 1000 \
  --output urls.txt
```

### Searching

```bash
# Basic search
rapidcrawl search "python tutorials"

# Search and scrape
rapidcrawl search "machine learning" \
  --scrape \
  --num-results 20 \
  --engine google \
  --output results/
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# API Configuration
RAPIDCRAWL_API_KEY=your_api_key_here
RAPIDCRAWL_BASE_URL=https://api.rapidcrawl.io/v1
RAPIDCRAWL_TIMEOUT=30

# Optional
RAPIDCRAWL_MAX_RETRIES=3
```

### Python Configuration

```python
from rapidcrawl import RapidCrawlApp

# Custom configuration
app = RapidCrawlApp(
    api_key="your_api_key",
    base_url="https://custom-api.example.com",
    timeout=60.0,
    max_retries=5,
    debug=True
)
```

### Manual Configuration Options

If the automated setup doesn't work, you can manually configure RapidCrawl:

1. **API Key**: Set via environment variable or pass to constructor
2. **Base URL**: For self-hosted instances
3. **Timeout**: Request timeout in seconds
4. **SSL Verification**: Disable for self-signed certificates
5. **Debug Mode**: Enable verbose logging

## 📚 API Reference

### RapidCrawlApp

The main client class for interacting with RapidCrawl.

#### Constructor

```python
RapidCrawlApp(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    max_retries: Optional[int] = None,
    verify_ssl: bool = True,
    debug: bool = False
)
```

#### Methods

- `scrape_url(url, **options)`: Scrape a single URL
- `crawl_url(url, **options)`: Crawl a website
- `crawl_url_async(url, **options)`: Async crawl
- `map_url(url, **options)`: Map website URLs
- `search(query, **options)`: Search the web
- `extract(urls, schema, prompt)`: Extract structured data

### Models

#### ScrapeOptions

```python
from rapidcrawl.models import ScrapeOptions, OutputFormat

options = ScrapeOptions(
    url="https://example.com",
    formats=[OutputFormat.MARKDOWN, OutputFormat.HTML],
    wait_for=".content",
    timeout=30000,
    mobile=False,
    actions=[...],
    extract_schema=[...],
    headers={"User-Agent": "Custom UA"}
)
```

#### CrawlOptions

```python
from rapidcrawl.models import CrawlOptions

options = CrawlOptions(
    url="https://example.com",
    max_pages=100,
    max_depth=3,
    include_patterns=["*/blog/*"],
    exclude_patterns=["*.pdf"],
    allow_subdomains=False,
    webhook_url="https://webhook.example.com"
)
```

## 🔧 Examples

For comprehensive examples, see the [examples directory](examples/):
- [Basic Scraping](examples/basic_scraping.py) - Getting started with web scraping
- [Web Crawling](examples/web_crawling.py) - Crawling websites recursively
- [Search and Map](examples/search_and_map.py) - Search and URL mapping
- [Data Extraction](examples/data_extraction.py) - Structured data extraction
- [Advanced Usage](examples/advanced_usage.py) - Production patterns

### E-commerce Price Monitoring

```python
from rapidcrawl import RapidCrawlApp
import json

app = RapidCrawlApp()

# Define extraction schema
schema = [
    {"name": "title", "selector": "h1.product-title"},
    {"name": "price", "selector": ".price-now", "type": "number"},
    {"name": "stock", "selector": ".availability"},
    {"name": "image", "selector": "img.product-image", "attribute": "src"}
]

# Monitor multiple products
products = [
    "https://shop.example.com/product1",
    "https://shop.example.com/product2",
]

results = []
for url in products:
    result = app.scrape_url(url, extract_schema=schema)
    if result.success:
        results.append({
            "url": url,
            "data": result.structured_data,
            "timestamp": result.scraped_at
        })

# Save results
with open("prices.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
```

### Content Aggregation

```python
import asyncio
from rapidcrawl import RapidCrawlApp

app = RapidCrawlApp()

async def aggregate_news():
    # Search multiple queries
    queries = [
        "artificial intelligence breakthroughs",
        "quantum computing news",
        "robotics innovation"
    ]
    
    all_articles = []
    
    for query in queries:
        result = app.search(
            query,
            num_results=5,
            scrape_results=True,
            formats=["markdown"]
        )
        
        for item in result.results:
            if item.scraped_content and item.scraped_content.success:
                all_articles.append({
                    "title": item.title,
                    "url": item.url,
                    "content": item.scraped_content.content["markdown"],
                    "query": query
                })
    
    return all_articles

# Run aggregation
articles = asyncio.run(aggregate_news())
```

### Website Change Detection

```python
import hashlib
import time
from rapidcrawl import RapidCrawlApp

app = RapidCrawlApp()

def monitor_changes(url, interval=3600):
    """Monitor a webpage for changes."""
    previous_hash = None
    
    while True:
        result = app.scrape_url(url, formats=["text"])
        
        if result.success:
            content = result.content["text"]
            current_hash = hashlib.md5(content.encode()).hexdigest()
            
            if previous_hash and current_hash != previous_hash:
                print(f"Change detected at {url}!")
                # Send notification, save diff, etc.
            
            previous_hash = current_hash
        
        time.sleep(interval)

# Monitor a page
monitor_changes("https://example.com/status", interval=300)  # Check every 5 minutes
```

## 🚀 Advanced Usage

### Rate Limiting

```python
import time
from rapidcrawl import RapidCrawlApp

class RateLimitedScraper:
    def __init__(self, requests_per_second=2):
        self.app = RapidCrawlApp()
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0
    
    def scrape_url(self, url):
        current = time.time()
        elapsed = current - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_request = time.time()
        return self.app.scrape_url(url)
```

### Caching Results

```python
from functools import lru_cache
import hashlib

class CachedScraper:
    def __init__(self):
        self.app = RapidCrawlApp()
        self.cache = {}
    
    def scrape_with_cache(self, url, max_age_hours=24):
        cache_key = hashlib.md5(url.encode()).hexdigest()
        
        if cache_key in self.cache:
            cached_time, cached_result = self.cache[cache_key]
            age_hours = (time.time() - cached_time) / 3600
            if age_hours < max_age_hours:
                return cached_result
        
        result = self.app.scrape_url(url)
        self.cache[cache_key] = (time.time(), result)
        return result
```

### Error Handling

```python
from rapidcrawl.exceptions import (
    RateLimitError,
    TimeoutError,
    NetworkError
)

def robust_scrape(url, max_retries=3):
    app = RapidCrawlApp()
    
    for attempt in range(max_retries):
        try:
            return app.scrape_url(url)
        except RateLimitError as e:
            wait_time = e.retry_after or 60
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except TimeoutError:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise
        except NetworkError as e:
            print(f"Network error: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Concurrent Scraping

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def concurrent_scrape(urls, max_workers=5):
    app = RapidCrawlApp()
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(app.scrape_url, url): url 
            for url in urls
        }
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = {"error": str(e)}
    
    return results
```

For more advanced patterns, see the [Advanced Usage Guide](docs/ADVANCED.md).

## ⚡ Performance

### Benchmarks

| Operation | URLs | Time | Speed |
|-----------|------|------|-------|
| Sequential Scraping | 10 | 12.3s | 0.8 pages/sec |
| Concurrent Scraping | 10 | 3.1s | 3.2 pages/sec |
| Async Crawling | 100 | 28.5s | 3.5 pages/sec |
| URL Mapping | 1000 | 5.2s | 192 URLs/sec |

### Optimization Tips

1. **Use Async Operations**: For crawling large sites, use `crawl_url_async()`
2. **Enable Connection Pooling**: Reuse HTTP connections
3. **Limit Concurrent Requests**: Prevent overwhelming servers
4. **Cache Results**: Avoid re-scraping unchanged content
5. **Use Specific Formats**: Only request needed output formats

## 🔍 Troubleshooting

### Common Issues

#### Installation Problems
```bash
# Update pip
python -m pip install --upgrade pip

# Install in virtual environment
python -m venv venv
source venv/bin/activate
pip install rapid-crawl
```

#### Playwright Issues
```bash
# Install browser dependencies
playwright install-deps chromium

# Or use Firefox
playwright install firefox
```

#### SSL Certificate Errors
```python
# For self-signed certificates (development only!)
app = RapidCrawlApp(verify_ssl=False)
```

#### Rate Limiting
```python
# Handle rate limits gracefully
try:
    result = app.scrape_url(url)
except RateLimitError as e:
    time.sleep(e.retry_after or 60)
    result = app.scrape_url(url)
```

For detailed troubleshooting, see the [Troubleshooting Guide](docs/TROUBLESHOOTING.md).

## 🛠️ Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/aoneahsan/rapid-crawl.git
cd rapid-crawl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rapidcrawl

# Run specific test file
pytest tests/test_scrape.py
```

### Code formatting

```bash
# Format code
black src/rapidcrawl

# Run linter
ruff check src/rapidcrawl

# Type checking
mypy src/rapidcrawl
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Follow PEP 8 style guide
- Update documentation
- Add type hints
- Run tests before submitting

## 🔒 Security

Security is important to us. Please see our [Security Policy](SECURITY.md) for details on:
- Reporting vulnerabilities
- Security best practices
- API key management
- Data privacy

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

### Documentation

- 📖 [Full Documentation](docs/)
- 🚀 [API Reference](docs/API.md)
- 💡 [Examples](docs/EXAMPLES.md)
- 🔧 [Advanced Usage](docs/ADVANCED.md)
- ❓ [Troubleshooting](docs/TROUBLESHOOTING.md)

### Community

- 🐛 [Report Issues](https://github.com/aoneahsan/rapid-crawl/issues)
- 💬 [Discussions](https://github.com/aoneahsan/rapid-crawl/discussions)
- 📧 [Email Support](mailto:aoneahsan@gmail.com)

### Resources

- 📝 [Changelog](CHANGELOG.md)
- 🔒 [Security Policy](SECURITY.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)
- ⚖️ [License](LICENSE)

## 👨‍💻 Developer

**Ahsan Mahmood**

- 🌐 Website: [https://aoneahsan.com](https://aoneahsan.com)
- 📧 Email: [aoneahsan@gmail.com](mailto:aoneahsan@gmail.com)
- 💼 LinkedIn: [https://linkedin.com/in/aoneahsan](https://linkedin.com/in/aoneahsan)
- 🐦 Twitter: [@aoneahsan](https://twitter.com/aoneahsan)

## 🙏 Acknowledgments

- Inspired by [Firecrawl](https://www.firecrawl.dev/)
- Built with [Playwright](https://playwright.dev/) for dynamic content handling
- Uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Click](https://click.palletsprojects.com/) for the CLI interface
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output

## 📊 Statistics

![GitHub Stars](https://img.shields.io/github/stars/aoneahsan/rapid-crawl?style=social)
![GitHub Forks](https://img.shields.io/github/forks/aoneahsan/rapid-crawl?style=social)
![PyPI Downloads](https://img.shields.io/pypi/dm/rapid-crawl)
![GitHub Issues](https://img.shields.io/github/issues/aoneahsan/rapid-crawl)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/aoneahsan/rapid-crawl)

---

<p align="center">
  <strong>RapidCrawl</strong> - Fast, reliable web scraping for Python<br>
  Made with ❤️ by <a href="https://aoneahsan.com">Ahsan Mahmood</a>
</p>

<p align="center">
  <a href="https://github.com/aoneahsan/rapid-crawl/stargazers">⭐ Star us on GitHub</a> •
  <a href="https://pypi.org/project/rapid-crawl/">📦 Install from PyPI</a> •
  <a href="https://github.com/aoneahsan/rapid-crawl/issues/new/choose">🐛 Report a Bug</a>
</p>