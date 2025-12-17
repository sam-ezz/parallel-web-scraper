from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth
import time
import random
import requests
from bs4 import BeautifulSoup
from utils import get_headers,ua
from proxy import Proxies

proxies = Proxies()

def fetch_slow(url: str, timeout: int = 20, quiet: bool = False):
    """
    Fetches a URL using a headless browser (Playwright).
    Sacrifices speed for:
    1. JavaScript execution (dynamic content).
    2. Bot evasion (real browser headers).
    3. Network resilience (waiting for idle state).
    """

    try:
        proxy = proxies.get_proxy()
        proxy = {"server":proxy} if proxy is not None  else None
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True,
                                        args=[
                                        '--disable-http2',
                                        '--disable-blink-features=AutomationControlled',
                                        '--no-sandbox', 
                                        '--disable-setuid-sandbox'
                                    ])
            
            # Create a context with specific viewport to look like a real desktop user
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent= ua.random, #set a random User Agent
                locale='en-US',
                timezone_id='America/New_York',
            )
            
            page = context.new_page()
            Stealth().apply_stealth_sync(page)

            excluded_resources = ["image", "media", "font", "stylesheet"]
            def route_intercept(route):
                if route.request.resource_type in excluded_resources:
                    route.abort()
                else:
                    route.continue_()
            page.route("**/*", route_intercept)

            if not quiet: print(f" [Scrape Info] Navigating to {url}...")

            try:
                page.goto(url, timeout=timeout * 1000,wait_until='domcontentloaded') 
            except PlaywrightTimeout:
                if not quiet: print(" [Scrape Warning] Initial timeout, retrying...")
                page.goto(url, timeout=timeout * 1000, wait_until='domcontentloaded')
            
            try:
                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                page.mouse.down()
                time.sleep(random.uniform(0.1, 0.3))
                page.mouse.up()
            except:
                pass

            time.sleep(random.uniform(1,3))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)") #Scroll to bottom to trigger lazy-loading images/text
            time.sleep(2) #wait for new content to load

            html_content = page.content()
            
            browser.close()
            return html_content

    except PlaywrightTimeout:
        if not quiet: print(f" [Scrape Error] Timeout error for {url}")
        return {'url': url, 'error': 'Timeout (Browser)'}
    
    except Exception as e:
        error_msg = str(e).split('Call log:')[0].strip()
        # If the error is long, cut it
        if len(error_msg) > 200: 
            error_msg = error_msg[:200] + "..."
            
        if not quiet: print(f"  [Scrape Error] Unexpected error for {url}: {error_msg}")
        return {'url': url, 'error': f'Unexpected error: {error_msg}'}


def fetch_quick(url:str,timeout:int = 10,retries:int = 2,quiet:bool =False):
    """Fetches a single URL and parses its content."""
    for i in range(retries):
        try:
            headers = get_headers()
            proxy = proxies.get_proxy()
            proxy =  {"http": proxy, "https": proxy} if proxy is not None else None
            response = requests.get(url, 
                                    timeout=timeout,
                                    headers=headers,
                                    proxies=proxy
                                    )
            
            response.raise_for_status()
            return response
        
        except requests.exceptions.Timeout:
            if not quiet: print(f" [Scrape Error] Timeout error for {url}")
            if i == retries-1: return {'url': url, 'error': 'Timeout'}
        
        except requests.exceptions.RequestException as e:
            if not quiet: print(f"  [Scrape Error] Request failed for {url}: {e}")
            if i == retries-1: return {'url': url, 'error': f'Request failed: {e}'}
        
        except Exception as e:
            if not quiet: print(f"  An unexpected error occurred for {url}: {e}")
            if i == retries-1: return {'url': url, 'error': f'Unexpected error: {e}'}
        
def parse(url,raw_data):
    soup = BeautifulSoup(raw_data, 'html.parser')
    title = soup.title.string if soup.title else 'N/A'
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
    return {
        'url': url,
        'title': title,
        'paragraphs': paragraphs,
        'links': links
        }

def fetch_and_parse(url:str,timeout:int = 10,quiet:bool =False,quick:bool = False):
    raw_data = fetch_quick(url,timeout=timeout,quiet=quiet)
    if isinstance(raw_data,dict) and 'error' in raw_data : #if we get a error when using fetchquick 
        if quick: 
            return raw_data  #return errored one 
        else:
            raw_data = fetch_slow(url,timeout=timeout,quiet=quiet)
            if isinstance(raw_data,dict) and 'error' in raw_data :
                return raw_data
    else:
        raw_data = raw_data.text    

    return parse(url,raw_data)

