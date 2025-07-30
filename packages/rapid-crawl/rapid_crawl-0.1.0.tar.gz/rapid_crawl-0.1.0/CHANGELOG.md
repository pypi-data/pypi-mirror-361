# Changelog

All notable changes to RapidCrawl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of RapidCrawl
- Core features:
  - **Scrape**: Web scraping with multiple output formats (markdown, HTML, text, screenshot)
  - **Crawl**: Recursive website crawling with depth control and filtering
  - **Map**: Fast URL discovery with sitemap support
  - **Search**: Web search across multiple engines with optional scraping
- Dynamic content handling with Playwright
- PDF and image processing capabilities
- Structured data extraction with schemas
- Command-line interface with rich output
- Async support for high-performance operations
- Comprehensive error handling and retry logic
- Interactive setup wizard
- NPX setup script for easy installation

### Features in Detail

#### Scraping
- Multiple output formats: markdown, HTML, raw HTML, text, screenshot, links
- Dynamic content handling with Playwright
- PDF text extraction
- Image metadata extraction
- Custom data extraction with CSS selectors
- Page interactions (click, wait, scroll)
- Mobile viewport support
- Location and language targeting

#### Crawling
- Configurable depth and page limits
- URL pattern filtering (include/exclude)
- Subdomain support
- robots.txt compliance
- Asynchronous crawling for performance
- Webhook notifications for progress updates
- Rate limiting support

#### Mapping
- Sitemap.xml parsing
- Fast BFS crawling
- Search term filtering
- Configurable result limits
- Subdomain inclusion option

#### Searching
- Multiple search engines: Google, Bing, DuckDuckGo
- Optional result scraping
- Date range filtering
- Location-based search
- Configurable result count

### Developer Experience
- Type hints throughout the codebase
- Comprehensive documentation
- Unit tests with mocking
- Pre-commit hooks
- Code formatting with Black
- Linting with Ruff
- Type checking with mypy

## [0.1.0] - 2024-01-XX (Upcoming)

### Added
- First stable release
- PyPI package publication
- npm package for setup script
- Complete documentation
- Example scripts
- GitHub repository setup

### Security
- Input validation for all user inputs
- Safe URL handling
- No storage of sensitive data
- Configurable SSL verification

### Known Issues
- Search engines may rate limit or block requests
- Some websites may block automated access
- Playwright installation required for dynamic content

## Version History Format

Each version entry should include:

### Added
New features or capabilities

### Changed
Changes to existing functionality

### Deprecated
Features that will be removed in future versions

### Removed
Features that have been removed

### Fixed
Bug fixes

### Security
Security-related changes

---

## Roadmap

### Version 0.2.0 (Planned)
- [ ] Proxy support
- [ ] Advanced rate limiting strategies
- [ ] Cloud storage integration
- [ ] Export to various formats (CSV, JSON, Excel)
- [ ] Browser extension

### Version 0.3.0 (Planned)
- [ ] API server mode
- [ ] Distributed crawling
- [ ] Machine learning content classification
- [ ] Advanced extraction templates
- [ ] Integration with popular AI/LLM services

### Future Considerations
- Node.js SDK
- Go SDK
- Rust SDK
- SaaS platform
- Visual scraping interface

## Upgrade Guide

### From 0.0.x to 0.1.0
- No breaking changes
- New features are backward compatible
- Recommended to update for bug fixes and performance improvements

---

For more details on each release, see the [GitHub releases](https://github.com/aoneahsan/rapid-crawl/releases) page.