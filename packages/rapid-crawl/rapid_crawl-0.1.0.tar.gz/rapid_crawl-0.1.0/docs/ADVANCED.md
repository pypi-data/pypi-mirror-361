# RapidCrawl Advanced Usage Guide

This guide covers advanced features and techniques for power users of RapidCrawl.

## Table of Contents

- [Custom Scrapers](#custom-scrapers)
- [Advanced Crawling Strategies](#advanced-crawling-strategies)
- [Performance Optimization](#performance-optimization)
- [Distributed Scraping](#distributed-scraping)
- [Custom Data Extractors](#custom-data-extractors)
- [Integration Patterns](#integration-patterns)
- [Extending RapidCrawl](#extending-rapidcrawl)
- [Production Deployment](#production-deployment)

---

## Custom Scrapers

### Building a Custom Scraper Class

```python
from rapidcrawl import RapidCrawlApp
from rapidcrawl.models import ScrapeOptions, ScrapeResult
from typing import List, Dict, Any
import json

class CustomScraper:
    """Advanced scraper with custom logic."""
    
    def __init__(self, config_file: str = None):
        self.app = RapidCrawlApp()
        self.config = self._load_config(config_file)
        self.session_data = {}
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load scraping configuration from file."""
        if config_file:
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def scrape_with_session(self, url: str, session_id: str) -> ScrapeResult:
        """Scrape with session management."""
        # Get session cookies
        cookies = self.session_data.get(session_id, {})
        
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
        }
        
        result = self.app.scrape_url(url, headers=headers)
        
        # Update session data from response
        # (In real implementation, parse Set-Cookie headers)
        
        return result
    
    def scrape_with_preprocessing(self, url: str) -> ScrapeResult:
        """Scrape with URL preprocessing."""
        # Transform URL based on rules
        if "mobile." not in url and self.config.get("force_mobile"):
            url = url.replace("www.", "mobile.")
        
        # Add tracking parameters
        if "?" in url:
            url += "&"
        else:
            url += "?"
        url += "utm_source=rapidcrawl"
        
        return self.app.scrape_url(url)
    
    def scrape_with_fallback(self, url: str, strategies: List[Dict]) -> ScrapeResult:
        """Try multiple scraping strategies."""
        last_error = None
        
        for strategy in strategies:
            try:
                result = self.app.scrape_url(url, **strategy)
                if result.success:
                    return result
            except Exception as e:
                last_error = e
                continue
        
        # All strategies failed
        return ScrapeResult(
            success=False,
            url=url,
            error=f"All strategies failed. Last error: {last_error}"
        )
```

### Advanced Extraction Pipeline

```python
from bs4 import BeautifulSoup
import re
from typing import Optional

class DataExtractor:
    """Advanced data extraction with multiple strategies."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self.extractors = {
            'json_ld': self._extract_json_ld,
            'microdata': self._extract_microdata,
            'opengraph': self._extract_opengraph,
            'custom': self._extract_custom
        }
    
    def extract_all(self, url: str) -> Dict[str, Any]:
        """Extract data using all available methods."""
        result = self.app.scrape_url(url, formats=["html"])
        
        if not result.success:
            return {"error": result.error}
        
        soup = BeautifulSoup(result.content["html"], "html.parser")
        extracted_data = {}
        
        for name, extractor in self.extractors.items():
            try:
                data = extractor(soup)
                if data:
                    extracted_data[name] = data
            except Exception as e:
                extracted_data[f"{name}_error"] = str(e)
        
        return extracted_data
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract JSON-LD structured data."""
        scripts = soup.find_all('script', type='application/ld+json')
        data = []
        
        for script in scripts:
            try:
                json_data = json.loads(script.string)
                data.append(json_data)
            except:
                continue
        
        return data if data else None
    
    def _extract_microdata(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract microdata (schema.org)."""
        items = soup.find_all(attrs={"itemscope": True})
        data = []
        
        for item in items:
            item_data = {
                "type": item.get("itemtype"),
                "properties": {}
            }
            
            props = item.find_all(attrs={"itemprop": True})
            for prop in props:
                name = prop.get("itemprop")
                value = prop.get("content") or prop.get_text(strip=True)
                item_data["properties"][name] = value
            
            data.append(item_data)
        
        return data if data else None
    
    def _extract_opengraph(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract Open Graph metadata."""
        og_tags = soup.find_all("meta", property=re.compile(r"^og:"))
        data = {}
        
        for tag in og_tags:
            property_name = tag.get("property").replace("og:", "")
            data[property_name] = tag.get("content")
        
        return data if data else None
    
    def _extract_custom(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Custom extraction logic."""
        # Implement your custom extraction
        return None
```

---

## Advanced Crawling Strategies

### Intelligent Crawl Queue Management

```python
import heapq
from urllib.parse import urlparse
from collections import defaultdict

class SmartCrawler:
    """Crawler with intelligent URL prioritization."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self.url_scores = defaultdict(float)
    
    def calculate_url_score(self, url: str, parent_score: float = 0) -> float:
        """Calculate priority score for URL."""
        score = parent_score * 0.8  # Decay parent score
        
        # Boost certain patterns
        if '/product/' in url:
            score += 10
        elif '/category/' in url:
            score += 5
        elif '/blog/' in url:
            score += 3
        
        # Penalize deep URLs
        depth = len(urlparse(url).path.split('/'))
        score -= depth * 0.5
        
        # Penalize query parameters
        if '?' in url:
            score -= 2
        
        return score
    
    async def smart_crawl(self, start_url: str, max_pages: int = 100):
        """Crawl with intelligent prioritization."""
        visited = set()
        queue = [(0, start_url)]  # Priority queue (score, url)
        results = []
        
        while queue and len(results) < max_pages:
            # Get highest priority URL
            neg_score, url = heapq.heappop(queue)
            score = -neg_score
            
            if url in visited:
                continue
            
            visited.add(url)
            
            # Scrape page
            result = self.app.scrape_url(url, include_links=True)
            
            if result.success:
                results.append(result)
                
                # Add new URLs to queue with scores
                for link in (result.links or []):
                    if link not in visited:
                        link_score = self.calculate_url_score(link, score)
                        heapq.heappush(queue, (-link_score, link))
        
        return results
```

### Adaptive Crawling

```python
class AdaptiveCrawler:
    """Crawler that adapts based on site structure."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self.site_patterns = {}
        self.success_rates = defaultdict(lambda: {"success": 0, "total": 0})
    
    def learn_site_structure(self, sample_urls: List[str]):
        """Learn site structure from sample URLs."""
        for url in sample_urls:
            result = self.app.scrape_url(url, include_links=True)
            
            if result.success:
                # Analyze URL patterns
                domain = urlparse(url).netloc
                patterns = self._extract_patterns(result.links or [])
                
                if domain not in self.site_patterns:
                    self.site_patterns[domain] = set()
                
                self.site_patterns[domain].update(patterns)
    
    def _extract_patterns(self, urls: List[str]) -> Set[str]:
        """Extract URL patterns."""
        patterns = set()
        
        for url in urls:
            # Extract path pattern
            path = urlparse(url).path
            # Replace numbers with placeholders
            pattern = re.sub(r'/\d+', '/{id}', path)
            pattern = re.sub(r'-\d+', '-{id}', pattern)
            patterns.add(pattern)
        
        return patterns
    
    def adaptive_crawl(self, start_url: str, max_pages: int = 100):
        """Crawl adapting to site structure."""
        domain = urlparse(start_url).netloc
        
        # Start with standard crawl
        result = self.app.crawl_url(
            start_url,
            max_pages=min(20, max_pages)  # Initial sample
        )
        
        # Learn from initial results
        if result.pages:
            successful_patterns = []
            
            for page in result.pages:
                pattern = self._get_url_pattern(page.url)
                self.success_rates[pattern]["total"] += 1
                
                if page.success:
                    self.success_rates[pattern]["success"] += 1
                    successful_patterns.append(pattern)
        
        # Continue crawling focusing on successful patterns
        if max_pages > 20:
            # Build include patterns based on success rates
            include_patterns = []
            
            for pattern, stats in self.success_rates.items():
                if stats["total"] > 0:
                    success_rate = stats["success"] / stats["total"]
                    if success_rate > 0.8:  # 80% success rate
                        # Convert pattern back to regex
                        regex_pattern = pattern.replace("{id}", r"\d+")
                        include_patterns.append(regex_pattern)
            
            # Continue crawling with learned patterns
            if include_patterns:
                result2 = self.app.crawl_url(
                    start_url,
                    max_pages=max_pages - 20,
                    include_patterns=include_patterns
                )
                
                # Combine results
                result.pages.extend(result2.pages)
        
        return result
    
    def _get_url_pattern(self, url: str) -> str:
        """Get URL pattern."""
        path = urlparse(url).path
        pattern = re.sub(r'/\d+', '/{id}', path)
        pattern = re.sub(r'-\d+', '-{id}', pattern)
        return pattern
```

---

## Performance Optimization

### Connection Pooling and Reuse

```python
import httpx
from contextlib import asynccontextmanager

class OptimizedScraper:
    """Scraper with connection pooling."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self._client = None
        self._async_client = None
    
    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0
                ),
                timeout=httpx.Timeout(30.0),
                http2=True  # Enable HTTP/2
            )
        return self._client
    
    @asynccontextmanager
    async def async_client(self):
        """Async client context manager."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100
                ),
                timeout=httpx.Timeout(30.0),
                http2=True
            )
        
        try:
            yield self._async_client
        finally:
            pass  # Keep connection alive
    
    async def batch_scrape_optimized(
        self,
        urls: List[str],
        batch_size: int = 10
    ) -> List[ScrapeResult]:
        """Optimized batch scraping."""
        results = []
        
        async with self.async_client() as client:
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                
                # Create tasks for batch
                tasks = [
                    self._scrape_with_client(client, url)
                    for url in batch
                ]
                
                # Execute batch concurrently
                batch_results = await asyncio.gather(
                    *tasks,
                    return_exceptions=True
                )
                
                results.extend(batch_results)
        
        return results
    
    async def _scrape_with_client(
        self,
        client: httpx.AsyncClient,
        url: str
    ) -> ScrapeResult:
        """Scrape using existing client."""
        try:
            response = await client.get(url)
            # Process response...
            return ScrapeResult(
                success=True,
                url=url,
                content={"text": response.text}
            )
        except Exception as e:
            return ScrapeResult(
                success=False,
                url=url,
                error=str(e)
            )
```

### Memory-Efficient Large Crawls

```python
import gc
import psutil
from typing import Iterator

class MemoryEfficientCrawler:
    """Crawler optimized for memory usage."""
    
    def __init__(self, memory_limit_mb: int = 1024):
        self.app = RapidCrawlApp()
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
    
    def stream_crawl(
        self,
        start_url: str,
        max_pages: int = 10000
    ) -> Iterator[ScrapeResult]:
        """Stream crawl results without storing all in memory."""
        visited = set()
        queue = deque([start_url])
        pages_crawled = 0
        
        while queue and pages_crawled < max_pages:
            # Check memory usage
            if self._check_memory_usage():
                self._cleanup_memory()
            
            url = queue.popleft()
            
            if url in visited:
                continue
            
            visited.add(url)
            
            # Scrape page
            result = self.app.scrape_url(url, include_links=True)
            
            if result.success:
                pages_crawled += 1
                
                # Add new URLs to queue
                for link in (result.links or [])[:10]:  # Limit new URLs
                    if link not in visited:
                        queue.append(link)
                
                # Clear large data from result before yielding
                if result.content and "html" in result.content:
                    # Keep only essential data
                    result.content = {
                        "markdown": result.content.get("markdown", "")[:1000]
                    }
                
                yield result
            
            # Periodic cleanup
            if pages_crawled % 100 == 0:
                visited = set(list(visited)[-1000:])  # Keep only recent
    
    def _check_memory_usage(self) -> bool:
        """Check if memory usage is too high."""
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss > self.memory_limit_bytes
    
    def _cleanup_memory(self):
        """Force memory cleanup."""
        gc.collect()
        
        # Additional cleanup for large objects
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
```

---

## Distributed Scraping

### Multi-Process Scraping

```python
from multiprocessing import Pool, Queue, Process
import queue

class DistributedScraper:
    """Scraper using multiple processes."""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
    
    def scrape_parallel(self, urls: List[str]) -> List[ScrapeResult]:
        """Scrape URLs in parallel using multiple processes."""
        with Pool(processes=self.num_workers) as pool:
            results = pool.map(self._scrape_single, urls)
        
        return results
    
    @staticmethod
    def _scrape_single(url: str) -> ScrapeResult:
        """Scrape single URL (runs in separate process)."""
        app = RapidCrawlApp()  # Create new instance per process
        return app.scrape_url(url)
    
    def distributed_crawl(self, start_url: str, max_pages: int = 1000):
        """Distributed crawling with work queue."""
        # Queues for communication
        url_queue = Queue()
        result_queue = Queue()
        
        # Start with initial URL
        url_queue.put(start_url)
        
        # Start worker processes
        workers = []
        for i in range(self.num_workers):
            p = Process(
                target=self._crawl_worker,
                args=(i, url_queue, result_queue, max_pages // self.num_workers)
            )
            p.start()
            workers.append(p)
        
        # Collect results
        results = []
        visited = set()
        
        while len(results) < max_pages:
            try:
                result = result_queue.get(timeout=30)
                results.append(result)
                
                # Add new URLs to queue
                if result.success and result.links:
                    for link in result.links:
                        if link not in visited:
                            visited.add(link)
                            url_queue.put(link)
            
            except queue.Empty:
                break
        
        # Stop workers
        for _ in workers:
            url_queue.put(None)
        
        for p in workers:
            p.join()
        
        return results
    
    @staticmethod
    def _crawl_worker(
        worker_id: int,
        url_queue: Queue,
        result_queue: Queue,
        max_pages: int
    ):
        """Worker process for crawling."""
        app = RapidCrawlApp()
        pages_crawled = 0
        
        while pages_crawled < max_pages:
            try:
                url = url_queue.get(timeout=10)
                
                if url is None:  # Shutdown signal
                    break
                
                result = app.scrape_url(url, include_links=True)
                result_queue.put(result)
                pages_crawled += 1
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
```

### Redis-Based Task Queue

```python
import redis
import json
from typing import Optional

class RedisQueueScraper:
    """Distributed scraper using Redis."""
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379
    ):
        self.app = RapidCrawlApp()
        self.redis = redis.Redis(host=redis_host, port=redis_port)
        self.queue_key = "rapidcrawl:urls"
        self.results_key = "rapidcrawl:results"
        self.visited_key = "rapidcrawl:visited"
    
    def add_urls(self, urls: List[str]):
        """Add URLs to scraping queue."""
        for url in urls:
            self.redis.lpush(self.queue_key, url)
    
    def worker(self, worker_id: str):
        """Worker process that consumes from queue."""
        while True:
            # Get URL from queue (blocking)
            url = self.redis.brpop(self.queue_key, timeout=30)
            
            if not url:
                continue
            
            url = url[1].decode('utf-8')
            
            # Check if already visited
            if self.redis.sismember(self.visited_key, url):
                continue
            
            # Mark as visited
            self.redis.sadd(self.visited_key, url)
            
            try:
                # Scrape URL
                result = self.app.scrape_url(url, include_links=True)
                
                # Store result
                result_data = {
                    "url": url,
                    "success": result.success,
                    "title": result.title,
                    "content_length": len(result.content.get("text", "")),
                    "links_count": len(result.links or []),
                    "worker_id": worker_id
                }
                
                self.redis.lpush(
                    self.results_key,
                    json.dumps(result_data)
                )
                
                # Add new URLs to queue
                if result.success and result.links:
                    for link in result.links[:10]:  # Limit
                        if not self.redis.sismember(self.visited_key, link):
                            self.redis.lpush(self.queue_key, link)
            
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
    
    def get_results(self, count: int = 100) -> List[Dict]:
        """Get results from Redis."""
        results = []
        
        for _ in range(count):
            result = self.redis.rpop(self.results_key)
            if result:
                results.append(json.loads(result))
            else:
                break
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get scraping statistics."""
        return {
            "queue_size": self.redis.llen(self.queue_key),
            "results_count": self.redis.llen(self.results_key),
            "visited_count": self.redis.scard(self.visited_key)
        }
```

---

## Custom Data Extractors

### Machine Learning Extractor

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class MLDataExtractor:
    """Extract data using machine learning."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self.vectorizer = TfidfVectorizer(max_features=100)
    
    def extract_similar_pages(
        self,
        urls: List[str],
        num_clusters: int = 5
    ) -> Dict[int, List[str]]:
        """Cluster similar pages."""
        # Scrape all pages
        contents = []
        valid_urls = []
        
        for url in urls:
            result = self.app.scrape_url(url, formats=["text"])
            if result.success:
                contents.append(result.content["text"])
                valid_urls.append(url)
        
        if not contents:
            return {}
        
        # Vectorize content
        vectors = self.vectorizer.fit_transform(contents)
        
        # Cluster pages
        kmeans = KMeans(n_clusters=min(num_clusters, len(contents)))
        clusters = kmeans.fit_predict(vectors)
        
        # Group URLs by cluster
        clustered_urls = defaultdict(list)
        for url, cluster in zip(valid_urls, clusters):
            clustered_urls[int(cluster)].append(url)
        
        return dict(clustered_urls)
    
    def extract_key_information(
        self,
        url: str,
        keywords: List[str]
    ) -> Dict[str, List[str]]:
        """Extract sentences containing keywords."""
        result = self.app.scrape_url(url, formats=["text"])
        
        if not result.success:
            return {}
        
        text = result.content["text"]
        sentences = text.split('.')
        
        extracted = defaultdict(list)
        
        for keyword in keywords:
            for sentence in sentences:
                if keyword.lower() in sentence.lower():
                    extracted[keyword].append(sentence.strip())
        
        return dict(extracted)
```

### Template-Based Extractor

```python
class TemplateExtractor:
    """Extract data using templates."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self.templates = {}
    
    def register_template(
        self,
        name: str,
        url_pattern: str,
        extraction_rules: Dict[str, Dict]
    ):
        """Register extraction template."""
        self.templates[name] = {
            "pattern": re.compile(url_pattern),
            "rules": extraction_rules
        }
    
    def extract_with_template(self, url: str) -> Optional[Dict]:
        """Extract using matching template."""
        # Find matching template
        template = None
        for name, t in self.templates.items():
            if t["pattern"].match(url):
                template = t
                break
        
        if not template:
            return None
        
        # Scrape page
        result = self.app.scrape_url(url, formats=["html"])
        
        if not result.success:
            return None
        
        soup = BeautifulSoup(result.content["html"], "html.parser")
        extracted = {}
        
        # Apply extraction rules
        for field, rule in template["rules"].items():
            try:
                if rule["type"] == "selector":
                    elem = soup.select_one(rule["selector"])
                    if elem:
                        value = elem.get_text(strip=True)
                        if rule.get("transform"):
                            value = rule["transform"](value)
                        extracted[field] = value
                
                elif rule["type"] == "regex":
                    match = re.search(rule["pattern"], result.content["html"])
                    if match:
                        extracted[field] = match.group(1)
                
                elif rule["type"] == "custom":
                    extracted[field] = rule["function"](soup)
            
            except Exception as e:
                extracted[f"{field}_error"] = str(e)
        
        return extracted

# Example usage
extractor = TemplateExtractor()

# Register product template
extractor.register_template(
    "product",
    r"https://shop\.example\.com/product/.*",
    {
        "title": {
            "type": "selector",
            "selector": "h1.product-title"
        },
        "price": {
            "type": "selector",
            "selector": ".price",
            "transform": lambda x: float(re.findall(r"[\d.]+", x)[0])
        },
        "availability": {
            "type": "custom",
            "function": lambda soup: "In Stock" if soup.find(class_="in-stock") else "Out of Stock"
        }
    }
)
```

---

## Integration Patterns

### Database Integration

```python
import sqlite3
from datetime import datetime

class DatabaseIntegration:
    """Store scraping results in database."""
    
    def __init__(self, db_path: str = "rapidcrawl.db"):
        self.app = RapidCrawlApp()
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS scraped_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT,
                scraped_at TIMESTAMP,
                success BOOLEAN,
                error TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS extracted_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                field_name TEXT,
                field_value TEXT,
                FOREIGN KEY (page_id) REFERENCES scraped_pages (id)
            )
        """)
        
        self.conn.commit()
    
    def scrape_and_store(self, url: str) -> int:
        """Scrape URL and store in database."""
        result = self.app.scrape_url(url)
        
        # Insert page
        cursor = self.conn.execute("""
            INSERT OR REPLACE INTO scraped_pages 
            (url, title, content, scraped_at, success, error)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            url,
            result.title,
            result.content.get("text", "")[:10000],  # Limit size
            datetime.now(),
            result.success,
            result.error
        ))
        
        page_id = cursor.lastrowid
        
        # Store structured data
        if result.structured_data:
            for field, value in result.structured_data.items():
                self.conn.execute("""
                    INSERT INTO extracted_data 
                    (page_id, field_name, field_value)
                    VALUES (?, ?, ?)
                """, (page_id, field, str(value)))
        
        self.conn.commit()
        return page_id
    
    def get_scraped_data(
        self,
        url_pattern: str = "%",
        limit: int = 100
    ) -> List[Dict]:
        """Retrieve scraped data from database."""
        cursor = self.conn.execute("""
            SELECT * FROM scraped_pages
            WHERE url LIKE ?
            ORDER BY scraped_at DESC
            LIMIT ?
        """, (url_pattern, limit))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

### Message Queue Integration

```python
import pika
import json

class RabbitMQIntegration:
    """Integrate with RabbitMQ for async processing."""
    
    def __init__(self, host: str = "localhost"):
        self.app = RapidCrawlApp()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host)
        )
        self.channel = self.connection.channel()
        
        # Declare queues
        self.channel.queue_declare(queue='urls_to_scrape')
        self.channel.queue_declare(queue='scraped_results')
    
    def publish_urls(self, urls: List[str]):
        """Publish URLs for scraping."""
        for url in urls:
            self.channel.basic_publish(
                exchange='',
                routing_key='urls_to_scrape',
                body=json.dumps({"url": url})
            )
    
    def consume_and_scrape(self):
        """Consume URLs and scrape them."""
        def callback(ch, method, properties, body):
            data = json.loads(body)
            url = data["url"]
            
            # Scrape URL
            result = self.app.scrape_url(url)
            
            # Publish result
            result_data = {
                "url": url,
                "success": result.success,
                "title": result.title,
                "content_length": len(result.content.get("text", "")),
                "scraped_at": datetime.now().isoformat()
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key='scraped_results',
                body=json.dumps(result_data)
            )
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(
            queue='urls_to_scrape',
            on_message_callback=callback
        )
        
        print("Waiting for URLs to scrape...")
        self.channel.start_consuming()
```

---

## Extending RapidCrawl

### Custom Output Formats

```python
from rapidcrawl.models import ScrapeResult

class CustomFormatter:
    """Add custom output formats."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self.formatters = {
            "xml": self._format_xml,
            "csv": self._format_csv,
            "jsonl": self._format_jsonl
        }
    
    def scrape_with_format(
        self,
        url: str,
        custom_format: str
    ) -> str:
        """Scrape and return in custom format."""
        result = self.app.scrape_url(url)
        
        if not result.success:
            raise Exception(f"Scraping failed: {result.error}")
        
        if custom_format in self.formatters:
            return self.formatters[custom_format](result)
        
        raise ValueError(f"Unknown format: {custom_format}")
    
    def _format_xml(self, result: ScrapeResult) -> str:
        """Format as XML."""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<page>
    <url>{result.url}</url>
    <title>{result.title or ""}</title>
    <description>{result.description or ""}</description>
    <content>{result.content.get("text", "")}</content>
    <scraped_at>{result.scraped_at.isoformat()}</scraped_at>
</page>"""
        return xml
    
    def _format_csv(self, result: ScrapeResult) -> str:
        """Format as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["url", "title", "description", "content_length"])
        writer.writerow([
            result.url,
            result.title or "",
            result.description or "",
            len(result.content.get("text", ""))
        ])
        
        return output.getvalue()
    
    def _format_jsonl(self, result: ScrapeResult) -> str:
        """Format as JSON Lines."""
        data = {
            "url": result.url,
            "title": result.title,
            "description": result.description,
            "content": result.content.get("text", "")[:1000],
            "scraped_at": result.scraped_at.isoformat()
        }
        return json.dumps(data)
```

### Plugin System

```python
from abc import ABC, abstractmethod
from typing import Optional

class ScraperPlugin(ABC):
    """Base class for scraper plugins."""
    
    @abstractmethod
    def pre_scrape(self, url: str, options: Dict) -> Optional[Dict]:
        """Called before scraping. Return modified options or None."""
        pass
    
    @abstractmethod
    def post_scrape(self, result: ScrapeResult) -> ScrapeResult:
        """Called after scraping. Return modified result."""
        pass

class PluggableScraper:
    """Scraper with plugin support."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        self.plugins: List[ScraperPlugin] = []
    
    def register_plugin(self, plugin: ScraperPlugin):
        """Register a plugin."""
        self.plugins.append(plugin)
    
    def scrape_with_plugins(self, url: str, **options) -> ScrapeResult:
        """Scrape with plugin processing."""
        # Pre-scrape plugins
        for plugin in self.plugins:
            modified_options = plugin.pre_scrape(url, options)
            if modified_options:
                options.update(modified_options)
        
        # Scrape
        result = self.app.scrape_url(url, **options)
        
        # Post-scrape plugins
        for plugin in self.plugins:
            result = plugin.post_scrape(result)
        
        return result

# Example plugin
class CachePlugin(ScraperPlugin):
    """Caching plugin."""
    
    def __init__(self):
        self.cache = {}
    
    def pre_scrape(self, url: str, options: Dict) -> Optional[Dict]:
        """Check cache before scraping."""
        if url in self.cache:
            # Return cached result
            return {"cached_result": self.cache[url]}
        return None
    
    def post_scrape(self, result: ScrapeResult) -> ScrapeResult:
        """Cache successful results."""
        if result.success:
            self.cache[result.url] = result
        return result
```

---

## Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy application
COPY . .

# Run scraper
CMD ["python", "scraper.py"]
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rapidcrawl-scraper
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rapidcrawl
  template:
    metadata:
      labels:
        app: rapidcrawl
    spec:
      containers:
      - name: scraper
        image: rapidcrawl:latest
        resources:
          limits:
            memory: "2Gi"
            cpu: "1"
          requests:
            memory: "1Gi"
            cpu: "500m"
        env:
        - name: RAPIDCRAWL_API_KEY
          valueFrom:
            secretKeyRef:
              name: rapidcrawl-secret
              key: api-key
---
apiVersion: v1
kind: Service
metadata:
  name: rapidcrawl-service
spec:
  selector:
    app: rapidcrawl
  ports:
  - port: 8080
    targetPort: 8080
```

### Monitoring and Logging

```python
import logging
from prometheus_client import Counter, Histogram, start_http_server
import time

# Prometheus metrics
scrape_counter = Counter('rapidcrawl_scrapes_total', 'Total scrapes', ['status'])
scrape_duration = Histogram('rapidcrawl_scrape_duration_seconds', 'Scrape duration')

class MonitoredScraper:
    """Scraper with monitoring."""
    
    def __init__(self):
        self.app = RapidCrawlApp()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def scrape_with_monitoring(self, url: str) -> ScrapeResult:
        """Scrape with monitoring."""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting scrape of {url}")
            result = self.app.scrape_url(url)
            
            # Record metrics
            duration = time.time() - start_time
            scrape_duration.observe(duration)
            
            if result.success:
                scrape_counter.labels(status='success').inc()
                self.logger.info(f"Successfully scraped {url} in {duration:.2f}s")
            else:
                scrape_counter.labels(status='failure').inc()
                self.logger.error(f"Failed to scrape {url}: {result.error}")
            
            return result
            
        except Exception as e:
            scrape_counter.labels(status='error').inc()
            self.logger.exception(f"Exception scraping {url}")
            raise
    
    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics server."""
        start_http_server(port)
        self.logger.info(f"Metrics server started on port {port}")
```

---

This advanced guide covers sophisticated techniques for using RapidCrawl in production environments. For specific use cases or additional advanced features, consult the [API documentation](API.md) or contact support.