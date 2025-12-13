
from ddgs import DDGS
import requests
import concurrent.futures
from bs4 import BeautifulSoup
import argparse
import json
import warnings

def get_urls_from_duckduckgo_search(query:str, num_results:int =10, safesearch:str ='moderate', timelimit:int =None,quiet:bool = False):
    """
    Performs a DuckDuckGo search for a given query and returns a list of URLs.
    Args:
        query (str): The search query string.
        num_results (int): The maximum number of URLs to retrieve.
                        DuckDuckGo might return fewer than requested.
        safesearch (str): 'on', 'moderate', or 'off'. Defaults to 'moderate'.
        timelimit (str): 'd' (day), 'w' (week), 'm' (month), 'y' (year) or None.

    Returns:
        list: A list of URLs (strings) from the search results.
    """
    found_urls = []
    if not quiet:print(f"\n--- Performing DuckDuckGo Search for: '{query}' ---")
    try:
        # DDGS().text returns a generator, so we iterate through it
        
        results_generator = DDGS().text(
            query=query, 
            safesearch=safesearch, 
            timelimit=timelimit,
            max_results=num_results, # Request up to num_results
            
        )

        for i, result in enumerate(results_generator):
            if 'href' in result and result['href']:
                found_urls.append(result['href'])
                if len(found_urls) >= num_results:
                    break 

    except Exception as e:
        if not quiet:
            print(f"  An error occurred during DuckDuckGo search for '{query}': {e}")
            print("  Consider adding a small 'time.sleep()' inside the loop if this persists.")
    
    if not quiet:print(f"  Search complete. Found {len(found_urls)} URLs for '{query}'.")
    return found_urls


def fetch_and_parse(url:str,timeout:int = 10,quiet:bool =False):
    """Fetches a single URL and parses its content."""
    try:
        response = requests.get(url, 
                                timeout=timeout,
                                headers={"User-Agent": "Mozilla/5.0 (compatible; SimpleScraper/1.0)"}
                                )
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'N/A'
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]

        return {
            'url': url,
            'title': title,
            'paragraphs': paragraphs,
            'links': links
        }
    
    except requests.exceptions.Timeout:
        if not quiet: print(f" [Scrape Error] Timeout error for {url}")
        return {'url': url, 'error': 'Timeout'}
    
    except requests.exceptions.RequestException as e:
        if not quiet: print(f"  [Scrape Error] Request failed for {url}: {e}")
        return {'url': url, 'error': f'Request failed: {e}'}
    
    except Exception as e:
        if not quiet: print(f"  An unexpected error occurred for {url}: {e}")
        return {'url': url, 'error': f'Unexpected error: {e}'}
        

    
def scrape_web_data_concurrent(urls:list, limit:int=10, max_workers:int =5,quiet:bool = False):
    """Scrapes web data concurrently"""
    scraped_data = []
    errors = []#list to store errored urls 
    if not quiet:print(f"\n--- Starting Concurrent Web Scraping (Static Content, {max_workers} workers) ---")

    urls_to_process = urls[:limit] # Limit URLs to the specified limit

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(lambda url: fetch_and_parse(url,10,quiet), urls_to_process) 

        for data in results:
            if 'error' not in data:
                scraped_data.append(data)
            else:
                errors.append(data['url'])
                if not quiet:print(f"Skipping {data['url']} due to error: {data['error']}")

    return scraped_data,errors

def search_and_retrieve(query:str,num_urls_from_search:int = 5,max_workers:int =5,quiet:bool =False):
    error = [] #list to store errored urls 
    return_data = {}
    # Call the new DuckDuckGo search function
    urls_from_ddg_search = get_urls_from_duckduckgo_search(
        query, 
        num_results=num_urls_from_search,
        quiet=quiet
    )

    if urls_from_ddg_search and len(urls_from_ddg_search) > 0:
        if not quiet:print('-'*7,'duckduck go search results','-'*7)
        for i, url in enumerate(urls_from_ddg_search):
            if not quiet:print(f"{i+1}. {url}")
    else:
        if not quiet:print("No URLs found for the search query or an error occurred.")
        return {'errors':'No URLs found for the search query or an error occurred.'}

    web_data,errors = scrape_web_data_concurrent(urls_from_ddg_search, limit=len(urls_from_ddg_search), max_workers=max_workers,quiet=quiet) 
    error.extend(errors)


    if not quiet: 
        print(f"Total URLs processed: {len(urls_from_ddg_search)}")
        print(f"Errors encountered: {len(error)}")
    
    if web_data :
        return_data = {
            'query':query,
            'urls':urls_from_ddg_search,
            'results':web_data,
            'errors':error,
        }


    return return_data

def save_data(data,filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_args():

    parser = argparse.ArgumentParser(description="A  command-line web scraper.")
    parser.add_argument(
        'query',
        type=str,
        help='the query to search and scrape'
    )
    parser.add_argument(
        '--path',
        type= str,
        default = None,
        help='File path to store JSON output.',
    )
    parser.add_argument(
        '--num_search_results',
        type = int,
        default=5,
        help = 'Number of URLs to scrape from search results.'
    )

    return parser.parse_args()

if __name__ == "__main__":
    try:
        args = add_args()
        print(f"Starting web scraping for query: '{args.query}'")
        if args.path is None:
            warnings.warn(
                    "JSON output path not specified. Scraped data will NOT be saved. "
                    "To save results, provide: --path <file.json>",
                UserWarning, 
                stacklevel=2        
                    )
        else:
            print(f"Results will be saved to: {args.path}")        
        web_data = search_and_retrieve(
            query=args.query,
            num_urls_from_search=args.num_search_results,
            max_workers=5,       
            quiet=False
        )

        if web_data and args.path is not None:
            save_data(web_data, args.path) # save it even if one url has errors as we scrape many urls 
        

    except Exception as e:
        print(f"A critical error occurred: {e}")