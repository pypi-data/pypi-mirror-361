# Crawl4 Website - Web Crawler Framework

A powerful and flexible web crawler built with crawl4ai framework that can crawl any website with ease.

## Features

- 🚀 Fast and efficient web crawling using crawl4ai
- 🔧 Configurable crawling parameters
- 📊 Multiple output formats (JSON, CSV, TXT)
- ⚡ Async/await support for high performance
- 🛡️ Built-in rate limiting and error handling
- 🌐 Support for JavaScript-rendered pages
- 📱 Mobile and desktop user agent support

## Installation

```bash
pip install crawl4-website
```

Or install from source:

```bash
git clone https://github.com/yourusername/crawl4_website.git
cd crawl4_website
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Basic crawling
crawl4-website https://example.com

# Crawl with custom output format
crawl4-website https://example.com --format json --output results.json

# Crawl with depth limit
crawl4-website https://example.com --depth 2 --max-pages 100
```

### Python API Usage

```python
from crawl4_website import WebCrawler

# Create crawler instance
crawler = WebCrawler()

# Crawl a website
results = await crawler.crawl("https://example.com")

# Save results
crawler.save_results(results, "output.json", format="json")
```

## Configuration

Create a `.env` file or set environment variables:

```env
USER_AGENT=Mozilla/5.0 (compatible; Crawl4Website/1.0)
DELAY_BETWEEN_REQUESTS=1
MAX_CONCURRENT_REQUESTS=10
```

## Advanced Usage

### Custom Crawling Configuration

```python
from crawl4_website import WebCrawler, CrawlConfig

config = CrawlConfig(
    max_depth=3,
    max_pages=500,
    delay=1.0,
    user_agent="Custom Bot",
    follow_external_links=False
)

crawler = WebCrawler(config)
results = await crawler.crawl("https://example.com")
```

### Filtering and Processing

```python
# Custom content filters
def text_filter(content):
    return len(content) > 100

crawler.add_filter("text", text_filter)

# Custom processors
def extract_emails(content):
    import re
    return re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)

crawler.add_processor("emails", extract_emails)
```

## Output Formats

- **JSON**: Structured data with metadata
- **CSV**: Tabular format for spreadsheet analysis
- **TXT**: Plain text content
- **XML**: Structured markup format

## Requirements

- Python 3.8+
- crawl4ai
- aiohttp
- beautifulsoup4
- lxml

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 Documentation: [Wiki](https://github.com/yourusername/crawl4_website/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/crawl4_website/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/crawl4_website/discussions)