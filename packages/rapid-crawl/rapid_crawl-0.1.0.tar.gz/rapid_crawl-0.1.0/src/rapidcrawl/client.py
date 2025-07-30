"""
Main client for the RapidCrawl SDK.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import warnings

import httpx
from dotenv import load_dotenv
from rich.console import Console

from rapidcrawl.models import (
    ScrapeOptions,
    CrawlOptions,
    MapOptions,
    SearchOptions,
    ScrapeResult,
    CrawlResult,
    MapResult,
    SearchResult,
    OutputFormat,
)
from rapidcrawl.exceptions import (
    AuthenticationError,
    RateLimitError,
    NetworkError,
    ConfigurationError,
)
from rapidcrawl.features.scrape import Scraper
from rapidcrawl.features.crawl import Crawler
from rapidcrawl.features.map import Mapper
from rapidcrawl.features.search import Searcher
from rapidcrawl.utils import retry_on_network_error

# Load environment variables
load_dotenv()

console = Console()


class RapidCrawlApp:
    """
    Main client for interacting with the RapidCrawl SDK.
    
    This client provides methods for scraping, crawling, mapping, and searching
    web content with various output formats and advanced features.
    """
    
    DEFAULT_BASE_URL = "https://api.rapidcrawl.io/v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 3
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        verify_ssl: bool = True,
        debug: bool = False,
    ):
        """
        Initialize the RapidCrawl client.
        
        Args:
            api_key: API key for authentication. If not provided, will look for
                    RAPIDCRAWL_API_KEY environment variable.
            base_url: Base URL for the API. Defaults to official API endpoint.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            verify_ssl: Whether to verify SSL certificates.
            debug: Enable debug mode for verbose logging.
        """
        # Get API key
        self.api_key = api_key or os.getenv("RAPIDCRAWL_API_KEY")
        if not self.api_key:
            # For now, we'll use a placeholder since we're building a self-hosted solution
            warnings.warn(
                "No API key provided. Some features may be limited. "
                "Set RAPIDCRAWL_API_KEY environment variable or pass api_key parameter.",
                UserWarning
            )
            self.api_key = "self-hosted"
        
        # Configuration
        self.base_url = base_url or os.getenv("RAPIDCRAWL_BASE_URL", self.DEFAULT_BASE_URL)
        self.timeout = timeout or float(os.getenv("RAPIDCRAWL_TIMEOUT", self.DEFAULT_TIMEOUT))
        self.max_retries = max_retries or int(os.getenv("RAPIDCRAWL_MAX_RETRIES", self.DEFAULT_MAX_RETRIES))
        self.verify_ssl = verify_ssl
        self.debug = debug
        
        # Initialize HTTP client
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            verify=self.verify_ssl,
            headers=self._get_default_headers(),
        )
        
        # Initialize async HTTP client (created on demand)
        self._async_client: Optional[httpx.AsyncClient] = None
        
        # Initialize feature handlers
        self.scraper = Scraper(self)
        self.crawler = Crawler(self)
        self.mapper = Mapper(self)
        self.searcher = Searcher(self)
        
        if self.debug:
            console.print(f"[green]RapidCrawl client initialized[/green]")
            console.print(f"  Base URL: {self.base_url}")
            console.print(f"  Timeout: {self.timeout}s")
            console.print(f"  Max retries: {self.max_retries}")
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "RapidCrawl/0.1.0 Python",
            "Content-Type": "application/json",
        }
    
    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers=self._get_default_headers(),
            )
        return self._async_client
    
    def scrape_url(
        self,
        url: str,
        formats: Optional[List[Union[str, OutputFormat]]] = None,
        **kwargs
    ) -> ScrapeResult:
        """
        Scrape a single URL and convert it to specified formats.
        
        Args:
            url: The URL to scrape.
            formats: List of output formats (markdown, html, screenshot, etc.).
            **kwargs: Additional options (see ScrapeOptions for all parameters).
        
        Returns:
            ScrapeResult containing the scraped content.
        
        Example:
            >>> app = RapidCrawlApp()
            >>> result = app.scrape_url(
            ...     "https://example.com",
            ...     formats=["markdown", "screenshot"],
            ...     wait_for=".content-loaded"
            ... )
            >>> print(result.content["markdown"])
        """
        # Convert string formats to OutputFormat enum
        if formats:
            formats = [
                OutputFormat(f) if isinstance(f, str) else f
                for f in formats
            ]
        
        options = ScrapeOptions(
            url=url,
            formats=formats or [OutputFormat.MARKDOWN],
            **kwargs
        )
        
        return self.scraper.scrape(options)
    
    def crawl_url(
        self,
        url: str,
        max_pages: Optional[int] = None,
        max_depth: Optional[int] = None,
        **kwargs
    ) -> CrawlResult:
        """
        Crawl a website starting from the given URL.
        
        Args:
            url: The starting URL for crawling.
            max_pages: Maximum number of pages to crawl.
            max_depth: Maximum depth to crawl.
            **kwargs: Additional options (see CrawlOptions for all parameters).
        
        Returns:
            CrawlResult containing all crawled pages.
        
        Example:
            >>> app = RapidCrawlApp()
            >>> result = app.crawl_url(
            ...     "https://example.com",
            ...     max_pages=50,
            ...     max_depth=3,
            ...     include_patterns=["*/blog/*"]
            ... )
            >>> print(f"Crawled {result.pages_crawled} pages")
        """
        options = CrawlOptions(
            url=url,
            max_pages=max_pages or 100,
            max_depth=max_depth or 3,
            **kwargs
        )
        
        return self.crawler.crawl(options)
    
    async def crawl_url_async(
        self,
        url: str,
        max_pages: Optional[int] = None,
        max_depth: Optional[int] = None,
        **kwargs
    ) -> CrawlResult:
        """
        Asynchronously crawl a website starting from the given URL.
        
        This method is more efficient for large crawls as it can process
        multiple pages concurrently.
        
        Args:
            url: The starting URL for crawling.
            max_pages: Maximum number of pages to crawl.
            max_depth: Maximum depth to crawl.
            **kwargs: Additional options (see CrawlOptions for all parameters).
        
        Returns:
            CrawlResult containing all crawled pages.
        """
        options = CrawlOptions(
            url=url,
            max_pages=max_pages or 100,
            max_depth=max_depth or 3,
            **kwargs
        )
        
        return await self.crawler.crawl_async(options)
    
    def map_url(
        self,
        url: str,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> MapResult:
        """
        Map all URLs from a website.
        
        This is a fast method to discover all URLs on a website without
        scraping their content.
        
        Args:
            url: The website URL to map.
            search: Filter URLs containing this search term.
            limit: Maximum number of URLs to return.
            **kwargs: Additional options (see MapOptions for all parameters).
        
        Returns:
            MapResult containing discovered URLs.
        
        Example:
            >>> app = RapidCrawlApp()
            >>> result = app.map_url(
            ...     "https://example.com",
            ...     search="product",
            ...     limit=1000
            ... )
            >>> print(f"Found {result.total_urls} URLs")
        """
        options = MapOptions(
            url=url,
            search=search,
            limit=limit or 5000,
            **kwargs
        )
        
        return self.mapper.map(options)
    
    def search(
        self,
        query: str,
        num_results: Optional[int] = None,
        scrape_results: bool = False,
        **kwargs
    ) -> SearchResult:
        """
        Search the web and optionally scrape results.
        
        Args:
            query: The search query.
            num_results: Number of results to return.
            scrape_results: Whether to scrape content from result URLs.
            **kwargs: Additional options (see SearchOptions for all parameters).
        
        Returns:
            SearchResult containing search results.
        
        Example:
            >>> app = RapidCrawlApp()
            >>> result = app.search(
            ...     "python web scraping tutorial",
            ...     num_results=10,
            ...     scrape_results=True,
            ...     formats=["markdown"]
            ... )
            >>> for item in result.results:
            ...     print(f"{item.title}: {item.url}")
        """
        options = SearchOptions(
            query=query,
            num_results=num_results or 10,
            scrape_results=scrape_results,
            **kwargs
        )
        
        return self.searcher.search(options)
    
    def extract(
        self,
        urls: Union[str, List[str]],
        schema: Optional[List[Dict[str, Any]]] = None,
        prompt: Optional[str] = None,
        **kwargs
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Extract structured data from one or more URLs.
        
        Args:
            urls: Single URL or list of URLs to extract from.
            schema: Extraction schema defining fields to extract.
            prompt: Natural language prompt for extraction.
            **kwargs: Additional scraping options.
        
        Returns:
            Single ScrapeResult or list of ScrapeResults with extracted data.
        
        Example:
            >>> app = RapidCrawlApp()
            >>> schema = [
            ...     {"name": "title", "selector": "h1"},
            ...     {"name": "price", "selector": ".price", "type": "number"}
            ... ]
            >>> result = app.extract(
            ...     "https://example.com/product",
            ...     schema=schema
            ... )
            >>> print(result.structured_data)
        """
        # Convert single URL to list
        single_url = isinstance(urls, str)
        if single_url:
            urls = [urls]
        
        results = []
        for url in urls:
            options = ScrapeOptions(
                url=url,
                formats=[OutputFormat.STRUCTURED],
                extract_schema=schema,
                extract_prompt=prompt,
                **kwargs
            )
            result = self.scraper.scrape(options)
            results.append(result)
        
        return results[0] if single_url else results
    
    def close(self):
        """Close HTTP clients and clean up resources."""
        if self._client:
            self._client.close()
        if self._async_client:
            asyncio.create_task(self._async_client.aclose())
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._async_client:
            await self._async_client.aclose()