"""
Service for searching and downloading papers from DOAJ.
"""
import httpx
import os
import uuid
from typing import List, Dict, Optional
from app.core.logging import logger

class DOAJService:
    def __init__(self, download_dir: str = "./uploaded_files"):
        self.download_dir = download_dir
        self.base_url = "https://doaj.org/api/v1/search/articles"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def fetch_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search DOAJ for papers and filter for PDF availability.
        """
        logger.info(f"Searching DOAJ for: {query} (max: {max_results})")
        
        params = {
            "pageSize": max_results
        }
        
        # DOAJ search query is part of the path
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}/{encoded_query}"
        
        try:
            # Using synchronous get to match ArXivService style for easy integration
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
            results = []
            for item in data.get("results", []):
                bibjson = item.get("bibjson", {})
                
                # Extract PDF URL if available
                pdf_url = None
                links = bibjson.get("link", [])
                
                # Prioritize application/pdf or URLs containing 'pdf'
                for link in links:
                    if link.get("content_type") == "application/pdf" or "pdf" in link.get("url", "").lower():
                        pdf_url = link.get("url")
                        break
                
                # If no PDF found, take the first available link as fallback
                fallback_url = links[0].get("url") if links else None
                
                results.append({
                    "id": f"doaj_{item.get('id') or uuid.uuid4().hex[:10]}",
                    "title": bibjson.get("title", "Untitled"),
                    "authors": [a.get("name") for a in bibjson.get("author", [])],
                    "summary": bibjson.get("abstract", "No abstract available."),
                    "url": pdf_url or fallback_url,
                    "has_pdf": pdf_url is not None,
                    "categories": [s.get("term") for s in bibjson.get("subject", [])],
                    "publication_date": bibjson.get("year", "n.d."),
                    "source": "DOAJ"
                })
                
            return results
        except Exception as e:
            logger.error(f"DOAJ search error: {e}")
            return []

    def download_paper(self, paper_url: str, paper_id: str) -> str:
        """
        Downloads a paper from a direct URL.
        """
        if not paper_url:
            return ""
            
        file_name = f"{paper_id}.pdf"
        file_path = os.path.join(self.download_dir, file_name)
        
        if os.path.exists(file_path):
            return file_path
            
        logger.info(f"Downloading DOAJ paper: {paper_url}")
        try:
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                response = client.get(paper_url)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
            return file_path
        except Exception as e:
            logger.error(f"Failed to download DOAJ paper {paper_id}: {e}")
            return ""
