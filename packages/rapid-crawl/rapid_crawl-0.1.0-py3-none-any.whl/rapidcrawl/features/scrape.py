"""
Web scraping functionality for RapidCrawl.
"""

import asyncio
import base64
import io
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright, Page, Browser
from playwright.sync_api import sync_playwright
import html2text
from markdownify import markdownify as md
from PIL import Image
import PyPDF2
from rich.console import Console

from rapidcrawl.models import ScrapeOptions, ScrapeResult, OutputFormat, PageAction
from rapidcrawl.exceptions import ScrapingError, TimeoutError, ValidationError
from rapidcrawl.utils import (
    normalize_url,
    is_valid_url,
    clean_text,
    extract_links,
    extract_images,
    get_content_type,
    is_html_content,
    is_pdf_content,
    is_image_content,
    retry_on_network_error,
)

console = Console()


class Scraper:
    """Handles web scraping operations."""
    
    def __init__(self, client):
        self.client = client
        self._browser: Optional[Browser] = None
        self._async_browser: Optional[Browser] = None
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0  # No line wrapping
    
    def scrape(self, options: ScrapeOptions) -> ScrapeResult:
        """Scrape a URL synchronously."""
        try:
            # Validate URL
            if not is_valid_url(str(options.url)):
                raise ValidationError(f"Invalid URL: {options.url}")
            
            # Normalize URL
            url = normalize_url(str(options.url))
            
            # Check if we need browser for dynamic content
            needs_browser = (
                options.wait_for or
                options.actions or
                OutputFormat.SCREENSHOT in options.formats or
                options.mobile
            )
            
            if needs_browser:
                return self._scrape_with_browser(url, options)
            else:
                return self._scrape_with_httpx(url, options)
                
        except Exception as e:
            return ScrapeResult(
                success=False,
                url=str(options.url),
                error=str(e),
                scraped_at=datetime.utcnow()
            )
    
    def _scrape_with_httpx(self, url: str, options: ScrapeOptions) -> ScrapeResult:
        """Scrape using httpx (for static content)."""
        start_time = datetime.utcnow()
        
        try:
            # Make request
            response = self._make_request(url, options)
            
            # Get content type
            mime_type, charset = get_content_type(response)
            
            # Handle different content types
            if is_html_content(mime_type):
                return self._process_html(url, response.text, options, start_time)
            elif is_pdf_content(mime_type):
                return self._process_pdf(url, response.content, options, start_time)
            elif is_image_content(mime_type):
                return self._process_image(url, response.content, mime_type, options, start_time)
            else:
                return self._process_other(url, response, mime_type, options, start_time)
                
        except httpx.TimeoutException:
            raise TimeoutError(f"Request timed out after {options.timeout}ms", timeout=options.timeout/1000)
        except httpx.NetworkError as e:
            raise ScrapingError(f"Network error: {e}", url=url)
        except Exception as e:
            raise ScrapingError(f"Failed to scrape URL: {e}", url=url)
    
    @retry_on_network_error(max_attempts=3)
    def _make_request(self, url: str, options: ScrapeOptions) -> httpx.Response:
        """Make HTTP request with retries."""
        headers = options.headers or {}
        headers.update(self.client._get_default_headers())
        
        # Add location/language headers if specified
        if options.location:
            headers["X-Forwarded-For"] = self._get_location_ip(options.location)
        if options.language:
            headers["Accept-Language"] = options.language
        
        response = self.client._client.get(
            url,
            headers=headers,
            timeout=options.timeout / 1000,  # Convert to seconds
            follow_redirects=True
        )
        
        response.raise_for_status()
        return response
    
    def _scrape_with_browser(self, url: str, options: ScrapeOptions) -> ScrapeResult:
        """Scrape using Playwright (for dynamic content)."""
        start_time = datetime.utcnow()
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            
            try:
                # Create context with options
                context_options = {}
                if options.mobile:
                    context_options.update(p.devices["iPhone 12"])
                if options.location:
                    context_options["geolocation"] = self._get_geolocation(options.location)
                    context_options["permissions"] = ["geolocation"]
                if options.language:
                    context_options["locale"] = options.language
                
                context = browser.new_context(**context_options)
                page = context.new_page()
                
                # Set headers
                if options.headers:
                    page.set_extra_http_headers(options.headers)
                
                # Navigate to URL
                page.goto(url, timeout=options.timeout, wait_until="networkidle")
                
                # Wait for specific element if requested
                if options.wait_for:
                    page.wait_for_selector(options.wait_for, timeout=options.timeout)
                
                # Perform actions
                if options.actions:
                    self._perform_actions(page, options.actions)
                
                # Get content
                html = page.content()
                
                # Take screenshot if requested
                screenshot = None
                if OutputFormat.SCREENSHOT in options.formats:
                    screenshot = page.screenshot(full_page=True)
                
                # Process HTML
                result = self._process_html(url, html, options, start_time)
                
                # Add screenshot to content
                if screenshot:
                    result.content = result.content or {}
                    result.content["screenshot"] = base64.b64encode(screenshot).decode()
                
                return result
                
            finally:
                browser.close()
    
    def _perform_actions(self, page: Page, actions: List[PageAction]):
        """Perform actions on the page."""
        for action in actions:
            timeout = action.timeout or 30000
            
            if action.type == "click":
                page.click(action.selector, timeout=timeout)
            elif action.type == "wait":
                if action.selector:
                    page.wait_for_selector(action.selector, timeout=timeout)
                else:
                    page.wait_for_timeout(action.value or 1000)
            elif action.type == "write":
                page.fill(action.selector, str(action.value), timeout=timeout)
            elif action.type == "scroll":
                if action.value:
                    page.evaluate(f"window.scrollTo(0, {action.value})")
                else:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif action.type == "screenshot":
                # Screenshot handled separately
                pass
    
    def _process_html(
        self,
        url: str,
        html: str,
        options: ScrapeOptions,
        start_time: datetime
    ) -> ScrapeResult:
        """Process HTML content."""
        soup = BeautifulSoup(html, "lxml")
        
        # Remove unwanted tags
        if options.remove_tags:
            for tag in options.remove_tags:
                for element in soup.find_all(tag):
                    element.decompose()
        
        # Extract main content if requested
        if options.only_main_content:
            main_content = self._extract_main_content(soup)
            if main_content:
                soup = main_content
        
        # Extract metadata
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        
        # Generate requested formats
        content = {}
        
        if OutputFormat.MARKDOWN in options.formats:
            content["markdown"] = self._html_to_markdown(str(soup))
        
        if OutputFormat.HTML in options.formats:
            content["html"] = str(soup)
        
        if OutputFormat.RAW_HTML in options.formats:
            content["rawHtml"] = html
        
        if OutputFormat.TEXT in options.formats:
            content["text"] = clean_text(soup.get_text())
        
        if OutputFormat.LINKS in options.formats:
            content["links"] = extract_links(str(soup), url)
        
        # Extract structured data if schema provided
        structured_data = None
        if options.extract_schema:
            structured_data = self._extract_structured_data(soup, options.extract_schema)
        elif options.extract_prompt:
            structured_data = self._extract_with_prompt(soup, options.extract_prompt)
        
        # Extract links and images if requested
        links = None
        images = None
        if options.include_links:
            links = extract_links(str(soup), url)
        if options.include_images:
            images = extract_images(str(soup), url)
        
        # Calculate load time
        load_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ScrapeResult(
            success=True,
            url=url,
            title=title,
            description=description,
            content=content,
            metadata={
                "language": self._detect_language(soup),
                "author": self._extract_author(soup),
                "published_date": self._extract_published_date(soup),
            },
            links=links,
            images=images,
            structured_data=structured_data,
            status_code=200,
            load_time=load_time,
            scraped_at=start_time
        )
    
    def _process_pdf(
        self,
        url: str,
        content: bytes,
        options: ScrapeOptions,
        start_time: datetime
    ) -> ScrapeResult:
        """Process PDF content."""
        try:
            # Read PDF
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            # Clean text
            text_content = clean_text(text_content)
            
            # Generate requested formats
            content_dict = {}
            
            if OutputFormat.TEXT in options.formats:
                content_dict["text"] = text_content
            
            if OutputFormat.MARKDOWN in options.formats:
                # Convert text to basic markdown
                content_dict["markdown"] = text_content
            
            # Extract metadata
            metadata = {
                "pages": len(pdf_reader.pages),
                "title": pdf_reader.metadata.get("/Title", ""),
                "author": pdf_reader.metadata.get("/Author", ""),
                "subject": pdf_reader.metadata.get("/Subject", ""),
            }
            
            load_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ScrapeResult(
                success=True,
                url=url,
                title=metadata.get("title"),
                content=content_dict,
                metadata=metadata,
                status_code=200,
                load_time=load_time,
                scraped_at=start_time
            )
            
        except Exception as e:
            raise ScrapingError(f"Failed to process PDF: {e}", url=url)
    
    def _process_image(
        self,
        url: str,
        content: bytes,
        mime_type: str,
        options: ScrapeOptions,
        start_time: datetime
    ) -> ScrapeResult:
        """Process image content."""
        try:
            # Open image
            img = Image.open(io.BytesIO(content))
            
            # Get image info
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
            }
            
            # Generate requested formats
            content_dict = {}
            
            if OutputFormat.SCREENSHOT in options.formats:
                # Return base64 encoded image
                content_dict["screenshot"] = base64.b64encode(content).decode()
            
            load_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ScrapeResult(
                success=True,
                url=url,
                content=content_dict,
                metadata=metadata,
                status_code=200,
                load_time=load_time,
                scraped_at=start_time
            )
            
        except Exception as e:
            raise ScrapingError(f"Failed to process image: {e}", url=url)
    
    def _process_other(
        self,
        url: str,
        response: httpx.Response,
        mime_type: str,
        options: ScrapeOptions,
        start_time: datetime
    ) -> ScrapeResult:
        """Process other content types."""
        content_dict = {}
        
        if OutputFormat.TEXT in options.formats:
            try:
                content_dict["text"] = response.text
            except:
                content_dict["text"] = f"Binary content ({mime_type})"
        
        load_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ScrapeResult(
            success=True,
            url=url,
            content=content_dict,
            metadata={"content_type": mime_type},
            status_code=response.status_code,
            load_time=load_time,
            scraped_at=start_time
        )
    
    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown."""
        # Use markdownify for better conversion
        markdown = md(html, heading_style="ATX", bullets="-")
        
        # Clean up excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        return markdown.strip()
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract main content from HTML."""
        # Look for common main content containers
        main_selectors = [
            "main",
            "article",
            '[role="main"]',
            "#main",
            ".main",
            "#content",
            ".content",
            "#article",
            ".article",
        ]
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element:
                return BeautifulSoup(str(element), "lxml")
        
        # If no main content found, return body
        body = soup.find("body")
        if body:
            return BeautifulSoup(str(body), "lxml")
        
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract title from HTML."""
        # Try meta og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        # Try regular title tag
        title_tag = soup.find("title")
        if title_tag:
            return clean_text(title_tag.get_text())
        
        # Try h1
        h1 = soup.find("h1")
        if h1:
            return clean_text(h1.get_text())
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from HTML."""
        # Try meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
        
        # Try og:description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from HTML."""
        # Try meta author
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author and meta_author.get("content"):
            return meta_author["content"]
        
        # Try article:author
        article_author = soup.find("meta", property="article:author")
        if article_author and article_author.get("content"):
            return article_author["content"]
        
        return None
    
    def _extract_published_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract published date from HTML."""
        # Try various meta tags
        date_properties = [
            "article:published_time",
            "datePublished",
            "pubdate",
            "publish_date",
        ]
        
        for prop in date_properties:
            meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if meta and meta.get("content"):
                return meta["content"]
        
        # Try time tag
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            return time_tag["datetime"]
        
        return None
    
    def _detect_language(self, soup: BeautifulSoup) -> Optional[str]:
        """Detect language from HTML."""
        # Check html lang attribute
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            return html_tag["lang"]
        
        # Check meta language
        meta_lang = soup.find("meta", attrs={"name": "language"})
        if meta_lang and meta_lang.get("content"):
            return meta_lang["content"]
        
        return None
    
    def _extract_structured_data(
        self,
        soup: BeautifulSoup,
        schema: List[Any]
    ) -> Dict[str, Any]:
        """Extract structured data based on schema."""
        result = {}
        
        for field in schema:
            name = field.name
            selector = field.selector
            attribute = field.attribute
            
            if selector:
                element = soup.select_one(selector)
                if element:
                    if attribute:
                        value = element.get(attribute)
                    else:
                        value = clean_text(element.get_text())
                    
                    # Type conversion
                    if field.type == "number":
                        try:
                            value = float(re.sub(r'[^\d.-]', '', value))
                        except:
                            value = field.default
                    elif field.type == "boolean":
                        value = value.lower() in ["true", "yes", "1"]
                    
                    result[name] = value
                elif field.required:
                    result[name] = field.default
        
        return result
    
    def _extract_with_prompt(self, soup: BeautifulSoup, prompt: str) -> Dict[str, Any]:
        """Extract data using natural language prompt."""
        # This would integrate with an LLM in a full implementation
        # For now, return a placeholder
        return {
            "prompt": prompt,
            "note": "LLM extraction not implemented in this version"
        }
    
    def _get_location_ip(self, location: str) -> str:
        """Get IP address for location."""
        # This would use a geolocation service in production
        # For now, return a placeholder
        location_ips = {
            "US": "1.1.1.1",
            "UK": "2.2.2.2",
            "CA": "3.3.3.3",
        }
        return location_ips.get(location.upper(), "1.1.1.1")
    
    def _get_geolocation(self, location: str) -> Dict[str, float]:
        """Get geolocation coordinates."""
        # This would use a geolocation service in production
        # For now, return placeholder coordinates
        locations = {
            "US": {"latitude": 37.7749, "longitude": -122.4194},  # San Francisco
            "UK": {"latitude": 51.5074, "longitude": -0.1278},   # London
            "CA": {"latitude": 43.6532, "longitude": -79.3832},  # Toronto
        }
        return locations.get(location.upper(), locations["US"])