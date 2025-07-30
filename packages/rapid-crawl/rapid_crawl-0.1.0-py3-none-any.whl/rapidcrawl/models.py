"""
Data models and schemas for the RapidCrawl package.
"""

from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator


class OutputFormat(str, Enum):
    """Supported output formats for scraping."""
    MARKDOWN = "markdown"
    HTML = "html"
    RAW_HTML = "rawHtml"
    SCREENSHOT = "screenshot"
    LINKS = "links"
    TEXT = "text"
    STRUCTURED = "structured"


class CrawlStatus(str, Enum):
    """Status of a crawl job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchEngine(str, Enum):
    """Supported search engines."""
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"


class PageAction(BaseModel):
    """Action to perform on a page (click, wait, write)."""
    type: Literal["click", "wait", "write", "scroll", "screenshot"]
    selector: Optional[str] = None
    value: Optional[Union[str, int]] = None
    timeout: Optional[int] = Field(None, description="Timeout in milliseconds")


class ExtractSchema(BaseModel):
    """Schema for structured data extraction."""
    name: str = Field(..., description="Name of the field to extract")
    type: Literal["string", "number", "boolean", "array", "object"] = "string"
    description: Optional[str] = None
    required: bool = True
    selector: Optional[str] = Field(None, description="CSS selector for the field")
    attribute: Optional[str] = Field(None, description="HTML attribute to extract")
    regex: Optional[str] = Field(None, description="Regex pattern to extract")
    default: Optional[Any] = None


class ScrapeOptions(BaseModel):
    """Options for scraping a single URL."""
    url: HttpUrl
    formats: List[OutputFormat] = Field(
        default=[OutputFormat.MARKDOWN],
        description="Output formats to generate"
    )
    headers: Optional[Dict[str, str]] = None
    include_links: bool = Field(False, description="Include all links found on the page")
    include_images: bool = Field(False, description="Include image URLs")
    wait_for: Optional[str] = Field(None, description="CSS selector to wait for")
    timeout: int = Field(30000, description="Timeout in milliseconds")
    actions: Optional[List[PageAction]] = Field(None, description="Actions to perform on the page")
    extract_schema: Optional[List[ExtractSchema]] = Field(
        None,
        description="Schema for structured extraction"
    )
    extract_prompt: Optional[str] = Field(
        None,
        description="Natural language prompt for extraction"
    )
    mobile: bool = Field(False, description="Use mobile viewport")
    location: Optional[str] = Field(None, description="Geographic location for the request")
    language: Optional[str] = Field(None, description="Language preference")
    remove_tags: Optional[List[str]] = Field(
        None,
        description="HTML tags to remove from output"
    )
    only_main_content: bool = Field(True, description="Extract only main content")
    
    class Config:
        json_encoders = {HttpUrl: str}


class CrawlOptions(BaseModel):
    """Options for crawling a website."""
    url: HttpUrl
    max_depth: int = Field(3, ge=1, le=10, description="Maximum crawl depth")
    max_pages: int = Field(100, ge=1, le=10000, description="Maximum pages to crawl")
    include_patterns: Optional[List[str]] = Field(
        None,
        description="URL patterns to include"
    )
    exclude_patterns: Optional[List[str]] = Field(
        None,
        description="URL patterns to exclude"
    )
    allow_subdomains: bool = Field(False, description="Allow crawling subdomains")
    formats: List[OutputFormat] = Field(
        default=[OutputFormat.MARKDOWN],
        description="Output formats for each page"
    )
    headers: Optional[Dict[str, str]] = None
    wait_for: Optional[str] = Field(None, description="CSS selector to wait for on each page")
    timeout: int = Field(30000, description="Timeout per page in milliseconds")
    webhook_url: Optional[HttpUrl] = Field(None, description="Webhook for progress updates")
    extract_schema: Optional[List[ExtractSchema]] = Field(
        None,
        description="Schema for structured extraction from each page"
    )
    limit_rate: Optional[int] = Field(
        None,
        description="Rate limit in requests per second"
    )
    
    class Config:
        json_encoders = {HttpUrl: str}


class MapOptions(BaseModel):
    """Options for mapping a website."""
    url: HttpUrl
    search: Optional[str] = Field(None, description="Filter URLs by search term")
    ignore_sitemap: bool = Field(False, description="Ignore sitemap.xml")
    include_subdomains: bool = Field(False, description="Include subdomain URLs")
    limit: int = Field(5000, ge=1, le=50000, description="Maximum URLs to return")
    
    class Config:
        json_encoders = {HttpUrl: str}


class SearchOptions(BaseModel):
    """Options for web search."""
    query: str = Field(..., min_length=1, description="Search query")
    engine: SearchEngine = Field(SearchEngine.GOOGLE, description="Search engine to use")
    num_results: int = Field(10, ge=1, le=100, description="Number of results to return")
    start_date: Optional[datetime] = Field(None, description="Filter results after this date")
    end_date: Optional[datetime] = Field(None, description="Filter results before this date")
    location: Optional[str] = Field(None, description="Geographic location for search")
    language: Optional[str] = Field(None, description="Language for search results")
    scrape_results: bool = Field(False, description="Scrape content from result URLs")
    formats: List[OutputFormat] = Field(
        default=[OutputFormat.MARKDOWN],
        description="Output formats when scraping results"
    )
    timeout: int = Field(30000, description="Timeout in milliseconds")


class ScrapeResult(BaseModel):
    """Result from scraping a single URL."""
    success: bool
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = Field(
        None,
        description="Content in requested formats"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Page metadata"
    )
    links: Optional[List[str]] = None
    images: Optional[List[str]] = None
    structured_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    load_time: Optional[float] = Field(None, description="Page load time in seconds")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class CrawlProgress(BaseModel):
    """Progress update for a crawl job."""
    job_id: str
    status: CrawlStatus
    pages_crawled: int
    pages_found: int
    pages_failed: int
    current_url: Optional[str] = None
    depth: int
    duration: float = Field(..., description="Duration in seconds")
    estimated_time_remaining: Optional[float] = None


class CrawlResult(BaseModel):
    """Result from crawling a website."""
    job_id: str
    status: CrawlStatus
    url: str
    pages: List[ScrapeResult]
    total_pages: int
    pages_crawled: int
    pages_failed: int
    duration: float = Field(..., description="Total duration in seconds")
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class MapResult(BaseModel):
    """Result from mapping a website."""
    success: bool
    url: str
    urls: List[str]
    total_urls: int
    sitemap_found: bool
    duration: float = Field(..., description="Mapping duration in seconds")
    mapped_at: datetime = Field(default_factory=datetime.utcnow)


class SearchResultItem(BaseModel):
    """A single search result item."""
    title: str
    url: str
    snippet: str
    position: int
    scraped_content: Optional[ScrapeResult] = None


class SearchResult(BaseModel):
    """Result from web search."""
    success: bool
    query: str
    engine: SearchEngine
    results: List[SearchResultItem]
    total_results: int
    duration: float = Field(..., description="Search duration in seconds")
    searched_at: datetime = Field(default_factory=datetime.utcnow)