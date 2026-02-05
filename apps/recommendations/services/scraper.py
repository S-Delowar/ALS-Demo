# import requests
# from bs4 import BeautifulSoup

# def fetch_page_data(url):
#     """
#     Fetches the HTML content and extracts:
#     1. Readable text (for verification).
#     2. Open Graph Image (for thumbnail).
    
#     Returns: dict {'text': str, 'image': str or None}
#     """
#     if not url:
#         return {'text': "", 'image': None}
        
#     headers = {
#         # Using a standard browser User-Agent to avoid being blocked
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     }
    
#     try:
#         response = requests.get(url, headers=headers, timeout=5)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         thumbnail_url = None

#         # --- FIX 1: Robust Open Graph Extraction ---
#         # We use attrs={"property": "..."} to be explicit.
#         og_image = soup.find("meta", attrs={"property": "og:image"})
        
#         # We also check if 'content' actually exists inside the tag to avoid KeyErrors
#         if og_image and "content" in og_image.attrs:
#             thumbnail_url = og_image["content"]
        
#         # --- FIX 2: Robust Twitter Card Fallback ---
#         if not thumbnail_url:
#             # We use attrs={"name": "..."} here as well
#             twitter_img = soup.find("meta", attrs={"name": "twitter:image"})
            
#             if twitter_img and "content" in twitter_img.attrs:
#                 thumbnail_url = twitter_img["content"]

#         # 3. Extract Text (Cleaned)
#         for script in soup(["script", "style", "nav", "footer", "aside"]):
#             script.decompose()
            
#         text = soup.get_text(separator=' ', strip=True)[:8000]
        
#         return {
#             'text': text,
#             'image': thumbnail_url
#         }
        
#     except Exception as e:
#         print(f"Scraping failed for {url}: {e}")
#         return {'text': "", 'image': None}



from playwright.sync_api import sync_playwright

def fetch_page_data(url):
    """
    Fetches the HTML content using a real browser (Playwright) and extracts:
    1. Readable text.
    2. Open Graph Image (or Twitter fallback).
    
    Returns: dict {'text': str, 'image': str or None}
    """
    if not url:
        return {'text': "", 'image': None}

    try:
        with sync_playwright() as p:
            # 1. Launch Browser
            browser = p.chromium.launch(headless=True)
            
            # 2. Create Context with a real User Agent
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()

            # 3. Navigate (Wait for the network to be idle to ensure JS has loaded)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=10000)
            except Exception as e:
                print(f"Navigation error for {url}: {e}")
                browser.close()
                return {'text': "", 'image': None}

            # 4. Extract Image (Run JS in the browser to find the tags)
            thumbnail_url = page.evaluate("""() => {
                // Try Open Graph first
                const og = document.querySelector("meta[property='og:image']");
                if (og && og.content) return og.content;

                // Try Twitter Fallback
                const tw = document.querySelector("meta[name='twitter:image']");
                if (tw && tw.content) return tw.content;

                return null;
            }""")

            # 5. Extract Text (Clean the DOM inside the browser first)
            text = page.evaluate("""() => {
                // Remove clutter elements
                const selectors = ['script', 'style', 'nav', 'footer', 'aside', 'noscript'];
                document.querySelectorAll(selectors.join(',')).forEach(el => el.remove());
                
                // Return clean text
                return document.body.innerText;
            }""")
            
            # Cleanup
            browser.close()
            
            # Truncate text if needed (Python side)
            clean_text = " ".join(text.split())[:8000]

            return {
                'text': clean_text,
                'image': thumbnail_url
            }

    except Exception as e:
        print(f"Playwright scraping failed for {url}: {e}")
        return {'text': "", 'image': None}