"""
Tests for utility functions.
"""

import pytest
from unittest.mock import Mock, patch
import httpx

from rapidcrawl.utils import (
    normalize_url,
    is_valid_url,
    get_domain,
    is_same_domain,
    resolve_url,
    clean_text,
    extract_links,
    extract_images,
    get_content_type,
    is_html_content,
    is_pdf_content,
    is_image_content,
    hash_url,
    sanitize_filename,
    estimate_read_time,
    truncate_text,
    parse_robots_txt,
    is_url_allowed,
)


class TestURLFunctions:
    """Test URL-related utility functions."""
    
    def test_normalize_url(self):
        """Test URL normalization."""
        # Add scheme if missing
        assert normalize_url("example.com") == "https://example.com/"
        
        # Remove trailing slash
        assert normalize_url("https://example.com/path/") == "https://example.com/path"
        
        # Remove fragment
        assert normalize_url("https://example.com#section") == "https://example.com/"
        
        # Lowercase domain
        assert normalize_url("https://EXAMPLE.COM") == "https://example.com/"
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com/path") is True
        assert is_valid_url("ftp://files.example.com") is True
        
        assert is_valid_url("not-a-url") is False
        assert is_valid_url("example.com") is False
        assert is_valid_url("") is False
    
    def test_get_domain(self):
        """Test domain extraction."""
        assert get_domain("https://example.com/path") == "example.com"
        assert get_domain("https://sub.example.com") == "sub.example.com"
        assert get_domain("http://EXAMPLE.COM") == "example.com"
    
    def test_is_same_domain(self):
        """Test same domain checking."""
        # Same domain
        assert is_same_domain(
            "https://example.com/page1",
            "https://example.com/page2"
        ) is True
        
        # Different domains
        assert is_same_domain(
            "https://example.com",
            "https://other.com"
        ) is False
        
        # Subdomain without allow_subdomains
        assert is_same_domain(
            "https://example.com",
            "https://sub.example.com",
            allow_subdomains=False
        ) is False
        
        # Subdomain with allow_subdomains
        assert is_same_domain(
            "https://example.com",
            "https://sub.example.com",
            allow_subdomains=True
        ) is True
    
    def test_resolve_url(self):
        """Test URL resolution."""
        base = "https://example.com/page"
        
        # Absolute URL
        assert resolve_url(base, "https://other.com") == "https://other.com"
        
        # Relative URL
        assert resolve_url(base, "/path") == "https://example.com/path"
        assert resolve_url(base, "subpage") == "https://example.com/subpage"
        
        # Protocol-relative URL
        assert resolve_url(base, "//cdn.example.com/file.js") == "https://cdn.example.com/file.js"


class TestTextFunctions:
    """Test text processing functions."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        # Remove extra whitespace
        assert clean_text("  Hello   World  ") == "Hello World"
        
        # Remove newlines and tabs
        assert clean_text("Hello\n\t\rWorld") == "Hello World"
        
        # Empty string
        assert clean_text("   ") == ""
    
    def test_estimate_read_time(self):
        """Test reading time estimation."""
        # 200 words at 200 wpm = 1 minute
        text = " ".join(["word"] * 200)
        assert estimate_read_time(text) == 1.0
        
        # 100 words at 200 wpm = 0.5 minutes
        text = " ".join(["word"] * 100)
        assert estimate_read_time(text) == 0.5
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs to be truncated"
        
        # Truncate with default suffix
        result = truncate_text(text, max_length=20)
        assert result == "This is a long te..."
        assert len(result) == 20
        
        # Custom suffix
        result = truncate_text(text, max_length=20, suffix=" [...]")
        assert result.endswith(" [...]")
        
        # No truncation needed
        short_text = "Short"
        assert truncate_text(short_text, max_length=10) == "Short"


class TestHTMLParsing:
    """Test HTML parsing functions."""
    
    def test_extract_links(self):
        """Test link extraction from HTML."""
        html = """
        <html>
            <a href="/page1">Page 1</a>
            <a href="https://example.com/page2">Page 2</a>
            <a href="page3">Page 3</a>
            <link href="/style.css" />
        </html>
        """
        base_url = "https://example.com"
        
        links = extract_links(html, base_url)
        
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        assert "https://example.com/page3" in links
        assert "https://example.com/style.css" in links
    
    def test_extract_images(self):
        """Test image URL extraction from HTML."""
        html = """
        <html>
            <img src="/image1.jpg" />
            <img src="https://cdn.example.com/image2.png" />
            <img data-src="/lazy.webp" />
        </html>
        """
        base_url = "https://example.com"
        
        images = extract_images(html, base_url)
        
        assert "https://example.com/image1.jpg" in images
        assert "https://cdn.example.com/image2.png" in images
        assert "https://example.com/lazy.webp" in images


class TestContentType:
    """Test content type functions."""
    
    def test_get_content_type(self):
        """Test content type extraction."""
        # Mock response with content-type header
        response = Mock(spec=httpx.Response)
        response.headers = {"content-type": "text/html; charset=utf-8"}
        
        mime_type, charset = get_content_type(response)
        assert mime_type == "text/html"
        assert charset == "utf-8"
        
        # No charset
        response.headers = {"content-type": "application/pdf"}
        mime_type, charset = get_content_type(response)
        assert mime_type == "application/pdf"
        assert charset == "utf-8"  # default
    
    def test_content_type_checks(self):
        """Test content type checking functions."""
        assert is_html_content("text/html") is True
        assert is_html_content("application/xhtml+xml") is True
        assert is_html_content("text/plain") is False
        
        assert is_pdf_content("application/pdf") is True
        assert is_pdf_content("text/html") is False
        
        assert is_image_content("image/jpeg") is True
        assert is_image_content("image/png") is True
        assert is_image_content("text/html") is False


class TestFileFunctions:
    """Test file-related functions."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Remove invalid characters
        assert sanitize_filename('file<>name?.txt') == "file__name_.txt"
        
        # Handle long filenames
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")
    
    def test_hash_url(self):
        """Test URL hashing."""
        url1 = "https://example.com/page1"
        url2 = "https://example.com/page2"
        
        hash1 = hash_url(url1)
        hash2 = hash_url(url2)
        
        # Same URL produces same hash
        assert hash1 == hash_url(url1)
        
        # Different URLs produce different hashes
        assert hash1 != hash2


class TestRobotsTxt:
    """Test robots.txt parsing."""
    
    def test_parse_robots_txt(self):
        """Test parsing robots.txt content."""
        robots_txt = """
        User-agent: *
        Disallow: /admin/
        Disallow: /private/
        Allow: /private/public/
        Crawl-delay: 1.5
        
        User-agent: RapidCrawl
        Disallow: /temp/
        Crawl-delay: 0.5
        
        Sitemap: https://example.com/sitemap.xml
        """
        
        # Parse for RapidCrawl user agent
        rules = parse_robots_txt(robots_txt, "RapidCrawl")
        
        assert "/temp/" in rules["disallow"]
        assert rules["crawl-delay"] == 0.5
        assert "https://example.com/sitemap.xml" in rules["sitemap"]
        
        # Parse for generic user agent
        rules = parse_robots_txt(robots_txt, "Googlebot")
        
        assert "/admin/" in rules["disallow"]
        assert "/private/" in rules["disallow"]
        assert "/private/public/" in rules["allow"]
        assert rules["crawl-delay"] == 1.5
    
    def test_is_url_allowed(self):
        """Test URL allowance checking."""
        rules = {
            "allow": ["/public/"],
            "disallow": ["/", "/private/"],
            "crawl-delay": None,
            "sitemap": []
        }
        
        # Disallowed paths
        assert is_url_allowed("https://example.com/private/data", rules) is False
        assert is_url_allowed("https://example.com/other", rules) is False
        
        # Allowed by specific rule
        assert is_url_allowed("https://example.com/public/page", rules) is True
        
        # More specific allow rule overrides disallow
        rules["allow"] = ["/private/public/"]
        assert is_url_allowed("https://example.com/private/public/data", rules) is True