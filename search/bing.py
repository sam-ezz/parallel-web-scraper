import os
import requests
from .handle_key_not_found import handle_key_not_found
def get_keys_bing():
    api_key = os.environ.get("BING_API_KEY")

    if not api_key:
        handle_key_not_found.handle_key_not_found('BING','"https://learn.microsoft.com/en-us/previous-versions/bing/search-apis/bing-web-search/create-bing-search-service-resource"')
        return None
    return api_key


def bing_search(query, num_results=10, market='en-US',quiet:bool = False):
    """
    Performs a Bing Web Search using the v7.0 API.

    Args:
        query (str): The search term.
        num_results (int): The number of results to return.
        market (str): The market code (e.g., 'en-US', 'en-GB').
    Returns:
        list: A list of urls 
    """
    api_key = get_keys_bing()
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    
    headers = {
        'Ocp-Apim-Subscription-Key': api_key
    }
    
    all_results = []
    
    # Bing allows a max of 50 results per request.
    # We loop to fetch more if num_results > 50.
    batch_size = 50
    
    try:
        for offset in range(0, num_results, batch_size):
            # Calculate how many to fetch in this specific batch
            count = min(batch_size, num_results - offset)
            
            params = {
                'q': query,
                'count': count,
                'offset': offset,
                'mkt': market
            }
            
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status() 
            
            data = response.json()
            
            if 'webPages' not in data or 'value' not in data['webPages']:
                if not quiet:print("No more results found.")
                break
            

            for item in data['webPages']['value']:
                all_results.append(item.get('url'))
                
    except requests.exceptions.HTTPError as e:
        if not quiet:print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        if not quiet:print(f"An error occurred: {e}")
        return []

    return all_results
