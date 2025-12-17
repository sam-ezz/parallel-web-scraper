import random
from fake_useragent import UserAgent

ua = UserAgent(browsers=["Google", "Chrome", "Firefox", "Edge", "Opera"," Safari"])

def get_headers():
    
    user_agent = ua.random
    # Common headers 
    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'DNT': '1', 
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # Browser-Specific Header 
    if "Chrome" in user_agent or "Edg" in user_agent or "OPR" in user_agent:
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
        })
    elif "Firefox" in user_agent:
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'TE': 'trailers'
        })

    elif "Safari" in user_agent:
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })


    return headers
