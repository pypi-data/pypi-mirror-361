"""
URL mapping functionality for RapidCrawl.
"""

import asyncio
import xml.etree.ElementTree as ET
from typing import Set, List, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from collections import deque

import httpx
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from rapidcrawl.models import MapOptions, MapResult
from rapidcrawl.exceptions import ValidationError, NetworkError
from rapidcrawl.utils import (
    normalize_url,
    is_valid_url,
    is_same_domain,
    extract_links,
    create_progress_bar,
)

console = Console()


class Mapper:
    """Handles URL mapping operations."""
    
    def __init__(self, client):
        self.client = client
    
    def map(self, options: MapOptions) -> MapResult:
        """Map all URLs from a website."""
        return asyncio.run(self._map_async(options))
    
    async def _map_async(self, options: MapOptions) -> MapResult:
        """Map URLs asynchronously for better performance."""
        start_time = datetime.utcnow()
        
        try:
            # Validate URL
            if not is_valid_url(str(options.url)):
                raise ValidationError(f"Invalid URL: {options.url}")
            
            start_url = normalize_url(str(options.url))
            domain = urlparse(start_url).netloc
            
            # Initialize URL set
            discovered_urls: Set[str] = set()
            sitemap_found = False
            
            # Create progress indicator
            progress = None
            if self.client.debug:
                progress = create_progress_bar(f"Mapping {domain}")
                task_id = progress.add_task("Discovering URLs", total=None)
                progress.start()
            
            # Try sitemap first unless ignored
            if not options.ignore_sitemap:
                if self.client.debug:
                    progress.update(task_id, description="Checking sitemap.xml")
                
                sitemap_urls = await self._fetch_sitemap_urls(start_url)
                if sitemap_urls:
                    sitemap_found = True
                    discovered_urls.update(sitemap_urls)
                    
                    if self.client.debug:
                        console.print(f"[green]Found {len(sitemap_urls)} URLs in sitemap[/green]")
            
            # If we need more URLs or no sitemap, crawl the site
            if len(discovered_urls) < options.limit:
                if self.client.debug:
                    progress.update(task_id, description="Crawling website")
                
                crawled_urls = await self._fast_crawl(
                    start_url,
                    options,
                    existing_urls=discovered_urls,
                    progress_task=(progress, task_id) if progress else None
                )
                discovered_urls.update(crawled_urls)
            
            # Filter URLs
            filtered_urls = self._filter_urls(
                discovered_urls,
                start_url,
                options
            )
            
            # Limit results
            final_urls = list(filtered_urls)[:options.limit]
            
            # Stop progress
            if progress:
                progress.stop()
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            if self.client.debug:
                console.print(f"[green]Mapping completed: {len(final_urls)} URLs found in {duration:.2f}s[/green]")
            
            return MapResult(
                success=True,
                url=str(options.url),
                urls=final_urls,
                total_urls=len(final_urls),
                sitemap_found=sitemap_found,
                duration=duration,
                mapped_at=start_time
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            if progress:
                progress.stop()
            
            return MapResult(
                success=False,
                url=str(options.url),
                urls=[],
                total_urls=0,
                sitemap_found=False,
                duration=duration,
                mapped_at=start_time
            )
    
    async def _fetch_sitemap_urls(self, base_url: str) -> Set[str]:
        """Fetch URLs from sitemap.xml."""
        urls = set()
        
        # Common sitemap locations
        sitemap_paths = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap-index.xml",
            "/sitemaps/sitemap.xml",
            "/sitemap/sitemap.xml",
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for path in sitemap_paths:
                sitemap_url = urljoin(base_url, path)
                
                try:
                    response = await client.get(
                        sitemap_url,
                        headers={"User-Agent": "RapidCrawl/0.1.0"}
                    )
                    
                    if response.status_code == 200:
                        # Parse sitemap
                        sitemap_urls = self._parse_sitemap(response.text, base_url)
                        urls.update(sitemap_urls)
                        
                        if urls:
                            break
                            
                except Exception:
                    continue
        
        return urls
    
    def _parse_sitemap(self, xml_content: str, base_url: str) -> Set[str]:
        """Parse sitemap XML and extract URLs."""
        urls = set()
        
        try:
            root = ET.fromstring(xml_content)
            
            # Handle different sitemap namespaces
            namespaces = {
                '': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            }
            
            # Check if this is a sitemap index
            for sitemap in root.findall('.//sitemap:sitemap', namespaces):
                loc = sitemap.find('sitemap:loc', namespaces)
                if loc is not None and loc.text:
                    # This is a sitemap index, we should fetch sub-sitemaps
                    # For now, we'll skip to keep it simple
                    pass
            
            # Extract URLs from regular sitemap
            for url_elem in root.findall('.//sitemap:url', namespaces):
                loc = url_elem.find('sitemap:loc', namespaces)
                if loc is not None and loc.text:
                    url = normalize_url(loc.text)
                    if is_valid_url(url):
                        urls.add(url)
            
            # Also try without namespace
            for url_elem in root.findall('.//url'):
                loc = url_elem.find('loc')
                if loc is not None and loc.text:
                    url = normalize_url(loc.text)
                    if is_valid_url(url):
                        urls.add(url)
                        
        except ET.ParseError:
            # Invalid XML
            pass
        
        return urls
    
    async def _fast_crawl(
        self,
        start_url: str,
        options: MapOptions,
        existing_urls: Set[str],
        progress_task: Optional[tuple] = None
    ) -> Set[str]:
        """Fast crawl to discover URLs without full scraping."""
        discovered = set()
        visited = set()
        queue = deque([start_url])
        
        # Limit concurrent requests
        semaphore = asyncio.Semaphore(10)
        
        async def fetch_page_urls(url: str) -> Set[str]:
            """Fetch URLs from a single page."""
            async with semaphore:
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(
                            url,
                            headers={"User-Agent": "RapidCrawl/0.1.0"},
                            follow_redirects=True
                        )
                        
                        if response.status_code == 200:
                            # Only parse HTML content
                            content_type = response.headers.get("content-type", "")
                            if "text/html" in content_type:
                                return set(extract_links(response.text, url))
                                
                except Exception:
                    pass
                
                return set()
        
        # Crawl with BFS approach
        max_pages_to_visit = min(100, options.limit // 10)  # Visit up to 10% of limit
        pages_visited = 0
        
        while queue and pages_visited < max_pages_to_visit:
            # Process batch of URLs concurrently
            batch_size = min(10, len(queue))
            batch_urls = []
            
            for _ in range(batch_size):
                if queue:
                    url = queue.popleft()
                    if url not in visited:
                        batch_urls.append(url)
                        visited.add(url)
            
            if not batch_urls:
                continue
            
            # Update progress
            if progress_task:
                progress, task_id = progress_task
                progress.update(
                    task_id,
                    description=f"Crawling: visited {pages_visited} pages, found {len(discovered)} URLs"
                )
            
            # Fetch URLs from all pages in batch
            tasks = [fetch_page_urls(url) for url in batch_urls]
            results = await asyncio.gather(*tasks)
            
            # Process results
            for url, found_urls in zip(batch_urls, results):
                pages_visited += 1
                
                for found_url in found_urls:
                    normalized = normalize_url(found_url)
                    
                    # Check if we should include this URL
                    if normalized not in discovered and normalized not in existing_urls:
                        if self._should_include_url(normalized, start_url, options):
                            discovered.add(normalized)
                            
                            # Add to queue if same domain and we haven't hit limits
                            if (len(discovered) + len(existing_urls) < options.limit and
                                is_same_domain(normalized, start_url, options.include_subdomains)):
                                queue.append(normalized)
                
                # Stop if we have enough URLs
                if len(discovered) + len(existing_urls) >= options.limit:
                    break
        
        return discovered
    
    def _filter_urls(
        self,
        urls: Set[str],
        base_url: str,
        options: MapOptions
    ) -> List[str]:
        """Filter and sort URLs based on options."""
        filtered = []
        
        for url in urls:
            if self._should_include_url(url, base_url, options):
                filtered.append(url)
        
        # Sort URLs (by length then alphabetically)
        filtered.sort(key=lambda u: (len(u), u))
        
        return filtered
    
    def _should_include_url(
        self,
        url: str,
        base_url: str,
        options: MapOptions
    ) -> bool:
        """Check if URL should be included in results."""
        # Check domain
        if not is_same_domain(url, base_url, options.include_subdomains):
            return False
        
        # Check search filter
        if options.search:
            if options.search.lower() not in url.lower():
                return False
        
        # Exclude common non-content URLs
        exclude_patterns = [
            r'/wp-admin/',
            r'/admin/',
            r'/login',
            r'/logout',
            r'/register',
            r'/api/',
            r'\.pdf$',
            r'\.zip$',
            r'\.exe$',
            r'\.(jpg|jpeg|png|gif|svg|ico)$',
            r'\.(css|js)$',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True