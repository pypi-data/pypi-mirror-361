# RapidCrawl Troubleshooting Guide

This guide helps you resolve common issues when using RapidCrawl.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Authentication Problems](#authentication-problems)
- [Scraping Errors](#scraping-errors)
- [Crawling Issues](#crawling-issues)
- [Performance Problems](#performance-problems)
- [Common Error Messages](#common-error-messages)
- [Platform-Specific Issues](#platform-specific-issues)
- [Debugging Tips](#debugging-tips)
- [FAQ](#faq)

---

## Installation Issues

### Problem: `pip install rapid-crawl` fails

**Symptoms:**
- Installation errors
- Dependency conflicts
- Permission denied errors

**Solutions:**

1. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install rapid-crawl
   ```

3. **Install with user flag:**
   ```bash
   pip install --user rapid-crawl
   ```

4. **For M1/M2 Macs:**
   ```bash
   # Install Rosetta if needed
   softwareupdate --install-rosetta
   
   # Use arch flag
   arch -x86_64 pip install rapid-crawl
   ```

### Problem: Playwright browsers not installing

**Symptoms:**
- `playwright install` fails
- Browser launch errors
- "Executable doesn't exist" errors

**Solutions:**

1. **Install specific browser:**
   ```bash
   playwright install chromium
   # or
   playwright install-deps chromium
   ```

2. **Install system dependencies (Linux):**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
   
   # CentOS/RHEL
   sudo yum install -y alsa-lib atk cups-libs libXcomposite libXdamage libXrandr libgbm libxkbcommon pango
   ```

3. **Set browser path manually:**
   ```python
   import os
   os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/path/to/browsers"
   ```

### Problem: Import errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'rapidcrawl'`
- Import errors for dependencies

**Solutions:**

1. **Verify installation:**
   ```bash
   pip show rapid-crawl
   pip list | grep rapid-crawl
   ```

2. **Reinstall with all dependencies:**
   ```bash
   pip uninstall rapid-crawl -y
   pip install rapid-crawl[dev]
   ```

3. **Check Python path:**
   ```python
   import sys
   print(sys.path)
   # Ensure your site-packages is in the path
   ```

---

## Authentication Problems

### Problem: "Invalid API key" error

**Symptoms:**
- `AuthenticationError: Invalid API key`
- 401 Unauthorized responses

**Solutions:**

1. **Check environment variable:**
   ```python
   import os
   print(os.getenv("RAPIDCRAWL_API_KEY"))  # Should show your key
   ```

2. **Set API key correctly:**
   ```python
   # Method 1: Environment variable
   os.environ["RAPIDCRAWL_API_KEY"] = "your-key"
   
   # Method 2: Direct initialization
   app = RapidCrawlApp(api_key="your-key")
   
   # Method 3: .env file
   # Create .env file with:
   # RAPIDCRAWL_API_KEY=your-key
   ```

3. **Verify .env file loading:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Explicitly load .env
   ```

### Problem: Self-hosted mode not working

**Symptoms:**
- Warning about missing API key
- Self-hosted features not available

**Solutions:**

1. **Explicitly set self-hosted mode:**
   ```python
   app = RapidCrawlApp(
       api_key="self-hosted",
       base_url="http://localhost:8000"  # Your local instance
   )
   ```

2. **Disable SSL for local development:**
   ```python
   app = RapidCrawlApp(verify_ssl=False)
   ```

---

## Scraping Errors

### Problem: "Failed to scrape URL" errors

**Symptoms:**
- `ScrapingError: Failed to scrape URL`
- Empty results
- Timeout errors

**Solutions:**

1. **Increase timeout:**
   ```python
   result = app.scrape_url(
       "https://slow-site.com",
       timeout=120000  # 2 minutes
   )
   ```

2. **Use wait_for selector:**
   ```python
   result = app.scrape_url(
       "https://dynamic-site.com",
       wait_for=".content-loaded",  # Wait for specific element
       timeout=60000
   )
   ```

3. **Handle dynamic content:**
   ```python
   result = app.scrape_url(
       "https://spa-site.com",
       actions=[
           {"type": "wait", "value": 3000},  # Wait 3 seconds
           {"type": "click", "selector": ".load-more"}
       ]
   )
   ```

### Problem: Blocked by website

**Symptoms:**
- 403 Forbidden errors
- CAPTCHA challenges
- "Access denied" messages

**Solutions:**

1. **Use custom headers:**
   ```python
   result = app.scrape_url(
       "https://protected-site.com",
       headers={
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate",
           "Connection": "keep-alive",
       }
   )
   ```

2. **Add delays between requests:**
   ```python
   import time
   
   for url in urls:
       result = app.scrape_url(url)
       time.sleep(2)  # 2 second delay
   ```

3. **Use mobile mode:**
   ```python
   result = app.scrape_url(url, mobile=True)
   ```

### Problem: Content not extracted properly

**Symptoms:**
- Missing data in results
- Incorrect structured data
- Empty markdown content

**Solutions:**

1. **Check selectors:**
   ```python
   # Debug selectors
   result = app.scrape_url(url, formats=["html"])
   soup = BeautifulSoup(result.content["html"], "html.parser")
   
   # Test your selector
   element = soup.select_one(".your-selector")
   print(element)  # Should not be None
   ```

2. **Adjust extraction schema:**
   ```python
   schema = [
       {
           "name": "price",
           "selector": ".price",
           "type": "number",
           "regex": r"[\d.]+",  # Extract numbers only
           "default": 0  # Provide default
       }
   ]
   ```

3. **Remove interfering tags:**
   ```python
   result = app.scrape_url(
       url,
       remove_tags=["script", "style", "nav", "footer"],
       only_main_content=True
   )
   ```

---

## Crawling Issues

### Problem: Crawl gets stuck or hangs

**Symptoms:**
- Crawl doesn't complete
- No progress updates
- Process hangs

**Solutions:**

1. **Set reasonable limits:**
   ```python
   result = app.crawl_url(
       "https://large-site.com",
       max_pages=100,  # Limit pages
       max_depth=3,    # Limit depth
       timeout=30000   # Per-page timeout
   )
   ```

2. **Use async crawling:**
   ```python
   import asyncio
   
   async def crawl():
       result = await app.crawl_url_async(
           "https://site.com",
           max_pages=1000
       )
       return result
   
   result = asyncio.run(crawl())
   ```

3. **Add exclude patterns:**
   ```python
   result = app.crawl_url(
       url,
       exclude_patterns=[
           r".*\.(jpg|png|gif|pdf|zip)$",  # Skip files
           r".*/page/\d{4,}",  # Skip deep pagination
           r".*/comment-page-.*"  # Skip comment pages
       ]
   )
   ```

### Problem: Missing pages in crawl

**Symptoms:**
- Expected pages not crawled
- Incomplete results
- Pages skipped

**Solutions:**

1. **Check robots.txt:**
   ```python
   # Crawl ignores robots.txt by default
   # Check if pages are disallowed
   import httpx
   resp = httpx.get("https://site.com/robots.txt")
   print(resp.text)
   ```

2. **Adjust patterns:**
   ```python
   result = app.crawl_url(
       url,
       include_patterns=[
           r"/products/.*",
           r"/category/.*"
       ],
       allow_subdomains=True  # Include subdomains
   )
   ```

3. **Check depth limits:**
   ```python
   # Increase depth if pages are too deep
   result = app.crawl_url(url, max_depth=5)
   ```

---

## Performance Problems

### Problem: Scraping is too slow

**Symptoms:**
- Long execution times
- Timeouts
- Poor performance

**Solutions:**

1. **Use concurrent scraping:**
   ```python
   import asyncio
   from concurrent.futures import ThreadPoolExecutor
   
   def scrape_batch(urls, max_workers=5):
       with ThreadPoolExecutor(max_workers=max_workers) as executor:
           futures = [executor.submit(app.scrape_url, url) for url in urls]
           results = [f.result() for f in futures]
       return results
   ```

2. **Optimize formats:**
   ```python
   # Only request needed formats
   result = app.scrape_url(
       url,
       formats=["markdown"],  # Don't request screenshot if not needed
       only_main_content=True  # Skip navigation, ads, etc.
   )
   ```

3. **Implement caching:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_scrape(url):
       return app.scrape_url(url)
   ```

### Problem: High memory usage

**Symptoms:**
- Memory errors
- Process killed
- System slowdown

**Solutions:**

1. **Process in batches:**
   ```python
   def process_large_crawl(url, batch_size=50):
       for i in range(0, 1000, batch_size):
           result = app.crawl_url(
               url,
               max_pages=batch_size,
               # Process and save results
           )
           # Clear memory
           del result
   ```

2. **Limit concurrent operations:**
   ```python
   result = app.crawl_url(
       url,
       limit_rate=2  # Max 2 requests per second
   )
   ```

---

## Common Error Messages

### `TimeoutError: Operation timed out`

**Cause:** Page took too long to load

**Fix:**
```python
# Increase timeout
result = app.scrape_url(url, timeout=120000)  # 2 minutes

# Or use wait_for with shorter timeout
result = app.scrape_url(
    url,
    wait_for=".content",
    timeout=30000
)
```

### `NetworkError: Connection refused`

**Cause:** Cannot connect to server

**Fix:**
```python
# Check URL is correct
print(f"Trying to connect to: {url}")

# Try with different protocol
if url.startswith("http://"):
    url = url.replace("http://", "https://")

# Add retry logic
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def scrape_with_retry(url):
    return app.scrape_url(url)
```

### `ValidationError: Invalid URL`

**Cause:** Malformed URL

**Fix:**
```python
from urllib.parse import urlparse

# Validate URL
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Add protocol if missing
if not url.startswith(('http://', 'https://')):
    url = 'https://' + url
```

---

## Platform-Specific Issues

### Windows Issues

**Problem:** Path too long errors

**Solution:**
```python
# Enable long paths in Windows
# Run as administrator:
# reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1

# Or use shorter paths
import tempfile
temp_dir = tempfile.mkdtemp(dir="C:\\temp")
```

**Problem:** SSL certificate errors

**Solution:**
```python
# Disable SSL verification (development only!)
app = RapidCrawlApp(verify_ssl=False)

# Or update certificates
# Download: https://curl.se/ca/cacert.pem
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

### macOS Issues

**Problem:** SSL: CERTIFICATE_VERIFY_FAILED

**Solution:**
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or use homebrew Python
brew install ca-certificates
```

### Linux Issues

**Problem:** Missing system dependencies

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-dev libxml2-dev libxslt1-dev

# CentOS/RHEL
sudo yum install python3-devel libxml2-devel libxslt-devel
```

---

## Debugging Tips

### Enable debug mode

```python
# Initialize with debug mode
app = RapidCrawlApp(debug=True)

# This will show:
# - Request details
# - Progress information
# - Error traces
```

### Log all operations

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='rapidcrawl_debug.log'
)

# Use logging in your code
logger = logging.getLogger(__name__)

try:
    result = app.scrape_url(url)
    logger.info(f"Successfully scraped {url}")
except Exception as e:
    logger.exception(f"Failed to scrape {url}")
```

### Test with simple URLs first

```python
# Test basic functionality
test_urls = [
    "https://httpbin.org/html",  # Simple HTML
    "https://example.com",        # Basic site
    "https://httpbin.org/delay/2" # Test timeouts
]

for url in test_urls:
    try:
        result = app.scrape_url(url)
        print(f"✓ {url} - Success")
    except Exception as e:
        print(f"✗ {url} - Failed: {e}")
```

### Inspect raw responses

```python
# Get raw HTML to debug parsing
result = app.scrape_url(url, formats=["rawHtml"])
with open("debug.html", "w", encoding="utf-8") as f:
    f.write(result.content["rawHtml"])

# Open debug.html in browser to inspect
```

---

## FAQ

### Q: How do I handle rate limiting?

**A:** Implement delays and respect rate limits:

```python
import time
from rapidcrawl.exceptions import RateLimitError

def scrape_with_rate_limit(urls, delay=1.0):
    results = []
    
    for url in urls:
        try:
            result = app.scrape_url(url)
            results.append(result)
        except RateLimitError as e:
            wait_time = e.retry_after or 60
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            # Retry
            result = app.scrape_url(url)
            results.append(result)
        
        time.sleep(delay)  # Regular delay
    
    return results
```

### Q: Can I use proxies?

**A:** Proxy support is planned for future versions. Current workaround:

```python
# Set proxy via environment variable
import os
os.environ["HTTP_PROXY"] = "http://proxy.example.com:8080"
os.environ["HTTPS_PROXY"] = "http://proxy.example.com:8080"

# Then initialize client
app = RapidCrawlApp()
```

### Q: How do I scrape JavaScript-heavy sites?

**A:** Use wait strategies and actions:

```python
result = app.scrape_url(
    "https://spa-app.com",
    wait_for=".app-loaded",  # Wait for app to initialize
    actions=[
        {"type": "wait", "value": 3000},  # Additional wait
        {"type": "scroll", "value": 1000}, # Trigger lazy loading
        {"type": "click", "selector": ".load-all"}  # Load all content
    ],
    timeout=60000  # Longer timeout for JS apps
)
```

### Q: Memory issues with large crawls?

**A:** Use streaming and batch processing:

```python
def crawl_large_site(url, output_file):
    with open(output_file, "w") as f:
        # Process in chunks
        for page_num in range(0, 10000, 100):
            result = app.crawl_url(
                url,
                max_pages=100,
                include_patterns=[f"/page/{page_num}-{page_num+99}"]
            )
            
            # Write results immediately
            for page in result.pages:
                f.write(f"{page.url}\t{page.title}\n")
            
            # Clear memory
            del result
```

### Q: How to handle login-protected content?

**A:** Use session cookies:

```python
# First, get login cookies (example with requests)
import requests

session = requests.Session()
session.post("https://site.com/login", data={
    "username": "user",
    "password": "pass"
})

# Extract cookies
cookies = {c.name: c.value for c in session.cookies}

# Use cookies in RapidCrawl
headers = {
    "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
}

result = app.scrape_url(
    "https://site.com/protected",
    headers=headers
)
```

---

If you're still experiencing issues after trying these solutions, please:

1. Check the [GitHub Issues](https://github.com/aoneahsan/rapid-crawl/issues) for similar problems
2. Create a new issue with:
   - Detailed error message
   - Minimal code to reproduce
   - System information (OS, Python version, RapidCrawl version)
   - What you've already tried

For urgent support, contact: aoneahsan@gmail.com