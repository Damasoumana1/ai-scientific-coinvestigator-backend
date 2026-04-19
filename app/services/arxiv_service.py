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

    def fetch_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search ArXiv for papers (Metadata only).
        """
        logger.info(f"Searching ArXiv for: {query} (max: {max_results})")
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for result in search.results():
            try:
                results.append({
                    "id": result.get_short_id(),
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "url": result.pdf_url,
                    "categories": result.categories,
                    "publication_date": result.published.strftime("%Y-%m-%d") if result.published else None
                })
            except Exception as e:
                logger.error(f"Error fetching metadata for {result.title}: {e}")
                
        return results

    def download_paper(self, arxiv_id: str) -> str:
        """
        Downloads a specific paper by its ArXiv ID and returns the file path.
        """
        file_name = f"{arxiv_id}.pdf"
        file_path = os.path.join(self.download_dir, file_name)
        
        if os.path.exists(file_path):
            return file_path
            
        logger.info(f"Downloading ArXiv paper: {arxiv_id}")
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        paper.download_pdf(dirpath=self.download_dir, filename=file_name)
        return file_path
