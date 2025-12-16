from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from .handle_key_not_found import handle_key_not_found 
import warnings
def get_keys_google():
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_key = os.environ.get("GOOGLE_CSE_ID")
    if not api_key:
        handle_key_not_found.handle_key_not_found('GOOGLE','https://console.cloud.google.com/marketplace/product/google/customsearch.googleapis.com')
    if not cse_key:
        handle_key_not_found.handle_key_not_found('GOOGLE','https://developers.google.com/custom-search/v1/introduction',suffix='_CSE_ID')
    return api_key,cse_key
 

def google_search(query:str, num_results:int =10,quiet:bool=False, **kwargs):
    """
    Performs a Google search using the Custom Search JSON API.

    Args:
        search_term (str): The query to search for.
        num_results (int): The total number of search results desired. 
                           Note: The API has a hard limit of 100 results.
        **kwargs: Additional parameters to pass to the API.

    Returns:
        list: A list of search result containing links and Returns an empty list on error.
    """
    all_results = []
    api_key,cse_id = get_keys_google()
    
    # The API is limited to 100 results total (10 pages of 10)
    if num_results > 100:
        warnings.warn("Warning: The API is limited to a maximum of 100 results. "
              "Fetching 100 results instead.",
              UserWarning,stacklevel=2)
        num_results = 100

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        
        # The API returns a max of 10 results per page, so we loop to get more
        for i in range(0, num_results, 10):
            start_index = i + 1
            
            num_for_this_request = min(10, num_results - i)

            res = service.cse().list(
                q=query,
                cx=cse_id,
                num=num_for_this_request,
                start=start_index,
                **kwargs
            ).execute()

            # If no items are returned, we've reached the end of results
            if 'items' not in res:
                break
            
            for item in res['items']:
                all_results.append(item.get('link'))

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    return all_results[:num_results]


