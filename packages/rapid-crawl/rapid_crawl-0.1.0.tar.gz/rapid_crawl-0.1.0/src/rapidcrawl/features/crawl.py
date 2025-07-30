"""
Web crawling functionality for RapidCrawl.
"""

import asyncio
import uuid
from typing import Set, Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from collections import deque
import time

import httpx
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from rapidcrawl.models import (
    CrawlOptions,
    CrawlResult,
    CrawlStatus,
    CrawlProgress,
    ScrapeOptions,
    ScrapeResult,
    OutputFormat,
)
from rapidcrawl.exceptions import ValidationError, NetworkError
from rapidcrawl.utils import (
    normalize_url,
    is_valid_url,
    is_same_domain,
    extract_links,
    parse_robots_txt,
    is_url_allowed,
    rate_limit_decorator,
    create_progress_bar,
)
from rapidcrawl.features.scrape import Scraper

console = Console()


class CrawlJob:
    """Represents a crawl job with its state."""
    
    def __init__(self, job_id: str, options: CrawlOptions):
        self.job_id = job_id
        self.options = options
        self.status = CrawlStatus.PENDING
        self.pages: List[ScrapeResult] = []
        self.visited_urls: Set[str] = set()
        self.url_queue: deque = deque()
        self.url_depths: Dict[str, int] = {}
        self.pages_crawled = 0
        self.pages_failed = 0
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.robots_rules = None
        self.crawl_delay = 0
    
    def get_progress(self) -> CrawlProgress:
        """Get current progress of the crawl job."""
        duration = 0
        if self.started_at:
            end_time = self.completed_at or datetime.utcnow()
            duration = (end_time - self.started_at).total_seconds()
        
        current_url = None
        current_depth = 0
        if self.url_queue:
            current_url = self.url_queue[0]
            current_depth = self.url_depths.get(current_url, 0)
        
        # Estimate remaining time
        estimated_time = None
        if self.pages_crawled > 0 and len(self.url_queue) > 0:
            avg_time_per_page = duration / self.pages_crawled
            estimated_time = avg_time_per_page * len(self.url_queue)
        
        return CrawlProgress(
            job_id=self.job_id,
            status=self.status,
            pages_crawled=self.pages_crawled,
            pages_found=len(self.visited_urls),
            pages_failed=self.pages_failed,
            current_url=current_url,
            depth=current_depth,
            duration=duration,
            estimated_time_remaining=estimated_time
        )
    
    def to_result(self) -> CrawlResult:
        """Convert job to final result."""
        return CrawlResult(
            job_id=self.job_id,
            status=self.status,
            url=str(self.options.url),
            pages=self.pages,
            total_pages=len(self.visited_urls),
            pages_crawled=self.pages_crawled,
            pages_failed=self.pages_failed,
            duration=(self.completed_at - self.started_at).total_seconds() if self.started_at and self.completed_at else 0,
            started_at=self.started_at,
            completed_at=self.completed_at,
            error=self.error
        )


class Crawler:
    """Handles web crawling operations."""
    
    def __init__(self, client):
        self.client = client
        self.scraper = Scraper(client)
        self.active_jobs: Dict[str, CrawlJob] = {}
    
    def crawl(self, options: CrawlOptions) -> CrawlResult:
        """Crawl a website synchronously."""
        # Create crawl job
        job_id = str(uuid.uuid4())
        job = CrawlJob(job_id, options)
        self.active_jobs[job_id] = job
        
        try:
            # Run crawl
            asyncio.run(self._run_crawl(job))
            return job.to_result()
        finally:
            # Clean up
            self.active_jobs.pop(job_id, None)
    
    async def crawl_async(self, options: CrawlOptions) -> CrawlResult:
        """Crawl a website asynchronously."""
        # Create crawl job
        job_id = str(uuid.uuid4())
        job = CrawlJob(job_id, options)
        self.active_jobs[job_id] = job
        
        try:
            # Run crawl
            await self._run_crawl(job)
            return job.to_result()
        finally:
            # Clean up
            self.active_jobs.pop(job_id, None)
    
    def get_job_status(self, job_id: str) -> Optional[CrawlProgress]:
        """Get status of a crawl job."""
        job = self.active_jobs.get(job_id)
        if job:
            return job.get_progress()
        return None
    
    async def _run_crawl(self, job: CrawlJob):
        """Run the crawl job."""
        job.status = CrawlStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        try:
            # Validate starting URL
            if not is_valid_url(str(job.options.url)):
                raise ValidationError(f"Invalid URL: {job.options.url}")
            
            start_url = normalize_url(str(job.options.url))
            
            # Fetch and parse robots.txt
            await self._fetch_robots_txt(job, start_url)
            
            # Initialize queue with starting URL
            job.url_queue.append(start_url)
            job.url_depths[start_url] = 0
            
            # Create progress bar if in debug mode
            progress = None
            if self.client.debug:
                progress = create_progress_bar("Crawling")
                task_id = progress.add_task(
                    f"Crawling {get_domain(start_url)}",
                    total=job.options.max_pages
                )
                progress.start()
            
            # Set up rate limiting
            if job.options.limit_rate:
                crawl_delay = 1.0 / job.options.limit_rate
            else:
                crawl_delay = job.crawl_delay
            
            # Crawl loop
            while job.url_queue and job.pages_crawled < job.options.max_pages:
                url = job.url_queue.popleft()
                
                # Skip if already visited
                if url in job.visited_urls:
                    continue
                
                # Check depth limit
                depth = job.url_depths.get(url, 0)
                if depth > job.options.max_depth:
                    continue
                
                # Mark as visited
                job.visited_urls.add(url)
                
                # Check robots.txt
                if job.robots_rules and not is_url_allowed(url, job.robots_rules):
                    continue
                
                # Update progress
                if progress:
                    progress.update(
                        task_id,
                        completed=job.pages_crawled,
                        description=f"Crawling: {url[:50]}..."
                    )
                
                # Rate limiting
                if crawl_delay > 0:
                    await asyncio.sleep(crawl_delay)
                
                # Scrape page
                try:
                    result = await self._scrape_page(job, url)
                    if result.success:
                        job.pages.append(result)
                        job.pages_crawled += 1
                        
                        # Extract and queue new URLs
                        if result.links:
                            await self._queue_urls(job, result.links, url, depth)
                        
                        # Send webhook update if configured
                        if job.options.webhook_url:
                            await self._send_webhook_update(job)
                    else:
                        job.pages_failed += 1
                        
                except Exception as e:
                    job.pages_failed += 1
                    if self.client.debug:
                        console.print(f"[red]Failed to crawl {url}: {e}[/red]")
            
            # Mark as completed
            job.status = CrawlStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            if progress:
                progress.stop()
                console.print(f"[green]Crawl completed: {job.pages_crawled} pages crawled[/green]")
                
        except Exception as e:
            job.status = CrawlStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            raise
    
    async def _fetch_robots_txt(self, job: CrawlJob, start_url: str):
        """Fetch and parse robots.txt."""
        try:
            parsed = urlparse(start_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    robots_url,
                    timeout=10.0,
                    headers={"User-Agent": "RapidCrawl/0.1.0"}
                )
                
                if response.status_code == 200:
                    job.robots_rules = parse_robots_txt(
                        response.text,
                        user_agent="RapidCrawl"
                    )
                    
                    # Get crawl delay
                    if job.robots_rules.get("crawl-delay"):
                        job.crawl_delay = job.robots_rules["crawl-delay"]
                        
        except Exception:
            # Ignore robots.txt errors
            pass
    
    async def _scrape_page(self, job: CrawlJob, url: str) -> ScrapeResult:
        """Scrape a single page."""
        # Create scrape options from crawl options
        scrape_options = ScrapeOptions(
            url=url,
            formats=job.options.formats,
            headers=job.options.headers,
            wait_for=job.options.wait_for,
            timeout=job.options.timeout,
            extract_schema=job.options.extract_schema,
            include_links=True,  # Always include links for crawling
        )
        
        # Scrape the page
        return self.scraper.scrape(scrape_options)
    
    async def _queue_urls(
        self,
        job: CrawlJob,
        urls: List[str],
        parent_url: str,
        parent_depth: int
    ):
        """Queue new URLs for crawling."""
        parent_domain = get_domain(parent_url)
        
        for url in urls:
            # Normalize URL
            url = normalize_url(url)
            
            # Skip if already visited or queued
            if url in job.visited_urls or url in job.url_queue:
                continue
            
            # Check domain restrictions
            if not is_same_domain(url, parent_url, job.options.allow_subdomains):
                continue
            
            # Check include patterns
            if job.options.include_patterns:
                if not any(re.match(pattern, url) for pattern in job.options.include_patterns):
                    continue
            
            # Check exclude patterns
            if job.options.exclude_patterns:
                if any(re.match(pattern, url) for pattern in job.options.exclude_patterns):
                    continue
            
            # Add to queue
            job.url_queue.append(url)
            job.url_depths[url] = parent_depth + 1
    
    async def _send_webhook_update(self, job: CrawlJob):
        """Send progress update to webhook."""
        try:
            progress = job.get_progress()
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    str(job.options.webhook_url),
                    json=progress.dict(),
                    timeout=10.0
                )
        except Exception:
            # Don't fail crawl on webhook errors
            pass


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc