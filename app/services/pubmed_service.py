"""
Service for searching and downloading papers from PubMed (NCBI).
"""
import httpx
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from app.core.logging import logger

class PubMedService:
    def __init__(self, download_dir: str = "./uploaded_files", email: str = "info@ai-coinvestigator.com"):
        self.download_dir = download_dir
        self.email = email
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def fetch_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search PubMed for papers and retrieve metadata.
        """
        logger.info(f"Searching PubMed for: {query} (max: {max_results})")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                # 1. Search for IDs
                search_url = f"{self.base_url}/esearch.fcgi"
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json",
                    "tool": "ai_coinvestigator",
                    "email": self.email
                }
                search_resp = client.get(search_url, params=search_params)
                search_resp.raise_for_status()
                id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])
                
                if not id_list:
                    return []
                
                # 2. Fetch metadata (Summary)
                summary_url = f"{self.base_url}/esummary.fcgi"
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(id_list),
                    "retmode": "json",
                    "tool": "ai_coinvestigator",
                    "email": self.email
                }
                summary_resp = client.get(summary_url, params=summary_params)
                summary_resp.raise_for_status()
                summary_data = summary_resp.json().get("result", {})
                
                results = []
                for pmid in id_list:
                    if pmid not in summary_data:
                        continue
                        
                    item = summary_data[pmid]
                    
                    # Extract PMID and potential PMC ID
                    pmid_val = item.get("uid")
                    pmcid = None
                    for article_id in item.get("articleids", []):
                        if article_id.get("idtype") == "pmc":
                            pmcid = article_id.get("value")
                    
                    # Construct PDF URL if PMCID is available
                    pdf_url = None
                    if pmcid:
                        # Standard PMC PDF pattern
                        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
                    
                    results.append({
                        "id": f"pubmed_{pmid_val}",
                        "title": item.get("title", "Untitled"),
                        "authors": [a.get("name") for a in item.get("authors", [])],
                        "summary": "Abstract available on PubMed. Full-text search enabled." if pmcid else "Abstract only.",
                        "url": pdf_url or f"https://pubmed.ncbi.nlm.nih.gov/{pmid_val}/",
                        "has_pdf": pdf_url is not None,
                        "publication_date": item.get("pubdate", "n.d."),
                        "source": "PubMed"
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return []

    def download_paper(self, paper_url: str, paper_id: str) -> str:
        """
        Downloads a paper from PubMed Central if PDF is available.
        Note: Access to PMC PDFs might require specific handling or follow redirects.
        """
        if not paper_url or "pdf" not in paper_url.lower():
            return ""
            
        file_name = f"{paper_id}.pdf"
        file_path = os.path.join(self.download_dir, file_name)
        
        if os.path.exists(file_path):
            return file_path
            
        logger.info(f"Downloading PubMed/PMC paper: {paper_url}")
        try:
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                response = client.get(paper_url)
                response.raise_for_status()
                # Verify content type to ensure it's a PDF
                if "application/pdf" not in response.headers.get("content-type", "").lower() and len(response.content) < 1000:
                    logger.warning(f"Download for {paper_id} did not yield a PDF (Content-Type: {response.headers.get('content-type')})")
                    return ""
                    
                with open(file_path, "wb") as f:
                    f.write(response.content)
            return file_path
        except Exception as e:
            logger.error(f"Failed to download PubMed paper {paper_id}: {e}")
            return ""
