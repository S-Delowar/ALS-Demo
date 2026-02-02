import requests
from bs4 import BeautifulSoup

def fetch_page_data(url):
    """
    Fetches the HTML content and extracts:
    1. Readable text (for verification).
    2. Open Graph Image (for thumbnail).
    
    Returns: dict {'text': str, 'image': str or None}
    """
    if not url:
        return {'text': "", 'image': None}
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Extract Thumbnail (Open Graph)
        og_image = soup.find("meta", property="og:image")
        thumbnail_url = og_image["content"] if og_image else None
        
        # Fallback: Twitter Card Image
        if not thumbnail_url:
            twitter_img = soup.find("meta", name="twitter:image")
            thumbnail_url = twitter_img["content"] if twitter_img else None

        # 2. Extract Text (Cleaned)
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)[:8000]
        
        return {
            'text': text,
            'image': thumbnail_url
        }
        
    except Exception as e:
        print(f"Scraping failed for {url}: {e}")
        return {'text': "", 'image': None}