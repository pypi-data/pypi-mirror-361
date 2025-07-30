# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of RapidCrawl seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT:

- Open a public GitHub issue
- Post about it on social media
- Exploit the vulnerability

### Please DO:

**Email us directly at**: aoneahsan@gmail.com

Please include the following information:

1. **Type of issue** (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
2. **Full paths of source file(s)** related to the manifestation of the issue
3. **Location** of the affected source code (tag/branch/commit or direct URL)
4. **Step-by-step instructions** to reproduce the issue
5. **Proof-of-concept or exploit code** (if possible)
6. **Impact** of the issue, including how an attacker might exploit it

### What to expect:

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
2. **Communication**: We will keep you informed about the progress of addressing the vulnerability
3. **Fix Timeline**: We aim to fix critical vulnerabilities within 7 days and other vulnerabilities within 30 days
4. **Disclosure**: We will coordinate with you on the disclosure timeline

## Security Best Practices

When using RapidCrawl, please follow these security best practices:

### 1. API Key Management

- **Never** commit API keys to version control
- Store API keys in environment variables or secure vaults
- Rotate API keys regularly
- Use different API keys for different environments

```python
# Good - Using environment variables
import os
from rapidcrawl import RapidCrawlApp

app = RapidCrawlApp(api_key=os.getenv("RAPIDCRAWL_API_KEY"))

# Bad - Hardcoded API key
app = RapidCrawlApp(api_key="sk-1234567890")  # DON'T DO THIS!
```

### 2. Input Validation

RapidCrawl validates URLs and other inputs, but always validate data from scraped content:

```python
# Validate scraped data before using it
result = app.scrape_url("https://example.com")
if result.success and result.structured_data:
    # Validate data types and ranges
    price = result.structured_data.get("price")
    if isinstance(price, (int, float)) and 0 <= price <= 1000000:
        # Safe to use
        process_price(price)
```

### 3. Rate Limiting

Respect website rate limits to avoid being blocked:

```python
# Use appropriate delays between requests
import time

for url in urls:
    result = app.scrape_url(url)
    time.sleep(1)  # Add delay between requests
```

### 4. Data Storage

When storing scraped data:

- Encrypt sensitive data at rest
- Don't store passwords or authentication tokens
- Follow data protection regulations (GDPR, CCPA, etc.)
- Implement proper access controls

### 5. Network Security

- Use HTTPS URLs whenever possible
- Be cautious with self-signed certificates
- Consider using proxies for additional anonymity
- Monitor for suspicious network activity

```python
# Only disable SSL verification for trusted internal services
app = RapidCrawlApp(verify_ssl=False)  # Use with caution!
```

### 6. Content Security

- Be aware that scraped content may contain malicious scripts
- Sanitize HTML content before displaying it
- Don't execute JavaScript from scraped content
- Validate file types before processing

## Known Security Considerations

### Web Scraping Ethics

- Always check and respect robots.txt
- Don't overwhelm servers with requests
- Respect website terms of service
- Consider the legal implications in your jurisdiction

### Data Privacy

- Be mindful of personal data in scraped content
- Implement data minimization practices
- Provide clear privacy policies if collecting user data
- Allow users to request data deletion

### Third-party Dependencies

We regularly update our dependencies to patch known vulnerabilities. You can check for outdated packages:

```bash
pip list --outdated
```

## Security Features

RapidCrawl includes several security features:

1. **Input Validation**: All URLs and parameters are validated
2. **Secure Defaults**: SSL verification enabled by default
3. **No Eval**: No use of eval() or exec() on user input
4. **Limited Scope**: No file system access beyond specified operations
5. **Dependency Scanning**: Regular security audits of dependencies

## Vulnerability Disclosure Policy

We follow a coordinated disclosure policy:

1. Security issues are fixed in a private repository
2. A new version is released with the fix
3. The vulnerability is publicly disclosed after users have had time to update
4. Credit is given to the reporter (unless they prefer to remain anonymous)

## Contact

For any security-related questions that don't involve reporting a vulnerability, please reach out:

- Email: aoneahsan@gmail.com
- GitHub Security Advisories: [Enable private vulnerability reporting](https://github.com/aoneahsan/rapid-crawl/security)

## Acknowledgments

We would like to thank the following individuals for responsibly disclosing security issues:

- *Your name could be here!*

---

Remember: Security is everyone's responsibility. If you see something, say something!