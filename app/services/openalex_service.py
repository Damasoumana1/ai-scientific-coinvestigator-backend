"""
Service for searching papers via OpenAlex.
"""
import httpx
from typing import List, Dict
from app.core.logging import logger

class OpenAlexService:
    def __init__(self, email: str = "soumanadama93@gmail.com"):
        self.base_url = "https://api.openalex.org/works"
        self.email = email

    def fetch_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search OpenAlex for papers (Metadata).
        """
        logger.info(f"Searching OpenAlex for: {query} (max: {max_results})")
        params = {
            "search": query,
            "mailto": self.email,
            "per-page": max_results
        }
        results = []
        try:
            with httpx.Client() as client:
                response = client.get(self.base_url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                items = data.get("results", [])
                
                for item in items:
                    # Ignore results with no title
                    if not item.get("title"):
                        continue
                        
                    # Reconstruct inverted abstract
                    abstract = ""
                    abs_dict = item.get("abstract_inverted_index")
                    if abs_dict:
                        # Find max index to pre-allocate array
                        max_idx = -1
                        for indices in abs_dict.values():
                            for idx in indices:
                                if idx > max_idx:
                                    max_idx = idx
                                    
                        if max_idx >= 0:
                            words = [""] * (max_idx + 1)
                            for word, indices in abs_dict.items():
                                for idx in indices:
                                    words[idx] = word
                            abstract = " ".join([w for w in words if w]).strip()
                    else:
                        abstract = "No abstract available."

                    # Extract PDF url if open access
                    oa = item.get("open_access", {})
                    pdf_url = oa.get("oa_url")
                    
                    authors = []
                    for authorship in item.get("authorships", []):
                        author = authorship.get("author", {})
                        if author.get("display_name"):
                            authors.append(author.get("display_name"))
                            
                    concepts = [c.get("display_name") for c in item.get("concepts", [])[:5]]
                    
                    # Ensure ID is clean (OpenAlex ids look like https://openalex.org/W298...)
                    raw_id = item.get("id", "")
                    clean_id = raw_id.split("/")[-1] if raw_id else "unknown_id"

                    results.append({
                        "id": clean_id,
                        "title": item.get("title"),
                        "authors": authors,
                        "summary": abstract,
                        "url": pdf_url or item.get("doi"),
                        "has_pdf": bool(pdf_url),
                        "categories": concepts,
                        "publication_date": item.get("publication_date")
                    })
        except Exception as e:
            logger.error(f"Error fetching from OpenAlex: {e}")
            
        return results
