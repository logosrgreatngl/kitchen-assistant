"""
Search Service — Google Search + Scraping
"""
import requests
from bs4 import BeautifulSoup
from config import Config


class SearchService:
    def __init__(self):
        print("✅ Search Service initialized")

    def search_web(self, query, num_results=None):
        if num_results is None:
            num_results = Config.MAX_SEARCH_RESULTS
        try:
            print(f"🔍 Searching: {query}")
            from googlesearch import search
            urls = []
            for url in search(query, num_results=num_results, lang='en'):
                urls.append(url)
                if len(urls) >= num_results:
                    break
            print(f"✅ Found {len(urls)} results")
            return urls
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def scrape_content(self, url):
        try:
            headers = {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
                )
            }
            r = requests.get(url, headers=headers, timeout=Config.SCRAPE_TIMEOUT)
            soup = BeautifulSoup(r.content, 'html.parser')
            for el in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                el.decompose()
            text = soup.get_text(separator=' ', strip=True)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            cleaned = ' '.join(lines)
            while '  ' in cleaned:
                cleaned = cleaned.replace('  ', ' ')
            return cleaned[:Config.MAX_SCRAPE_CHARS]
        except Exception as e:
            print(f"❌ Scrape error: {e}")
            return None

    def get_context(self, query, num_results=None):
        urls = self.search_web(query, num_results)
        if not urls:
            return None
        contexts = []
        for url in urls:
            content = self.scrape_content(url)
            if content:
                contexts.append(content)
        return '\n\n'.join(contexts) if contexts else None