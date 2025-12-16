from ddgs import DDGS

def duckduckgo_search(query:str, num_results:int =10, safesearch:str ='moderate', timelimit:int =None,quiet:bool = False):
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
    try:
        # DDGS().text returns a generator, so we iterate through it
        
        results_generator = DDGS().text(
            query=query, 
            safesearch=safesearch, 
            timelimit=timelimit,
            max_results=num_results, 
        )

        for i, result in enumerate(results_generator):
            if 'href' in result and result['href']:
                found_urls.append(result['href'])
                if len(found_urls) >= num_results:
                    break 

    except Exception as e:
        if not quiet:
            print(f"  An error occurred during DuckDuckGo search for '{query}': {e}")
    
    if not quiet:print(f"  Search complete. Found {len(found_urls)} URLs for '{query}'.")
    return found_urls