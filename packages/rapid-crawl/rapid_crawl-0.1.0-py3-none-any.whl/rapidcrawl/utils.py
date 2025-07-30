"""
Utility functions for the RapidCrawl package.
"""

import re
import time
import hashlib
import mimetypes
from typing import Optional, Dict, Any, List, Union, Tuple
from urllib.parse import urlparse, urljoin, urlunparse
from functools import wraps
import asyncio
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from rapidcrawl.exceptions import RateLimitError, NetworkError

console = Console()


def normalize_url(url: str) -> str:
    """Normalize a URL to ensure consistency."""
    parsed = urlparse(url)
    
    # Ensure scheme
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)
    
    # Remove trailing slash from path
    path = parsed.path.rstrip("/") or "/"
    
    # Remove fragment
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        path,
        parsed.params,
        parsed.query,
        ""
    ))
    
    return normalized


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc.lower()


def is_same_domain(url1: str, url2: str, allow_subdomains: bool = False) -> bool:
    """Check if two URLs are from the same domain."""
    domain1 = get_domain(url1)
    domain2 = get_domain(url2)
    
    if domain1 == domain2:
        return True
    
    if allow_subdomains:
        # Check if one is a subdomain of the other
        parts1 = domain1.split(".")
        parts2 = domain2.split(".")
        
        if len(parts1) > len(parts2):
            longer, shorter = parts1, parts2
        else:
            longer, shorter = parts2, parts1
        
        # Check if shorter domain is suffix of longer domain
        return longer[-len(shorter):] == shorter
    
    return False


def resolve_url(base_url: str, url: str) -> str:
    """Resolve a URL relative to a base URL."""
    return urljoin(base_url, url)


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def extract_links(html: str, base_url: str) -> List[str]:
    """Extract all links from HTML content."""
    soup = BeautifulSoup(html, "lxml")
    links = set()
    
    for tag in soup.find_all(["a", "link"]):
        href = tag.get("href")
        if href:
            absolute_url = resolve_url(base_url, href)
            if is_valid_url(absolute_url):
                links.add(normalize_url(absolute_url))
    
    return list(links)


def extract_images(html: str, base_url: str) -> List[str]:
    """Extract all image URLs from HTML content."""
    soup = BeautifulSoup(html, "lxml")
    images = set()
    
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src:
            absolute_url = resolve_url(base_url, src)
            if is_valid_url(absolute_url):
                images.add(absolute_url)
    
    return list(images)


def get_content_type(response: httpx.Response) -> Tuple[str, str]:
    """Get content type and charset from response."""
    content_type = response.headers.get("content-type", "text/html")
    
    # Parse content type and charset
    parts = content_type.split(";")
    mime_type = parts[0].strip()
    
    charset = "utf-8"
    for part in parts[1:]:
        if "charset=" in part:
            charset = part.split("=")[1].strip().strip('"')
            break
    
    return mime_type, charset


def is_html_content(mime_type: str) -> bool:
    """Check if MIME type indicates HTML content."""
    return mime_type.startswith("text/html") or mime_type.startswith("application/xhtml")


def is_pdf_content(mime_type: str) -> bool:
    """Check if MIME type indicates PDF content."""
    return mime_type == "application/pdf"


def is_image_content(mime_type: str) -> bool:
    """Check if MIME type indicates image content."""
    return mime_type.startswith("image/")


def hash_url(url: str) -> str:
    """Generate a hash for a URL."""
    return hashlib.md5(url.encode()).hexdigest()


def rate_limit_decorator(calls: int = 10, period: float = 1.0):
    """Decorator to rate limit function calls."""
    min_interval = period / calls
    last_called = {}
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = f"{func.__name__}_{args}_{kwargs}"
            current_time = time.time()
            
            if key in last_called:
                elapsed = current_time - last_called[key]
                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)
            
            last_called[key] = time.time()
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = f"{func.__name__}_{args}_{kwargs}"
            current_time = time.time()
            
            if key in last_called:
                elapsed = current_time - last_called[key]
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)
            
            last_called[key] = time.time()
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def create_progress_bar(description: str = "Processing") -> Progress:
    """Create a rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )


def retry_on_network_error(
    max_attempts: int = 3,
    wait_multiplier: float = 1.0,
    max_wait: float = 10.0
):
    """Decorator to retry on network errors."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=wait_multiplier, max=max_wait),
        retry=retry_if_exception_type((NetworkError, httpx.NetworkError)),
        reraise=True,
    )


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe file system usage."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = f"{name[:250]}.{ext}" if ext else name[:255]
    return filename


def estimate_read_time(text: str, words_per_minute: int = 200) -> float:
    """Estimate reading time for text in minutes."""
    word_count = len(text.split())
    return word_count / words_per_minute


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def parse_robots_txt(robots_txt: str, user_agent: str = "*") -> Dict[str, List[str]]:
    """Parse robots.txt content and extract rules."""
    rules = {"allow": [], "disallow": [], "crawl-delay": None, "sitemap": []}
    current_agent = None
    
    for line in robots_txt.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if ":" not in line:
            continue
        
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        
        if key == "user-agent":
            current_agent = value.lower()
        elif current_agent in [user_agent.lower(), "*"]:
            if key == "allow":
                rules["allow"].append(value)
            elif key == "disallow":
                rules["disallow"].append(value)
            elif key == "crawl-delay":
                try:
                    rules["crawl-delay"] = float(value)
                except ValueError:
                    pass
            elif key == "sitemap":
                rules["sitemap"].append(value)
    
    return rules


def is_url_allowed(url: str, robots_rules: Dict[str, List[str]]) -> bool:
    """Check if URL is allowed according to robots.txt rules."""
    parsed = urlparse(url)
    path = parsed.path
    
    # Check disallow rules first
    for pattern in robots_rules.get("disallow", []):
        if pattern and path.startswith(pattern):
            # Check if there's a more specific allow rule
            for allow_pattern in robots_rules.get("allow", []):
                if allow_pattern and path.startswith(allow_pattern) and len(allow_pattern) > len(pattern):
                    return True
            return False
    
    return True