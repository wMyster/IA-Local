from typing import List, Dict, Any
from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    results = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for item in raw_results:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "url": item.get("href", "")
                })
    except Exception as e:
        print(f"[AVISO] Erro na busca Web (DuckDuckGo): {e}")
    return results
