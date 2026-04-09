"""
Discovery API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.dependencies import get_db
from app.services.arxiv_service import ArXivService
from app.services.analysis_service import AnalysisService
from app.core.logging import logger
import os

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    max_results: int = 3

class DiscoveryResponse(BaseModel):
    message: str
    papers: List[dict]
    analysis_id: str
    status: str

@router.post("/search", response_model=DiscoveryResponse)
async def discovery_search(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Search ArXiv and return metadata for browsing.
    """
    try:
        # 1. Fetch from ArXiv (Metadata only now)
        arxiv_service = ArXivService(download_dir="./uploaded_files")
        papers_data = arxiv_service.fetch_papers(request.query, request.max_results)
        
        if not papers_data:
            raise HTTPException(status_code=404, detail="No papers found for this query")
        
        return DiscoveryResponse(
            message=f"Found {len(papers_data)} papers matching your query.",
            papers=[{
                "title": p["title"], 
                "id": p["id"],
                "authors": p["authors"],
                "summary": p["summary"],
                "publication_date": p["publication_date"]
            } for p in papers_data],
            analysis_id="", # Analysis to be triggered by user selection
            status="idle"
        )
        
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
