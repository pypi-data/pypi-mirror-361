# Brave DeepSeek Book Review

Intelligent book reviews and search using Brave Search API + DeepSeek LLM for comprehensive book information and analysis.

## Installation

```bash
pip install brave-deepseek-book-review
```

## Quick Start

### Python Library Usage

```python
from brave_deepseek_book_search import BookSearch

# Initialize with API keys
search = BookSearch(
    deepseek_api_key="your_deepseek_api_key",
    brave_api_key="your_brave_api_key"
)

# Generate book review
result = search.find_book("Dune Frank Herbert")

if result.success:
    print(f"Title: {result.title}")
    print(f"Author: {result.author}")
    print(f"Review: {result.description}")
else:
    print(f"Error: {result.error}")
```

### Command Line Usage

```bash
# Set environment variables
export DEEPSEEK_API_KEY="your_key"
export BRAVE_API_KEY="your_key" 

# Generate book review
book-review "Dune Frank Herbert"

# JSON output
book-review "1984 George Orwell" --json

# Debug mode
book-review "The Great Gatsby" --debug
```

## Configuration

### SearchConfig Options

```python
from brave_deepseek_book_search import BookSearch, SearchConfig

config = SearchConfig(
    max_results=10,                           # Max search results to analyze
    countries=["usa", "uk", "france"],        # Countries to search
    debug_mode=True,                          # Enable debug output
    model="deepseek-chat"                     # DeepSeek model to use
)

search = BookSearch(
    deepseek_api_key="...",
    brave_api_key="...", 
    config=config
)
```

## API Keys

You need API keys from:

1. **DeepSeek**: https://platform.deepseek.com/
2. **Brave Search**: https://api.search.brave.com/

## Features

- 🌍 Multi-country search (15+ countries supported)
- 🤖 AI-powered book analysis and review generation
- 🔍 Intelligent search result synthesis
- 📚 Comprehensive book information extraction
- 💰 Cost-optimized API usage
- 🖥️ Both library and CLI interfaces
- 📖 Detailed book reviews and summaries

## Countries Supported

- 🇺🇸 USA
- 🇬🇧 UK  
- 🇫🇷 France
- 🇩🇪 Germany
- 🇷🇺 Russia
- 🇪🇸 Spain
- 🇮🇹 Italy
- 🇯🇵 Japan
- 🇨🇳 China
- 🇨🇦 Canada
- 🇦🇺 Australia
- 🇧🇷 Brazil
- 🇵🇹 Portugal
- 🇦🇷 Argentina
- 🇲🇽 Mexico

## License

MIT License