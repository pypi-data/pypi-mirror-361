# RapidCrawl Examples

This directory contains comprehensive examples demonstrating how to use RapidCrawl for various web scraping and crawling tasks.

## Example Files

### 1. `basic_scraping.py`
Learn the fundamentals of web scraping:
- Simple URL scraping
- Multiple output formats (markdown, HTML, text, screenshot)
- Structured data extraction
- Custom headers and options
- Batch scraping multiple URLs

### 2. `web_crawling.py`
Master website crawling techniques:
- Basic recursive crawling
- URL filtering with patterns
- Asynchronous crawling for performance
- Data extraction during crawling
- Progress tracking and monitoring
- Saving crawl results

### 3. `search_and_map.py`
Explore search and URL mapping features:
- Web search with multiple engines
- Scraping search results
- URL mapping and sitemap generation
- Subdomain discovery
- Combining search with mapping

### 4. `data_extraction.py`
Advanced data extraction techniques:
- Schema-based extraction
- E-commerce product data
- Table data extraction
- Batch extraction from multiple pages
- Data validation and transformation

### 5. `advanced_usage.py`
Production-ready patterns and optimizations:
- Authentication methods
- Rate limiting and throttling
- Retry logic with exponential backoff
- Caching strategies (disk and memory)
- Concurrent and async scraping
- Error handling patterns
- Monitoring and logging

## Running the Examples

### Prerequisites

1. Install RapidCrawl:
```bash
pip install rapid-crawl
```

2. For advanced features, install Playwright browsers:
```bash
playwright install chromium
```

### Running Individual Examples

Each example file can be run independently:

```bash
# Basic scraping
python examples/basic_scraping.py

# Web crawling
python examples/web_crawling.py

# Search and mapping
python examples/search_and_map.py

# Data extraction
python examples/data_extraction.py

# Advanced usage
python examples/advanced_usage.py
```

### Running All Examples

To run all examples at once:

```bash
cd examples
for file in *.py; do
    echo "Running $file..."
    python "$file"
done
```

## Example Output

The examples will create various output files:
- `example_content.md` - Scraped content in markdown
- `products.json` / `products.csv` - Extracted product data
- `search_results.json` - Search results with content
- `sitemap.txt` - List of discovered URLs
- `crawl_results/` - Directory with crawl data
- `scraping.log` - Detailed logging output
- `cache/` - Cached scraping results

## Customization

Feel free to modify these examples for your specific use cases:

1. **Change URLs**: Replace example URLs with your target websites
2. **Adjust schemas**: Modify extraction schemas for your data structure
3. **Configure options**: Tweak timeouts, formats, and other parameters
4. **Add features**: Extend examples with additional RapidCrawl features

## Important Notes

- **Rate Limiting**: Always be respectful of websites. Use rate limiting to avoid overwhelming servers.
- **robots.txt**: Check and respect robots.txt files.
- **Terms of Service**: Ensure you comply with website terms of service.
- **Error Handling**: Production code should include comprehensive error handling.
- **API Keys**: Some features require API keys. Set `RAPIDCRAWL_API_KEY` environment variable.

## Troubleshooting

If you encounter issues:

1. Check the [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)
2. Ensure all dependencies are installed
3. Verify network connectivity
4. Check for API key if using cloud features
5. Review error messages and logs

## More Resources

- [API Documentation](../docs/API.md)
- [Advanced Usage Guide](../docs/ADVANCED.md)
- [Full Examples Documentation](../docs/EXAMPLES.md)
- [GitHub Repository](https://github.com/aoneahsan/rapid-crawl)

## Contributing

Have an interesting example? Feel free to contribute! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.