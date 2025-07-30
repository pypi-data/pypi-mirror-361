# Contributing to RapidCrawl

First off, thank you for considering contributing to RapidCrawl! It's people like you that make RapidCrawl such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
  - [Python Style Guide](#python-style-guide)
  - [Commit Messages](#commit-messages)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Push to your fork and submit a pull request

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize client with '...'
2. Call method '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened. Include error messages.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - Python version: [e.g. 3.8.10]
 - RapidCrawl version: [e.g. 0.1.0]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Explain why this enhancement would be useful
- List any alternative solutions you've considered

### Your First Code Contribution

Unsure where to begin? You can start by looking through these issues:

- Issues labeled `good first issue` - should only require a few lines of code
- Issues labeled `help wanted` - more involved but still accessible

### Pull Requests

1. Follow the [style guidelines](#style-guidelines)
2. Include tests for any new functionality
3. Update documentation as needed
4. Ensure all tests pass
5. Write a clear PR description

**PR Checklist:**

- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass locally
- [ ] Any dependent changes have been merged

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aoneahsan/rapid-crawl.git
   cd rapid-crawl
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Style Guidelines

### Python Style Guide

We use the following tools to maintain code quality:

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **mypy** for type checking

Before committing:

```bash
# Format code
black src/rapidcrawl tests

# Run linter
ruff check src/rapidcrawl tests

# Type checking
mypy src/rapidcrawl
```

**Key Style Points:**

1. Use type hints for all function signatures
2. Write docstrings for all public functions/classes (Google style)
3. Keep functions focused and under 50 lines when possible
4. Use descriptive variable names
5. Follow PEP 8 with Black's modifications

**Example:**

```python
from typing import Optional, List, Dict, Any

def scrape_url(
    self,
    url: str,
    formats: Optional[List[str]] = None,
    timeout: int = 30000
) -> Dict[str, Any]:
    """
    Scrape a URL and return its content.
    
    Args:
        url: The URL to scrape.
        formats: List of output formats (markdown, html, etc.).
        timeout: Request timeout in milliseconds.
        
    Returns:
        Dictionary containing scraped content and metadata.
        
    Raises:
        ScrapingError: If the URL cannot be scraped.
        ValidationError: If the URL is invalid.
    """
    # Implementation here
    pass
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: add PDF extraction support to scraper
fix: handle timeout errors in async crawler
docs: update API reference for search feature
test: add unit tests for URL validation
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rapidcrawl --cov-report=html

# Run specific test file
pytest tests/test_scrape.py

# Run specific test
pytest tests/test_scrape.py::TestScraper::test_basic_scraping
```

### Writing Tests

1. Place tests in the `tests/` directory
2. Name test files with `test_` prefix
3. Use descriptive test names that explain what is being tested
4. Include both positive and negative test cases
5. Mock external dependencies

**Example test:**

```python
import pytest
from unittest.mock import Mock, patch

from rapidcrawl import RapidCrawlApp
from rapidcrawl.exceptions import ScrapingError


class TestScraper:
    def test_scrape_url_success(self):
        """Test successful URL scraping."""
        app = RapidCrawlApp()
        
        with patch.object(app.scraper, '_make_request') as mock_request:
            mock_request.return_value.text = "<h1>Test</h1>"
            
            result = app.scrape_url("https://example.com")
            
            assert result.success is True
            assert "Test" in result.content["markdown"]
    
    def test_scrape_url_invalid_url(self):
        """Test scraping with invalid URL."""
        app = RapidCrawlApp()
        
        with pytest.raises(ValidationError):
            app.scrape_url("not-a-url")
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain what the function does,
    any important details, etc.
    
    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.
        
    Returns:
        Description of return value.
        
    Raises:
        ExceptionType: Description of when this exception is raised.
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Updating Documentation

When making changes:

1. Update docstrings for any modified functions/classes
2. Update README.md if adding new features
3. Update API.md for API changes
4. Add examples to EXAMPLES.md for new functionality
5. Update CHANGELOG.md

## Community

### Getting Help

- Check the [documentation](https://github.com/aoneahsan/rapid-crawl#readme)
- Look through [existing issues](https://github.com/aoneahsan/rapid-crawl/issues)
- Join our [discussions](https://github.com/aoneahsan/rapid-crawl/discussions)

### Staying Updated

- Watch the repository for updates
- Follow [@aoneahsan](https://twitter.com/aoneahsan) for announcements
- Subscribe to the [changelog](CHANGELOG.md)

## Recognition

Contributors will be recognized in:

- The project README
- Release notes
- Our contributor hall of fame

Thank you for contributing to RapidCrawl! 🚀