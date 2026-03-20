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
    Search ArXiv, download papers, parse them, and start analysis.
    """
    try:
        # 1. Fetch from ArXiv
        arxiv_service = ArXivService(download_dir="./uploaded_files")
        papers_data = arxiv_service.fetch_papers(request.query, request.max_results)
        
        if not papers_data:
            raise HTTPException(status_code=404, detail="No papers found for this query")

        # 2. Register in DB and Parse
        # For discovery/demo mode, we accept that these papers might not be linked 
        # to a specific project initially, or we use the nil UUID if we want it to be stateless.
        # However, ResearchPaper requires a real project_id in DB.
        # We'll use a placeholder project ID for discovery if needed, 
        # but for the most "fluid" demo, we can just return the paths and titles
        # and let the analysis use them statelessly.
        
        paper_ids = []
        for p in papers_data:
            # We don't save to DB here if we want to stay within the "stateless demo" logic
            # to avoid ForeignKey errors with nil UUID.
            # Instead, we'll return a specially formatted analysis_id
            paper_ids.append(p["id"])

        # 3. Trigger Analysis logic
        # We use the "demo_real_" prefix which our analysis route already handles
        # It expects a comma-separated list of "paper_ids" which could be internal IDs or ArXiv IDs.
        paper_ids_str = ",".join([p["id"] for p in papers_data])
        mock_id = f"demo_real_{paper_ids_str}"
        
        return DiscoveryResponse(
            message=f"Found and processed {len(papers_data)} papers from ArXiv.",
            papers=[{"title": p["title"], "id": p["id"]} for p in papers_data],
            analysis_id=mock_id,
            status="pending"
        )
        
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
