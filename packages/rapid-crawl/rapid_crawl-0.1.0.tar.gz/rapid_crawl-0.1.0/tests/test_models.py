"""
Tests for RapidCrawl models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from rapidcrawl.models import (
    OutputFormat,
    CrawlStatus,
    SearchEngine,
    PageAction,
    ExtractSchema,
    ScrapeOptions,
    CrawlOptions,
    MapOptions,
    SearchOptions,
    ScrapeResult,
    CrawlResult,
    MapResult,
    SearchResult,
    SearchResultItem,
)


class TestEnums:
    """Test enum classes."""
    
    def test_output_format_values(self):
        """Test OutputFormat enum values."""
        assert OutputFormat.MARKDOWN.value == "markdown"
        assert OutputFormat.HTML.value == "html"
        assert OutputFormat.SCREENSHOT.value == "screenshot"
        assert OutputFormat.TEXT.value == "text"
    
    def test_crawl_status_values(self):
        """Test CrawlStatus enum values."""
        assert CrawlStatus.PENDING.value == "pending"
        assert CrawlStatus.RUNNING.value == "running"
        assert CrawlStatus.COMPLETED.value == "completed"
        assert CrawlStatus.FAILED.value == "failed"
    
    def test_search_engine_values(self):
        """Test SearchEngine enum values."""
        assert SearchEngine.GOOGLE.value == "google"
        assert SearchEngine.BING.value == "bing"
        assert SearchEngine.DUCKDUCKGO.value == "duckduckgo"


class TestPageAction:
    """Test PageAction model."""
    
    def test_click_action(self):
        """Test creating a click action."""
        action = PageAction(
            type="click",
            selector=".button",
            timeout=5000
        )
        assert action.type == "click"
        assert action.selector == ".button"
        assert action.timeout == 5000
    
    def test_wait_action(self):
        """Test creating a wait action."""
        action = PageAction(
            type="wait",
            value=2000
        )
        assert action.type == "wait"
        assert action.value == 2000
    
    def test_write_action(self):
        """Test creating a write action."""
        action = PageAction(
            type="write",
            selector="input[name='search']",
            value="test query"
        )
        assert action.type == "write"
        assert action.selector == "input[name='search']"
        assert action.value == "test query"
    
    def test_invalid_action_type(self):
        """Test invalid action type raises error."""
        with pytest.raises(ValidationError):
            PageAction(type="invalid", selector=".test")


class TestExtractSchema:
    """Test ExtractSchema model."""
    
    def test_basic_schema(self):
        """Test creating basic extraction schema."""
        schema = ExtractSchema(
            name="title",
            type="string",
            selector="h1"
        )
        assert schema.name == "title"
        assert schema.type == "string"
        assert schema.selector == "h1"
        assert schema.required is True
    
    def test_schema_with_all_fields(self):
        """Test schema with all fields."""
        schema = ExtractSchema(
            name="price",
            type="number",
            description="Product price",
            required=False,
            selector=".price",
            attribute="data-price",
            regex=r"[\d.]+",
            default=0
        )
        assert schema.name == "price"
        assert schema.type == "number"
        assert schema.required is False
        assert schema.default == 0


class TestScrapeOptions:
    """Test ScrapeOptions model."""
    
    def test_minimal_options(self):
        """Test creating minimal scrape options."""
        options = ScrapeOptions(url="https://example.com")
        assert str(options.url) == "https://example.com/"
        assert options.formats == [OutputFormat.MARKDOWN]
        assert options.timeout == 30000
        assert options.only_main_content is True
    
    def test_full_options(self):
        """Test creating scrape options with all fields."""
        actions = [PageAction(type="click", selector=".more")]
        schema = [ExtractSchema(name="title", selector="h1")]
        
        options = ScrapeOptions(
            url="https://example.com",
            formats=[OutputFormat.HTML, OutputFormat.SCREENSHOT],
            headers={"User-Agent": "Test"},
            include_links=True,
            include_images=True,
            wait_for=".content",
            timeout=60000,
            actions=actions,
            extract_schema=schema,
            extract_prompt="Extract product info",
            mobile=True,
            location="US",
            language="en",
            remove_tags=["script", "style"],
            only_main_content=False
        )
        
        assert len(options.formats) == 2
        assert options.mobile is True
        assert options.location == "US"
        assert len(options.actions) == 1
    
    def test_invalid_url(self):
        """Test invalid URL raises error."""
        with pytest.raises(ValidationError):
            ScrapeOptions(url="not-a-url")


class TestCrawlOptions:
    """Test CrawlOptions model."""
    
    def test_minimal_options(self):
        """Test minimal crawl options."""
        options = CrawlOptions(url="https://example.com")
        assert options.max_depth == 3
        assert options.max_pages == 100
        assert options.allow_subdomains is False
    
    def test_depth_limits(self):
        """Test depth limit validation."""
        # Valid depth
        options = CrawlOptions(url="https://example.com", max_depth=5)
        assert options.max_depth == 5
        
        # Too deep
        with pytest.raises(ValidationError):
            CrawlOptions(url="https://example.com", max_depth=15)
        
        # Too shallow
        with pytest.raises(ValidationError):
            CrawlOptions(url="https://example.com", max_depth=0)
    
    def test_page_limits(self):
        """Test page limit validation."""
        # Valid limit
        options = CrawlOptions(url="https://example.com", max_pages=5000)
        assert options.max_pages == 5000
        
        # Too many
        with pytest.raises(ValidationError):
            CrawlOptions(url="https://example.com", max_pages=20000)


class TestMapOptions:
    """Test MapOptions model."""
    
    def test_minimal_options(self):
        """Test minimal map options."""
        options = MapOptions(url="https://example.com")
        assert options.limit == 5000
        assert options.ignore_sitemap is False
        assert options.include_subdomains is False
    
    def test_with_search(self):
        """Test map options with search."""
        options = MapOptions(
            url="https://example.com",
            search="product",
            limit=1000
        )
        assert options.search == "product"
        assert options.limit == 1000


class TestSearchOptions:
    """Test SearchOptions model."""
    
    def test_minimal_options(self):
        """Test minimal search options."""
        options = SearchOptions(query="test query")
        assert options.query == "test query"
        assert options.engine == SearchEngine.GOOGLE
        assert options.num_results == 10
        assert options.scrape_results is False
    
    def test_empty_query_validation(self):
        """Test empty query raises error."""
        with pytest.raises(ValidationError):
            SearchOptions(query="")
    
    def test_date_filtering(self):
        """Test search with date filtering."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        
        options = SearchOptions(
            query="news",
            start_date=start,
            end_date=end
        )
        assert options.start_date == start
        assert options.end_date == end


class TestScrapeResult:
    """Test ScrapeResult model."""
    
    def test_successful_result(self):
        """Test successful scrape result."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            title="Example Page",
            content={"markdown": "# Example"},
            status_code=200,
            load_time=1.5
        )
        assert result.success is True
        assert result.title == "Example Page"
        assert result.content["markdown"] == "# Example"
    
    def test_failed_result(self):
        """Test failed scrape result."""
        result = ScrapeResult(
            success=False,
            url="https://example.com",
            error="Connection timeout",
            status_code=None
        )
        assert result.success is False
        assert result.error == "Connection timeout"
        assert result.status_code is None
    
    def test_timestamp_auto_set(self):
        """Test scraped_at timestamp is auto-set."""
        result = ScrapeResult(
            success=True,
            url="https://example.com"
        )
        assert isinstance(result.scraped_at, datetime)


class TestSearchResultItem:
    """Test SearchResultItem model."""
    
    def test_basic_item(self):
        """Test basic search result item."""
        item = SearchResultItem(
            title="Test Page",
            url="https://example.com",
            snippet="This is a test page...",
            position=1
        )
        assert item.title == "Test Page"
        assert item.position == 1
        assert item.scraped_content is None
    
    def test_item_with_scraped_content(self):
        """Test item with scraped content."""
        scraped = ScrapeResult(
            success=True,
            url="https://example.com",
            content={"markdown": "# Test"}
        )
        
        item = SearchResultItem(
            title="Test Page",
            url="https://example.com",
            snippet="Test snippet",
            position=1,
            scraped_content=scraped
        )
        assert item.scraped_content.success is True