import re
import httpx
from typing import List, Dict, Any

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_html_text(html_content: str) -> str:
    # Remover scripts e estilos
    text = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remover tags HTML
    text = re.sub(r'<.*?>', ' ', text)
    # Limpar múltiplos espaços e quebras de linha
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_url_text(url: str, max_chars: int = 2000) -> str:
    try:
        with httpx.Client(headers=HEADERS, timeout=5.0, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                cleaned = clean_html_text(resp.text)
                return cleaned[:max_chars]
    except Exception as e:
        print(f"[AVISO] Não foi possível ler o link {url}: {e}")
    return ""

def search_web(query: str, max_results: int = 3, deep_scrape: bool = True) -> List[Dict[str, Any]]:
    results = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for item in raw_results:
                url = item.get("href", "") or item.get("link", "")
                snippet = item.get("body", "") or item.get("snippet", "")
                title = item.get("title", "")
                
                full_text = snippet
                if deep_scrape and url:
                    extracted = scrape_url_text(url, max_chars=2000)
                    if extracted and len(extracted) > len(snippet):
                        full_text = extracted

                results.append({
                    "title": title,
                    "snippet": snippet,
                    "full_text": full_text,
                    "url": url
                })
    except Exception as e:
        print(f"[AVISO] Erro na busca Web: {e}")
    return results
