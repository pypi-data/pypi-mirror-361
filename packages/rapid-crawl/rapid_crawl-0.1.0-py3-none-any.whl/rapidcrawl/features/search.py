"""
Web search functionality for RapidCrawl.
"""

import asyncio
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

import httpx
from bs4 import BeautifulSoup
from rich.console import Console

from rapidcrawl.models import (
    SearchOptions,
    SearchResult,
    SearchResultItem,
    SearchEngine,
    ScrapeOptions,
    OutputFormat,
)
from rapidcrawl.exceptions import ValidationError, NetworkError
from rapidcrawl.utils import normalize_url, is_valid_url, clean_text
from rapidcrawl.features.scrape import Scraper

console = Console()


class SearchProvider:
    """Base class for search providers."""
    
    def __init__(self, client):
        self.client = client
    
    async def search(
        self,
        query: str,
        num_results: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform search and return raw results."""
        raise NotImplementedError


class GoogleSearchProvider(SearchProvider):
    """Google search provider using web scraping."""
    
    async def search(
        self,
        query: str,
        num_results: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search Google and parse results."""
        results = []
        
        # Build search URL
        params = {
            "q": query,
            "num": min(num_results, 100),  # Google limits to 100
        }
        
        # Add date range if specified
        if start_date or end_date:
            date_range = self._build_date_range(start_date, end_date)
            if date_range:
                params["tbs"] = f"cdr:1,cd_min:{date_range['min']},cd_max:{date_range['max']}"
        
        # Add language
        if language:
            params["hl"] = language
            params["lr"] = f"lang_{language}"
        
        # Add location (using country code)
        if location:
            params["gl"] = location.upper()
        
        search_url = f"https://www.google.com/search?{urllib.parse.urlencode(params)}"
        
        # Make request with proper headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, headers=headers, timeout=10.0)
            
            if response.status_code != 200:
                raise NetworkError(f"Search failed with status {response.status_code}")
            
            # Parse results
            soup = BeautifulSoup(response.text, "lxml")
            
            # Find search result divs
            position = 1
            for g in soup.find_all("div", class_="g"):
                # Skip if no link found
                link_elem = g.find("a", href=True)
                if not link_elem:
                    continue
                
                # Extract URL
                url = link_elem["href"]
                if not url.startswith("http"):
                    continue
                
                # Extract title
                title_elem = g.find("h3")
                if not title_elem:
                    continue
                title = clean_text(title_elem.get_text())
                
                # Extract snippet
                snippet = ""
                snippet_elem = g.find("span", class_="st") or g.find("div", class_="VwiC3b")
                if snippet_elem:
                    snippet = clean_text(snippet_elem.get_text())
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "position": position,
                })
                
                position += 1
                if len(results) >= num_results:
                    break
        
        return results
    
    def _build_date_range(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Optional[Dict[str, str]]:
        """Build date range for Google search."""
        if not start_date and not end_date:
            return None
        
        date_format = "%m/%d/%Y"
        
        min_date = start_date.strftime(date_format) if start_date else "1/1/1900"
        max_date = end_date.strftime(date_format) if end_date else datetime.now().strftime(date_format)
        
        return {"min": min_date, "max": max_date}


class DuckDuckGoSearchProvider(SearchProvider):
    """DuckDuckGo search provider."""
    
    async def search(
        self,
        query: str,
        num_results: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search DuckDuckGo and parse results."""
        results = []
        
        # DuckDuckGo HTML interface
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, headers=headers, timeout=10.0)
            
            if response.status_code != 200:
                raise NetworkError(f"Search failed with status {response.status_code}")
            
            # Parse results
            soup = BeautifulSoup(response.text, "lxml")
            
            position = 1
            for result in soup.find_all("div", class_="result"):
                # Extract URL
                link_elem = result.find("a", class_="result__a", href=True)
                if not link_elem:
                    continue
                
                url = link_elem["href"]
                title = clean_text(link_elem.get_text())
                
                # Extract snippet
                snippet_elem = result.find("a", class_="result__snippet")
                snippet = clean_text(snippet_elem.get_text()) if snippet_elem else ""
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "position": position,
                })
                
                position += 1
                if len(results) >= num_results:
                    break
        
        return results


class BingSearchProvider(SearchProvider):
    """Bing search provider."""
    
    async def search(
        self,
        query: str,
        num_results: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search Bing and parse results."""
        results = []
        
        # Build search URL
        params = {
            "q": query,
            "count": min(num_results, 50),  # Bing limit
        }
        
        if language:
            params["setlang"] = language
        
        search_url = f"https://www.bing.com/search?{urllib.parse.urlencode(params)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, headers=headers, timeout=10.0)
            
            if response.status_code != 200:
                raise NetworkError(f"Search failed with status {response.status_code}")
            
            # Parse results
            soup = BeautifulSoup(response.text, "lxml")
            
            position = 1
            for li in soup.find_all("li", class_="b_algo"):
                # Extract URL and title
                h2 = li.find("h2")
                if not h2:
                    continue
                
                link_elem = h2.find("a", href=True)
                if not link_elem:
                    continue
                
                url = link_elem["href"]
                title = clean_text(link_elem.get_text())
                
                # Extract snippet
                snippet = ""
                snippet_elem = li.find("div", class_="b_caption")
                if snippet_elem:
                    p = snippet_elem.find("p")
                    if p:
                        snippet = clean_text(p.get_text())
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "position": position,
                })
                
                position += 1
                if len(results) >= num_results:
                    break
        
        return results


class Searcher:
    """Handles web search operations."""
    
    def __init__(self, client):
        self.client = client
        self.scraper = Scraper(client)
        
        # Initialize search providers
        self.providers = {
            SearchEngine.GOOGLE: GoogleSearchProvider(client),
            SearchEngine.DUCKDUCKGO: DuckDuckGoSearchProvider(client),
            SearchEngine.BING: BingSearchProvider(client),
        }
    
    def search(self, options: SearchOptions) -> SearchResult:
        """Perform web search synchronously."""
        return asyncio.run(self._search_async(options))
    
    async def _search_async(self, options: SearchOptions) -> SearchResult:
        """Perform web search asynchronously."""
        start_time = datetime.utcnow()
        
        try:
            # Validate query
            if not options.query.strip():
                raise ValidationError("Search query cannot be empty")
            
            # Get search provider
            provider = self.providers.get(options.engine)
            if not provider:
                raise ValidationError(f"Unsupported search engine: {options.engine}")
            
            if self.client.debug:
                console.print(f"[blue]Searching {options.engine.value} for: {options.query}[/blue]")
            
            # Perform search
            raw_results = await provider.search(
                query=options.query,
                num_results=options.num_results,
                start_date=options.start_date,
                end_date=options.end_date,
                location=options.location,
                language=options.language,
            )
            
            # Convert to SearchResultItem objects
            results = []
            for raw in raw_results:
                item = SearchResultItem(
                    title=raw["title"],
                    url=raw["url"],
                    snippet=raw["snippet"],
                    position=raw["position"],
                )
                results.append(item)
            
            if self.client.debug:
                console.print(f"[green]Found {len(results)} search results[/green]")
            
            # Scrape results if requested
            if options.scrape_results and results:
                await self._scrape_search_results(results, options)
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return SearchResult(
                success=True,
                query=options.query,
                engine=options.engine,
                results=results,
                total_results=len(results),
                duration=duration,
                searched_at=start_time,
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            if self.client.debug:
                console.print(f"[red]Search failed: {e}[/red]")
            
            return SearchResult(
                success=False,
                query=options.query,
                engine=options.engine,
                results=[],
                total_results=0,
                duration=duration,
                searched_at=start_time,
            )
    
    async def _scrape_search_results(
        self,
        results: List[SearchResultItem],
        options: SearchOptions
    ):
        """Scrape content from search results."""
        if self.client.debug:
            console.print(f"[blue]Scraping {len(results)} search results...[/blue]")
        
        # Create scraping tasks
        tasks = []
        for result in results:
            scrape_options = ScrapeOptions(
                url=result.url,
                formats=options.formats,
                timeout=options.timeout,
                only_main_content=True,
            )
            
            task = self._scrape_with_error_handling(scrape_options)
            tasks.append(task)
        
        # Run scraping concurrently
        scraped_results = await asyncio.gather(*tasks)
        
        # Attach scraped content to results
        for result, scraped in zip(results, scraped_results):
            if scraped:
                result.scraped_content = scraped
        
        if self.client.debug:
            successful = sum(1 for r in results if r.scraped_content and r.scraped_content.success)
            console.print(f"[green]Successfully scraped {successful}/{len(results)} results[/green]")
    
    async def _scrape_with_error_handling(
        self,
        options: ScrapeOptions
    ) -> Optional[Any]:
        """Scrape with error handling to not fail entire search."""
        try:
            # Use sync scraper for now (could be made async)
            return self.scraper.scrape(options)
        except Exception as e:
            if self.client.debug:
                console.print(f"[yellow]Failed to scrape {options.url}: {e}[/yellow]")
            return None