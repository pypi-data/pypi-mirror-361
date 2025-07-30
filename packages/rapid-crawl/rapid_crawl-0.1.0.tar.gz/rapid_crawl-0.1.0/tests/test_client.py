"""
Tests for the RapidCrawl client.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import AuthenticationError, ConfigurationError


class TestRapidCrawlApp:
    """Test cases for RapidCrawlApp client."""
    
    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        app = RapidCrawlApp(api_key="test-key")
        assert app.api_key == "test-key"
        assert app.base_url == "https://api.rapidcrawl.io/v1"
        assert app.timeout == 30.0
        assert app.max_retries == 3
    
    def test_init_with_env_vars(self):
        """Test client initialization with environment variables."""
        with patch.dict(os.environ, {
            "RAPIDCRAWL_API_KEY": "env-key",
            "RAPIDCRAWL_BASE_URL": "https://custom.api.com",
            "RAPIDCRAWL_TIMEOUT": "60",
            "RAPIDCRAWL_MAX_RETRIES": "5"
        }):
            app = RapidCrawlApp()
            assert app.api_key == "env-key"
            assert app.base_url == "https://custom.api.com"
            assert app.timeout == 60.0
            assert app.max_retries == 5
    
    def test_init_without_api_key_warning(self):
        """Test client initialization without API key shows warning."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.warns(UserWarning, match="No API key provided"):
                app = RapidCrawlApp()
                assert app.api_key == "self-hosted"
    
    def test_default_headers(self):
        """Test default headers are set correctly."""
        app = RapidCrawlApp(api_key="test-key")
        headers = app._get_default_headers()
        
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["User-Agent"] == "RapidCrawl/0.1.0 Python"
        assert headers["Content-Type"] == "application/json"
    
    def test_scrape_url_basic(self):
        """Test basic scrape_url functionality."""
        app = RapidCrawlApp()
        
        # Mock the scraper
        with patch.object(app.scraper, 'scrape') as mock_scrape:
            mock_result = Mock()
            mock_result.success = True
            mock_result.content = {"markdown": "# Test Content"}
            mock_scrape.return_value = mock_result
            
            result = app.scrape_url("https://example.com")
            
            assert result.success
            assert result.content["markdown"] == "# Test Content"
            mock_scrape.assert_called_once()
    
    def test_scrape_url_with_formats(self):
        """Test scrape_url with multiple formats."""
        app = RapidCrawlApp()
        
        with patch.object(app.scraper, 'scrape') as mock_scrape:
            app.scrape_url(
                "https://example.com",
                formats=["markdown", "html", "screenshot"]
            )
            
            # Check that formats were converted to enums
            call_args = mock_scrape.call_args[0][0]
            assert len(call_args.formats) == 3
            assert all(hasattr(f, 'value') for f in call_args.formats)
    
    def test_crawl_url_basic(self):
        """Test basic crawl_url functionality."""
        app = RapidCrawlApp()
        
        with patch.object(app.crawler, 'crawl') as mock_crawl:
            mock_result = Mock()
            mock_result.status = "completed"
            mock_result.pages_crawled = 10
            mock_crawl.return_value = mock_result
            
            result = app.crawl_url("https://example.com", max_pages=10)
            
            assert result.status == "completed"
            assert result.pages_crawled == 10
            
            # Check options were passed correctly
            call_args = mock_crawl.call_args[0][0]
            assert call_args.max_pages == 10
            assert str(call_args.url) == "https://example.com"
    
    def test_map_url_basic(self):
        """Test basic map_url functionality."""
        app = RapidCrawlApp()
        
        with patch.object(app.mapper, 'map') as mock_map:
            mock_result = Mock()
            mock_result.success = True
            mock_result.total_urls = 100
            mock_result.urls = ["https://example.com/1", "https://example.com/2"]
            mock_map.return_value = mock_result
            
            result = app.map_url("https://example.com", limit=100)
            
            assert result.success
            assert result.total_urls == 100
            assert len(result.urls) == 2
    
    def test_search_basic(self):
        """Test basic search functionality."""
        app = RapidCrawlApp()
        
        with patch.object(app.searcher, 'search') as mock_search:
            mock_result = Mock()
            mock_result.success = True
            mock_result.total_results = 5
            mock_search.return_value = mock_result
            
            result = app.search("python tutorials", num_results=5)
            
            assert result.success
            assert result.total_results == 5
            
            # Check options
            call_args = mock_search.call_args[0][0]
            assert call_args.query == "python tutorials"
            assert call_args.num_results == 5
    
    def test_extract_single_url(self):
        """Test extract with single URL."""
        app = RapidCrawlApp()
        
        with patch.object(app.scraper, 'scrape') as mock_scrape:
            mock_result = Mock()
            mock_result.success = True
            mock_result.structured_data = {"title": "Test", "price": 29.99}
            mock_scrape.return_value = mock_result
            
            schema = [
                {"name": "title", "selector": "h1"},
                {"name": "price", "selector": ".price", "type": "number"}
            ]
            
            result = app.extract("https://example.com", schema=schema)
            
            # Should return single result, not list
            assert not isinstance(result, list)
            assert result.success
            assert result.structured_data["title"] == "Test"
    
    def test_extract_multiple_urls(self):
        """Test extract with multiple URLs."""
        app = RapidCrawlApp()
        
        with patch.object(app.scraper, 'scrape') as mock_scrape:
            mock_result = Mock()
            mock_result.success = True
            mock_scrape.return_value = mock_result
            
            urls = ["https://example.com/1", "https://example.com/2"]
            results = app.extract(urls, prompt="Extract product info")
            
            # Should return list
            assert isinstance(results, list)
            assert len(results) == 2
            assert mock_scrape.call_count == 2
    
    def test_context_manager(self):
        """Test client works as context manager."""
        with patch('rapidcrawl.client.httpx.Client') as mock_client:
            with RapidCrawlApp() as app:
                assert app is not None
            
            # Check client was closed
            mock_client.return_value.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test client works as async context manager."""
        with patch('rapidcrawl.client.httpx.AsyncClient') as mock_async_client:
            async with RapidCrawlApp() as app:
                # Access async_client to trigger creation
                _ = app.async_client
            
            # Check async client was closed
            mock_async_client.return_value.aclose.assert_called()
    
    @pytest.mark.asyncio
    async def test_crawl_url_async(self):
        """Test async crawl functionality."""
        app = RapidCrawlApp()
        
        with patch.object(app.crawler, 'crawl_async') as mock_crawl:
            mock_result = Mock()
            mock_result.status = "completed"
            mock_crawl.return_value = mock_result
            
            result = await app.crawl_url_async("https://example.com")
            
            assert result.status == "completed"
            mock_crawl.assert_called_once()