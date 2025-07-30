#!/usr/bin/env python3
"""
Advanced usage examples for RapidCrawl.

This example demonstrates:
- Custom headers and authentication
- Rate limiting and throttling
- Error handling and retries
- Caching strategies
- Performance optimization
- Integration patterns
"""

import os
import sys
import json
import time
import asyncio
import hashlib
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import (
    RapidCrawlError,
    RateLimitError,
    TimeoutError,
    NetworkError,
    ValidationError
)


def authentication_example():
    """Examples of various authentication methods."""
    print("=== Authentication Examples ===\n")
    
    app = RapidCrawlApp()
    
    # Basic authentication
    import base64
    basic_auth = base64.b64encode(b"username:password").decode()
    
    result = app.scrape_url(
        "https://httpbin.org/basic-auth/username/password",
        headers={
            "Authorization": f"Basic {basic_auth}"
        }
    )
    
    if result.success:
        print("✓ Basic auth successful")
    
    # Bearer token authentication
    result = app.scrape_url(
        "https://api.example.com/protected",
        headers={
            "Authorization": "Bearer your-api-token-here",
            "X-API-Version": "2.0"
        }
    )
    
    # Custom headers for specific sites
    result = app.scrape_url(
        "https://example.com",
        headers={
            "User-Agent": "RapidCrawl/1.0 (Compatible; Example Bot)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Referer": "https://google.com"
        }
    )


def rate_limiting_example():
    """Implement rate limiting for polite crawling."""
    print("\n=== Rate Limiting Example ===\n")
    
    class RateLimitedScraper:
        def __init__(self, requests_per_second=2):
            self.app = RapidCrawlApp()
            self.min_interval = 1.0 / requests_per_second
            self.last_request_time = 0
        
        def scrape_url(self, url, **kwargs):
            # Enforce rate limit
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                print(f"Rate limiting: waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
            return self.app.scrape_url(url, **kwargs)
    
    # Use rate-limited scraper
    scraper = RateLimitedScraper(requests_per_second=1)
    
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1"
    ]
    
    print("Scraping with rate limit (1 req/sec)...")
    start_time = time.time()
    
    for url in urls:
        result = scraper.scrape_url(url)
        print(f"  Scraped: {url}")
    
    total_time = time.time() - start_time
    print(f"Total time: {total_time:.2f}s (should be ~3s with rate limiting)")


def retry_with_backoff():
    """Implement retry logic with exponential backoff."""
    print("\n=== Retry with Backoff Example ===\n")
    
    def retry_on_failure(max_retries=3, backoff_factor=2):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except (NetworkError, TimeoutError) as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = backoff_factor ** attempt
                            print(f"  Attempt {attempt + 1} failed, waiting {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"  All {max_retries} attempts failed")
                
                raise last_exception
            return wrapper
        return decorator
    
    @retry_on_failure(max_retries=3, backoff_factor=2)
    def scrape_with_retry(url):
        app = RapidCrawlApp()
        return app.scrape_url(url, timeout=5000)  # 5 second timeout
    
    # Test with unreliable URL
    print("Testing retry logic...")
    try:
        result = scrape_with_retry("https://httpbin.org/status/500")
    except Exception as e:
        print(f"Final failure: {e}")


def caching_example():
    """Implement various caching strategies."""
    print("\n=== Caching Example ===\n")
    
    class CachedScraper:
        def __init__(self, cache_dir="cache"):
            self.app = RapidCrawlApp()
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(exist_ok=True)
            self.memory_cache = {}
        
        def _get_cache_key(self, url, options):
            """Generate cache key from URL and options."""
            cache_data = f"{url}:{json.dumps(options, sort_keys=True)}"
            return hashlib.md5(cache_data.encode()).hexdigest()
        
        def _get_cache_path(self, cache_key):
            """Get file path for cache key."""
            return self.cache_dir / f"{cache_key}.pkl"
        
        def scrape_with_disk_cache(self, url, max_age_hours=24, **options):
            """Scrape with disk-based caching."""
            cache_key = self._get_cache_key(url, options)
            cache_path = self._get_cache_path(cache_key)
            
            # Check cache
            if cache_path.exists():
                age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
                if age_hours < max_age_hours:
                    print(f"  Using disk cache (age: {age_hours:.1f}h)")
                    with open(cache_path, "rb") as f:
                        return pickle.load(f)
            
            # Scrape fresh
            print(f"  Scraping fresh content...")
            result = self.app.scrape_url(url, **options)
            
            # Save to cache
            with open(cache_path, "wb") as f:
                pickle.dump(result, f)
            
            return result
        
        @lru_cache(maxsize=100)
        def scrape_with_memory_cache(self, url):
            """Scrape with in-memory LRU cache."""
            print(f"  Scraping (not in memory cache)...")
            return self.app.scrape_url(url)
    
    # Test caching
    scraper = CachedScraper()
    
    # Disk cache example
    print("Testing disk cache:")
    url = "https://example.com"
    
    # First request - will scrape
    result1 = scraper.scrape_with_disk_cache(url)
    
    # Second request - from cache
    result2 = scraper.scrape_with_disk_cache(url)
    
    # Memory cache example
    print("\nTesting memory cache:")
    
    # First request - will scrape
    result3 = scraper.scrape_with_memory_cache("https://example.org")
    
    # Second request - from memory
    result4 = scraper.scrape_with_memory_cache("https://example.org")


def concurrent_scraping():
    """Optimize performance with concurrent scraping."""
    print("\n=== Concurrent Scraping Example ===\n")
    
    app = RapidCrawlApp()
    
    # URLs to scrape
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1"
    ]
    
    # Sequential scraping
    print("Sequential scraping (5 URLs)...")
    start_time = time.time()
    
    sequential_results = []
    for url in urls:
        result = app.scrape_url(url)
        sequential_results.append(result)
    
    sequential_time = time.time() - start_time
    print(f"  Time: {sequential_time:.2f}s")
    
    # Concurrent scraping with ThreadPoolExecutor
    print("\nConcurrent scraping (5 URLs)...")
    start_time = time.time()
    
    concurrent_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(app.scrape_url, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                concurrent_results.append(result)
            except Exception as e:
                print(f"  Error scraping {url}: {e}")
    
    concurrent_time = time.time() - start_time
    print(f"  Time: {concurrent_time:.2f}s")
    print(f"  Speedup: {sequential_time / concurrent_time:.2f}x")


async def async_scraping():
    """Async scraping for maximum performance."""
    print("\n=== Async Scraping Example ===\n")
    
    app = RapidCrawlApp()
    
    # URLs to scrape
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1"
    ]
    
    # Async scraping function
    async def scrape_url_async(url):
        # In real implementation, this would use async HTTP client
        # For demo, we'll use asyncio.to_thread
        return await asyncio.to_thread(app.scrape_url, url)
    
    # Scrape all URLs concurrently
    print("Async scraping (5 URLs)...")
    start_time = time.time()
    
    tasks = [scrape_url_async(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    async_time = time.time() - start_time
    print(f"  Time: {async_time:.2f}s")
    
    # Process results
    successful = sum(1 for r in results if not isinstance(r, Exception) and r.success)
    print(f"  Successful: {successful}/{len(urls)}")


def error_handling_patterns():
    """Advanced error handling patterns."""
    print("\n=== Error Handling Patterns ===\n")
    
    app = RapidCrawlApp()
    
    def scrape_with_fallback(primary_url, fallback_url):
        """Try primary URL, fall back to alternative if failed."""
        try:
            result = app.scrape_url(primary_url, timeout=5000)
            if result.success:
                return result
        except (NetworkError, TimeoutError):
            pass
        
        print(f"  Primary failed, trying fallback...")
        return app.scrape_url(fallback_url)
    
    def scrape_with_circuit_breaker(urls, failure_threshold=3):
        """Stop trying after too many failures."""
        consecutive_failures = 0
        results = []
        
        for url in urls:
            if consecutive_failures >= failure_threshold:
                print(f"  Circuit breaker triggered after {failure_threshold} failures")
                break
            
            try:
                result = app.scrape_url(url, timeout=5000)
                if result.success:
                    consecutive_failures = 0
                    results.append(result)
                else:
                    consecutive_failures += 1
            except Exception:
                consecutive_failures += 1
        
        return results
    
    # Test error handling
    print("Testing fallback pattern...")
    result = scrape_with_fallback(
        "https://invalid-url-12345.com",
        "https://example.com"
    )
    
    print("\nTesting circuit breaker...")
    test_urls = [
        "https://invalid1.com",
        "https://invalid2.com",
        "https://invalid3.com",
        "https://example.com",  # This won't be tried
        "https://example.org"   # This won't be tried
    ]
    results = scrape_with_circuit_breaker(test_urls, failure_threshold=3)


def monitoring_and_logging():
    """Add monitoring and logging to scraping."""
    print("\n=== Monitoring and Logging Example ===\n")
    
    import logging
    from datetime import datetime
    
    class MonitoredScraper:
        def __init__(self):
            self.app = RapidCrawlApp()
            self.stats = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_bytes": 0,
                "total_time": 0
            }
            
            # Setup logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('scraping.log'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
        
        def scrape_with_monitoring(self, url):
            """Scrape with monitoring and logging."""
            start_time = time.time()
            self.stats["total_requests"] += 1
            
            self.logger.info(f"Starting scrape of {url}")
            
            try:
                result = self.app.scrape_url(url)
                duration = time.time() - start_time
                self.stats["total_time"] += duration
                
                if result.success:
                    self.stats["successful_requests"] += 1
                    content_size = len(result.content.get("text", ""))
                    self.stats["total_bytes"] += content_size
                    
                    self.logger.info(
                        f"Success: {url} - "
                        f"{content_size} bytes in {duration:.2f}s"
                    )
                else:
                    self.stats["failed_requests"] += 1
                    self.logger.error(f"Failed: {url} - {result.error}")
                
                return result
                
            except Exception as e:
                self.stats["failed_requests"] += 1
                self.logger.exception(f"Exception scraping {url}")
                raise
        
        def print_stats(self):
            """Print scraping statistics."""
            if self.stats["total_requests"] > 0:
                success_rate = (
                    self.stats["successful_requests"] / 
                    self.stats["total_requests"] * 100
                )
                avg_time = self.stats["total_time"] / self.stats["total_requests"]
                avg_bytes = (
                    self.stats["total_bytes"] / 
                    self.stats["successful_requests"]
                    if self.stats["successful_requests"] > 0 else 0
                )
                
                print("\nScraping Statistics:")
                print(f"  Total requests: {self.stats['total_requests']}")
                print(f"  Successful: {self.stats['successful_requests']}")
                print(f"  Failed: {self.stats['failed_requests']}")
                print(f"  Success rate: {success_rate:.1f}%")
                print(f"  Average time: {avg_time:.2f}s")
                print(f"  Average size: {avg_bytes:.0f} bytes")
                print(f"  Total data: {self.stats['total_bytes'] / 1024:.1f} KB")
    
    # Test monitoring
    scraper = MonitoredScraper()
    
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://example.org"
    ]
    
    for url in test_urls:
        try:
            scraper.scrape_with_monitoring(url)
        except Exception:
            pass
    
    scraper.print_stats()


if __name__ == "__main__":
    try:
        # Run sync examples
        authentication_example()
        rate_limiting_example()
        retry_with_backoff()
        caching_example()
        concurrent_scraping()
        error_handling_patterns()
        monitoring_and_logging()
        
        # Run async example
        print("\nRunning async example...")
        asyncio.run(async_scraping())
        
        print("\n✓ All advanced examples completed!")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")