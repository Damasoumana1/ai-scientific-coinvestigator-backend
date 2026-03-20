"""
Service for searching and downloading papers from ArXiv.
"""
import arxiv
import os
from typing import List, Dict
from app.core.logging import logger

class ArXivService:
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def fetch_papers(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search ArXiv for papers and download them.
        """
        logger.info(f"Searching ArXiv for: {query}")
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        downloaded_files = []
        for result in search.results():
            try:
                logger.info(f"Found paper: {result.title}")
                # Clean filename
                file_name = f"{result.get_short_id()}.pdf"
                file_path = os.path.join(self.download_dir, file_name)
                
                # Check if file already exists to avoid re-downloading
                if not os.path.exists(file_path):
                    result.download_pdf(dirpath=self.download_dir, filename=file_name)
                
                downloaded_files.append({
                    "path": file_path,
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "url": result.pdf_url,
                    "id": result.get_short_id(),
                    "publication_date": result.published.strftime("%Y-%m-%d") if result.published else None
                })
            except Exception as e:
                logger.error(f"Error downloading paper {result.title}: {e}")
                
        return downloaded_files
