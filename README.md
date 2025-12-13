# Concurrent Web Scraper & Searcher

A Python command-line tool that searches DuckDuckGo and concurrently scrapes the resulting webpages for text content.

## Features
- **Search:** Uses DuckDuckGo to find relevant URLs.
- **Concurrency:** Uses `concurrent.futures` to scrape multiple pages simultaneously for faster execution.
- **Extraction:** Parses HTML to extract titles, paragraphs, and links.
- **Output:** Saves results to a structured JSON file.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sam-ezz/parallel-web-scraper.git
   ```
2.  Navigate into the project directory:
    ```bash
    cd parallel-web-scraper
    ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line:

```bash
python main.py "artificial intelligence" --num_search_results 10 --path results.json
```

### Arguments
- `query`: The search term (e.g., "What is web scraping").
- `--num_search_results`: (Optional) Number of URLs to fetch (default: 5).
- `--path`: (Optional) File path to save the JSON output.

## Demo

Here is the tool in action searching for "what is scraping":

![Terminal output showing a search for web scraping](assets/terminal_demo.png)
 
## Disclaimer
This tool is for educational purposes only. Please respect the `robots.txt` of websites and do not use this tool for spamming or overloading servers.
```