"""
RapidCrawl - A powerful Python SDK for web scraping, crawling, and data extraction.

This package provides a comprehensive toolkit for extracting data from websites,
handling dynamic content, and converting web pages into clean, structured formats
suitable for AI and LLM applications.
"""

from rapidcrawl.client import RapidCrawlApp
from rapidcrawl.exceptions import (
    RapidCrawlError,
    AuthenticationError,
    RateLimitError,
    ScrapingError,
    ValidationError,
)
from rapidcrawl.models import (
    ScrapeOptions,
    CrawlOptions,
    MapOptions,
    SearchOptions,
    ExtractSchema,
    ScrapeResult,
    CrawlResult,
    MapResult,
    SearchResult,
)

__version__ = "0.1.0"
__author__ = "Ahsan Mahmood"
__email__ = "aoneahsan@gmail.com"

__all__ = [
    "RapidCrawlApp",
    "RapidCrawlError",
    "AuthenticationError",
    "RateLimitError",
    "ScrapingError",
    "ValidationError",
    "ScrapeOptions",
    "CrawlOptions",
    "MapOptions",
    "SearchOptions",
    "ExtractSchema",
    "ScrapeResult",
    "CrawlResult",
    "MapResult",
    "SearchResult",
]