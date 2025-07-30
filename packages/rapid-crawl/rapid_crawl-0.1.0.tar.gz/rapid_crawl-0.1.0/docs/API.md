# RapidCrawl API Reference

This document provides a comprehensive reference for the RapidCrawl Python API.

## Table of Contents

- [Client](#client)
  - [RapidCrawlApp](#rapidcrawlapp)
- [Methods](#methods)
  - [scrape_url](#scrape_url)
  - [crawl_url](#crawl_url)
  - [crawl_url_async](#crawl_url_async)
  - [map_url](#map_url)
  - [search](#search)
  - [extract](#extract)
- [Models](#models)
  - [ScrapeOptions](#scrapeoptions)
  - [CrawlOptions](#crawloptions)
  - [MapOptions](#mapoptions)
  - [SearchOptions](#searchoptions)
  - [Result Models](#result-models)
- [Exceptions](#exceptions)
- [Enums](#enums)
- [Utilities](#utilities)

---

## Client

### RapidCrawlApp

The main client class for interacting with RapidCrawl.

```python
from rapidcrawl import RapidCrawlApp

app = RapidCrawlApp(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    max_retries: Optional[int] = None,
    verify_ssl: bool = True,
    debug: bool = False
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `Optional[str]` | `None` | API key for authentication. If not provided, looks for `RAPIDCRAWL_API_KEY` env var |
| `base_url` | `Optional[str]` | `"https://api.rapidcrawl.io/v1"` | Base URL for API endpoint |
| `timeout` | `Optional[float]` | `30.0` | Request timeout in seconds |
| `max_retries` | `Optional[int]` | `3` | Maximum number of retry attempts |
| `verify_ssl` | `bool` | `True` | Whether to verify SSL certificates |
| `debug` | `bool` | `False` | Enable debug mode with verbose logging |

#### Example

```python
# Basic initialization
app = RapidCrawlApp()

# With custom configuration
app = RapidCrawlApp(
    api_key="your-api-key",
    timeout=60.0,
    debug=True
)

# Using context manager
with RapidCrawlApp() as app:
    result = app.scrape_url("https://example.com")
```

---

## Methods

### scrape_url

Scrape a single URL and convert it to specified formats.

```python
def scrape_url(
    self,
    url: str,
    formats: Optional[List[Union[str, OutputFormat]]] = None,
    **kwargs
) -> ScrapeResult
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | *required* | The URL to scrape |
| `formats` | `Optional[List[Union[str, OutputFormat]]]` | `["markdown"]` | Output formats |
| `**kwargs` | | | Additional options (see [ScrapeOptions](#scrapeoptions)) |

#### Returns

Returns a [`ScrapeResult`](#scraperesult) object.

#### Example

```python
# Basic scraping
result = app.scrape_url("https://example.com")

# Multiple formats with options
result = app.scrape_url(
    "https://example.com",
    formats=["markdown", "html", "screenshot"],
    wait_for=".content",
    timeout=60000,
    mobile=True
)

# With structured extraction
result = app.scrape_url(
    "https://example.com/product",
    extract_schema=[
        {"name": "title", "selector": "h1"},
        {"name": "price", "selector": ".price", "type": "number"}
    ]
)
```

### crawl_url

Crawl a website starting from the given URL.

```python
def crawl_url(
    self,
    url: str,
    max_pages: Optional[int] = None,
    max_depth: Optional[int] = None,
    **kwargs
) -> CrawlResult
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | *required* | Starting URL for crawling |
| `max_pages` | `Optional[int]` | `100` | Maximum pages to crawl |
| `max_depth` | `Optional[int]` | `3` | Maximum crawl depth |
| `**kwargs` | | | Additional options (see [CrawlOptions](#crawloptions)) |

#### Returns

Returns a [`CrawlResult`](#crawlresult) object.

#### Example

```python
# Basic crawling
result = app.crawl_url("https://example.com")

# Advanced crawling
result = app.crawl_url(
    "https://example.com",
    max_pages=50,
    max_depth=2,
    include_patterns=[r"/blog/.*"],
    exclude_patterns=[r".*\.pdf$"],
    allow_subdomains=True
)
```

### crawl_url_async

Asynchronously crawl a website for better performance.

```python
async def crawl_url_async(
    self,
    url: str,
    max_pages: Optional[int] = None,
    max_depth: Optional[int] = None,
    **kwargs
) -> CrawlResult
```

Parameters and returns are the same as [`crawl_url`](#crawl_url).

#### Example

```python
import asyncio

async def main():
    async with RapidCrawlApp() as app:
        result = await app.crawl_url_async(
            "https://example.com",
            max_pages=100
        )
    return result

result = asyncio.run(main())
```

### map_url

Map all URLs from a website.

```python
def map_url(
    self,
    url: str,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    **kwargs
) -> MapResult
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | *required* | Website URL to map |
| `search` | `Optional[str]` | `None` | Filter URLs by search term |
| `limit` | `Optional[int]` | `5000` | Maximum URLs to return |
| `**kwargs` | | | Additional options (see [MapOptions](#mapoptions)) |

#### Returns

Returns a [`MapResult`](#mapresult) object.

#### Example

```python
# Basic mapping
result = app.map_url("https://example.com")

# With filtering
result = app.map_url(
    "https://example.com",
    search="product",
    limit=1000,
    include_subdomains=True
)
```

### search

Search the web and optionally scrape results.

```python
def search(
    self,
    query: str,
    num_results: Optional[int] = None,
    scrape_results: bool = False,
    **kwargs
) -> SearchResult
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | *required* | Search query |
| `num_results` | `Optional[int]` | `10` | Number of results |
| `scrape_results` | `bool` | `False` | Scrape content from results |
| `**kwargs` | | | Additional options (see [SearchOptions](#searchoptions)) |

#### Returns

Returns a [`SearchResult`](#searchresult) object.

#### Example

```python
# Basic search
result = app.search("python web scraping")

# Search with scraping
result = app.search(
    "latest AI news",
    num_results=20,
    scrape_results=True,
    engine="google",
    formats=["markdown"]
)
```

### extract

Extract structured data from one or more URLs.

```python
def extract(
    self,
    urls: Union[str, List[str]],
    schema: Optional[List[Dict[str, Any]]] = None,
    prompt: Optional[str] = None,
    **kwargs
) -> Union[ScrapeResult, List[ScrapeResult]]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `urls` | `Union[str, List[str]]` | *required* | URL(s) to extract from |
| `schema` | `Optional[List[Dict[str, Any]]]` | `None` | Extraction schema |
| `prompt` | `Optional[str]` | `None` | Natural language prompt |
| `**kwargs` | | | Additional scraping options |

#### Returns

Returns a single `ScrapeResult` for one URL or a list for multiple URLs.

#### Example

```python
# Single URL extraction
schema = [
    {"name": "title", "selector": "h1"},
    {"name": "price", "selector": ".price", "type": "number"},
    {"name": "image", "selector": "img", "attribute": "src"}
]

result = app.extract("https://example.com/product", schema=schema)
print(result.structured_data)

# Multiple URLs
urls = ["https://example.com/p1", "https://example.com/p2"]
results = app.extract(urls, schema=schema)
```

---

## Models

### ScrapeOptions

Configuration options for scraping operations.

```python
from rapidcrawl.models import ScrapeOptions, OutputFormat

options = ScrapeOptions(
    url="https://example.com",
    formats=[OutputFormat.MARKDOWN],
    headers=None,
    include_links=False,
    include_images=False,
    wait_for=None,
    timeout=30000,
    actions=None,
    extract_schema=None,
    extract_prompt=None,
    mobile=False,
    location=None,
    language=None,
    remove_tags=None,
    only_main_content=True
)
```

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | `HttpUrl` | *required* | URL to scrape |
| `formats` | `List[OutputFormat]` | `[OutputFormat.MARKDOWN]` | Output formats |
| `headers` | `Optional[Dict[str, str]]` | `None` | Custom HTTP headers |
| `include_links` | `bool` | `False` | Include all links found |
| `include_images` | `bool` | `False` | Include image URLs |
| `wait_for` | `Optional[str]` | `None` | CSS selector to wait for |
| `timeout` | `int` | `30000` | Timeout in milliseconds |
| `actions` | `Optional[List[PageAction]]` | `None` | Page actions to perform |
| `extract_schema` | `Optional[List[ExtractSchema]]` | `None` | Extraction schema |
| `extract_prompt` | `Optional[str]` | `None` | Natural language prompt |
| `mobile` | `bool` | `False` | Use mobile viewport |
| `location` | `Optional[str]` | `None` | Geographic location |
| `language` | `Optional[str]` | `None` | Language preference |
| `remove_tags` | `Optional[List[str]]` | `None` | HTML tags to remove |
| `only_main_content` | `bool` | `True` | Extract only main content |

### CrawlOptions

Configuration options for crawling operations.

```python
from rapidcrawl.models import CrawlOptions

options = CrawlOptions(
    url="https://example.com",
    max_depth=3,
    max_pages=100,
    include_patterns=None,
    exclude_patterns=None,
    allow_subdomains=False,
    formats=[OutputFormat.MARKDOWN],
    headers=None,
    wait_for=None,
    timeout=30000,
    webhook_url=None,
    extract_schema=None,
    limit_rate=None
)
```

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | `HttpUrl` | *required* | Starting URL |
| `max_depth` | `int` | `3` | Maximum crawl depth (1-10) |
| `max_pages` | `int` | `100` | Maximum pages (1-10000) |
| `include_patterns` | `Optional[List[str]]` | `None` | URL patterns to include |
| `exclude_patterns` | `Optional[List[str]]` | `None` | URL patterns to exclude |
| `allow_subdomains` | `bool` | `False` | Allow crawling subdomains |
| `formats` | `List[OutputFormat]` | `[OutputFormat.MARKDOWN]` | Output formats |
| `webhook_url` | `Optional[HttpUrl]` | `None` | Progress webhook URL |
| `limit_rate` | `Optional[int]` | `None` | Rate limit (requests/sec) |

### MapOptions

Configuration options for mapping operations.

```python
from rapidcrawl.models import MapOptions

options = MapOptions(
    url="https://example.com",
    search=None,
    ignore_sitemap=False,
    include_subdomains=False,
    limit=5000
)
```

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | `HttpUrl` | *required* | Website URL to map |
| `search` | `Optional[str]` | `None` | Filter URLs by term |
| `ignore_sitemap` | `bool` | `False` | Ignore sitemap.xml |
| `include_subdomains` | `bool` | `False` | Include subdomain URLs |
| `limit` | `int` | `5000` | Maximum URLs (1-50000) |

### SearchOptions

Configuration options for search operations.

```python
from rapidcrawl.models import SearchOptions, SearchEngine

options = SearchOptions(
    query="search query",
    engine=SearchEngine.GOOGLE,
    num_results=10,
    start_date=None,
    end_date=None,
    location=None,
    language=None,
    scrape_results=False,
    formats=[OutputFormat.MARKDOWN],
    timeout=30000
)
```

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | `str` | *required* | Search query |
| `engine` | `SearchEngine` | `SearchEngine.GOOGLE` | Search engine |
| `num_results` | `int` | `10` | Number of results (1-100) |
| `start_date` | `Optional[datetime]` | `None` | Filter after date |
| `end_date` | `Optional[datetime]` | `None` | Filter before date |
| `location` | `Optional[str]` | `None` | Geographic location |
| `language` | `Optional[str]` | `None` | Language preference |
| `scrape_results` | `bool` | `False` | Scrape result content |
| `formats` | `List[OutputFormat]` | `[OutputFormat.MARKDOWN]` | Scraping formats |

## Result Models

### ScrapeResult

Result from a scraping operation.

```python
class ScrapeResult:
    success: bool
    url: str
    title: Optional[str]
    description: Optional[str]
    content: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    links: Optional[List[str]]
    images: Optional[List[str]]
    structured_data: Optional[Dict[str, Any]]
    error: Optional[str]
    status_code: Optional[int]
    load_time: Optional[float]
    scraped_at: datetime
```

### CrawlResult

Result from a crawling operation.

```python
class CrawlResult:
    job_id: str
    status: CrawlStatus
    url: str
    pages: List[ScrapeResult]
    total_pages: int
    pages_crawled: int
    pages_failed: int
    duration: float
    started_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]
```

### MapResult

Result from a mapping operation.

```python
class MapResult:
    success: bool
    url: str
    urls: List[str]
    total_urls: int
    sitemap_found: bool
    duration: float
    mapped_at: datetime
```

### SearchResult

Result from a search operation.

```python
class SearchResult:
    success: bool
    query: str
    engine: SearchEngine
    results: List[SearchResultItem]
    total_results: int
    duration: float
    searched_at: datetime
```

### SearchResultItem

Individual search result item.

```python
class SearchResultItem:
    title: str
    url: str
    snippet: str
    position: int
    scraped_content: Optional[ScrapeResult]
```

---

## Exceptions

### Exception Hierarchy

```
RapidCrawlError (base)
├── AuthenticationError
├── RateLimitError
├── ScrapingError
├── ValidationError
├── TimeoutError
├── NetworkError
└── ConfigurationError
```

### Usage Example

```python
from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import (
    RateLimitError,
    ScrapingError,
    ValidationError
)

app = RapidCrawlApp()

try:
    result = app.scrape_url("https://example.com")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except ScrapingError as e:
    print(f"Scraping failed: {e.message}")
    print(f"URL: {e.url}, Status: {e.status_code}")
```

---

## Enums

### OutputFormat

Available output formats for scraping.

```python
from rapidcrawl.models import OutputFormat

class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    RAW_HTML = "rawHtml"
    SCREENSHOT = "screenshot"
    LINKS = "links"
    TEXT = "text"
    STRUCTURED = "structured"
```

### CrawlStatus

Status values for crawl operations.

```python
from rapidcrawl.models import CrawlStatus

class CrawlStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### SearchEngine

Available search engines.

```python
from rapidcrawl.models import SearchEngine

class SearchEngine(str, Enum):
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
```

---

## Utilities

### PageAction

Actions to perform on a page during scraping.

```python
from rapidcrawl.models import PageAction

# Click action
action = PageAction(
    type="click",
    selector=".button",
    timeout=5000
)

# Wait action
action = PageAction(
    type="wait",
    value=2000  # milliseconds
)

# Write action
action = PageAction(
    type="write",
    selector="input[name='search']",
    value="search text"
)

# Scroll action
action = PageAction(
    type="scroll",
    value=500  # pixels
)
```

### ExtractSchema

Schema for structured data extraction.

```python
from rapidcrawl.models import ExtractSchema

schema = ExtractSchema(
    name="price",
    type="number",
    selector=".price",
    attribute=None,
    regex=r"[\d.]+",
    required=True,
    default=0
)
```

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *required* | Field name |
| `type` | `Literal["string", "number", "boolean", "array", "object"]` | `"string"` | Data type |
| `selector` | `Optional[str]` | `None` | CSS selector |
| `attribute` | `Optional[str]` | `None` | HTML attribute |
| `regex` | `Optional[str]` | `None` | Regex pattern |
| `required` | `bool` | `True` | Is field required |
| `default` | `Optional[Any]` | `None` | Default value |

---

## Advanced Usage

### Custom Headers

```python
result = app.scrape_url(
    "https://api.example.com",
    headers={
        "Authorization": "Bearer token",
        "X-Custom-Header": "value"
    }
)
```

### Error Handling with Retries

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def scrape_with_retry(url):
    return app.scrape_url(url)
```

### Batch Processing

```python
import asyncio
from typing import List

async def batch_scrape(urls: List[str]):
    tasks = []
    for url in urls:
        task = asyncio.create_task(
            app.scraper.scrape_async(url)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Progress Tracking

```python
def crawl_with_progress(url: str):
    result = app.crawl_url(
        url,
        webhook_url="https://your-server.com/webhook"
    )
    
    # Webhook will receive CrawlProgress updates
    return result
```