import concurrent.futures
import argparse
import json
import warnings
import search
from fetch import fetch_and_parse

def get_search_results(engine,**kwargs):
    print(f"\n--- Performing {engine} Search for: {kwargs.get('query', 'Unknown Query')}")
    engine_list = ['duckduckgo','google','bing']
    if engine.lower() == 'duckduckgo':    
        return search.duckduckgo_search(**kwargs)
    elif engine.lower() == 'google':
        return search.google_search(**kwargs)
    elif engine.lower() == 'bing':
        return search.bing_search(**kwargs)
    else:
        raise   RuntimeError('Selected search engine not found \n','Available Engines: ',engine_list)

    
def scrape_web_data_concurrent(urls:list, limit:int=10, max_workers:int =5,quiet:bool = False,**kwargs):
    """Scrapes web data concurrently"""
    scraped_data = []
    errors = []#list to store errored urls 
    if not quiet:print(f"\n--- Starting Concurrent Web Scraping (Static Content, {max_workers} workers) ---")

    urls_to_process = urls[:limit] # limit URLs to the specified limit

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(lambda url: fetch_and_parse(url,10,quiet,**kwargs), urls_to_process) 

        for data in results:
            if 'error' not in data:
                scraped_data.append(data)
            else:
                errors.append(data['url'])
                if not quiet:print(f"Skipping {data['url']} due to error: {data['error']}")

    return scraped_data,errors

def search_and_retrieve(query:str,num_urls_from_search:int = 5,max_workers:int =5,engine:str='duckduckgo',quick=False,quiet:bool =False):

    return_data = {}
    urls_from_search = get_search_results(
        engine,
        query = query, 
        num_results=num_urls_from_search,
        quiet=quiet
    )

    if urls_from_search and isinstance(urls_from_search, list) and len(urls_from_search) > 0:
        if not quiet:print('-'*7,'duckduck go search results','-'*7)
        for i, url in enumerate(urls_from_search):
            if not quiet:print(f"{i+1}. {url}")
    else:
        if not quiet:print("No URLs found for the search query or an error occurred.")
        return {'errors':'No URLs found for the search query or an error occurred.'}

    web_data,errors = scrape_web_data_concurrent(urls_from_search, limit=len(urls_from_search), max_workers=max_workers,quiet=quiet,quick=quick) 



    if not quiet: 
        print(f"Total URLs processed: {len(urls_from_search)}")
        print(f"Errors encountered: {len(errors)}")
    
    if web_data :
        return_data = {
            'query':query,
            'urls':urls_from_search,
            'results':web_data,
            'errors':errors,
        }

    return return_data

def save_data(data,filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_args():

    parser = argparse.ArgumentParser(description="A command-line web scraper.")
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
    parser.add_argument(
        '--engine',
        type= str,
        default='duckduckgo',
        help = 'Search engine to use for searching query.'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        default=False,
        help = 'Setting quick as true reduces scraping error but makes scraping slower'
    )
    return parser.parse_args()

if __name__ == "__main__":

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
            engine=args.engine,
            query=args.query,
            num_urls_from_search=args.num_search_results,
            max_workers=5,       
            quiet=False,
            quick=args.quick,
        )

        if web_data and args.path is not None:
            save_data(web_data, args.path) 
            print(f"Successfully saved data to {args.path}")
        else:
            print("\n--- Scraped Data Preview ---")
            print(json.dumps(web_data, indent=4, ensure_ascii=False))
        

