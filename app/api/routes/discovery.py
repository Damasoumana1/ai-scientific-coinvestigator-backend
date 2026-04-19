"""
Discovery API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.dependencies import get_db
from app.services.arxiv_service import ArXivService
from app.services.doaj_service import DOAJService
from app.services.pubmed_service import PubMedService
from app.services.analysis_service import AnalysisService
from app.core.logging import logger
import os

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10

class DiscoveryResponse(BaseModel):
    message: str
    papers: List[dict]
    analysis_id: str
    status: str

def map_to_discipline(paper: dict) -> str:
    """
    Maps a paper to one of the 5 target disciplines based on its metadata.
    """
    source = paper.get("source", "")
    sources = paper.get("sources", [source])
    categories = paper.get("categories", [])
    title = paper.get("title", "").lower()
    summary = paper.get("summary", "").lower()

    # Priority 1: Life Sciences & Medicine (PubMed always maps here)
    if "PubMed" in sources:
        return "Life Sciences & Medicine"

    # Priority 2: Computer Science & AI
    cs_keywords = ["computer science", "neural network", "deep learning", "artificial intelligence", "algorithms"]
    if any(c.startswith("cs.") for c in categories) or any(k in title or k in summary for k in cs_keywords):
        return "Computer Science & AI"

    # Priority 3: Physics & Mathematics
    math_phys_categories = ["math.", "phys.", "stat.", "astro-ph.", "quant-ph.", "nlin."]
    if any(any(c.startswith(mp) for mp in math_phys_categories) for c in categories):
        return "Physics & Mathematics"

    # Priority 4: Engineering
    eng_categories = ["eess."]
    eng_keywords = ["engineering", "electronics", "circuits", "hardware", "material science"]
    if any(any(c.startswith(ec) for ec in eng_categories) for c in categories) or any(k in title or k in summary for k in eng_keywords):
        return "Engineering"

    # Priority 5: Social Sciences
    soc_categories = ["econ.", "q-fin."]
    soc_keywords = ["sociology", "psychology", "economics", "philosophy", "social", "humanities"]
    if any(any(c.startswith(sc) for sc in soc_categories) for c in categories) or any(k in title or k in summary for k in soc_keywords):
        return "Social Sciences"

    # Fallback based on DOAJ subjects if still missing
    doaj_subjects = [s.lower() for s in categories] if source == "DOAJ" else []
    if any("medicine" in s or "biology" in s for s in doaj_subjects): return "Life Sciences & Medicine"
    if any("social" in s or "law" in s or "education" in s for s in doaj_subjects): return "Social Sciences"
    if any("mathematics" in s or "physics" in s for s in doaj_subjects): return "Physics & Mathematics"
    if any("technology" in s or "engineering" in s for s in doaj_subjects): return "Engineering"
    if any("computer" in s for s in doaj_subjects): return "Computer Science & AI"

    return "General Science"

@router.post("/search", response_model=DiscoveryResponse)
async def discovery_search(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Search ArXiv, DOAJ, and PubMed and return merged metadata for browsing.
    """
    try:
        # 1. Fetch from ArXiv
        arxiv_service = ArXivService(download_dir="./uploaded_files")
        arxiv_data = arxiv_service.fetch_papers(request.query, request.max_results)
        
        # 2. Fetch from DOAJ
        doaj_service = DOAJService(download_dir="./uploaded_files")
        doaj_data = doaj_service.fetch_papers(request.query, request.max_results)
        
        # 3. Fetch from PubMed
        pubmed_service = PubMedService(download_dir="./uploaded_files")
        pubmed_data = pubmed_service.fetch_papers(request.query, request.max_results)
        
        # 4. Merge and deduplicate by title
        seen_titles = {}
        merged_results = []
        
        all_papers = []
        for p in arxiv_data:
            p["source"] = "ArXiv"
            all_papers.append(p)
        for p in doaj_data:
            all_papers.append(p)
        for p in pubmed_data:
            all_papers.append(p)
            
        for paper in all_papers:
            import re
            norm_title = re.sub(r'\W+', '', paper["title"].lower())
            
            if norm_title in seen_titles:
                existing_index = seen_titles[norm_title]
                if paper["source"] not in merged_results[existing_index]["sources"]:
                    merged_results[existing_index]["sources"].append(paper["source"])
                if paper.get("has_pdf") and not merged_results[existing_index].get("has_pdf"):
                    merged_results[existing_index]["url"] = paper["url"]
                    merged_results[existing_index]["has_pdf"] = True
                # Merge categories
                if "categories" in paper:
                    current_cats = merged_results[existing_index].get("raw_categories", [])
                    merged_results[existing_index]["raw_categories"] = list(set(current_cats + paper["categories"]))
            else:
                paper["sources"] = [paper["source"]]
                if paper["source"] == "ArXiv":
                    paper["has_pdf"] = True
                
                seen_titles[norm_title] = len(merged_results)
                merged_results.append({
                    "title": paper["title"],
                    "id": paper["id"],
                    "authors": paper["authors"],
                    "summary": paper["summary"],
                    "publication_date": paper["publication_date"],
                    "url": paper.get("url"),
                    "sources": paper["sources"],
                    "has_pdf": paper.get("has_pdf", False),
                    "raw_categories": paper.get("categories", [])
                })
        
        # 5. Assign disciplines
        for i in range(len(merged_results)):
            paper_for_mapping = {
                "sources": merged_results[i]["sources"],
                "categories": merged_results[i].get("raw_categories", []),
                "title": merged_results[i]["title"],
                "summary": merged_results[i]["summary"]
            }
            merged_results[i]["discipline"] = map_to_discipline(paper_for_mapping)
            # Remove raw_categories to keep response clean
            merged_results[i].pop("raw_categories", None)

        if not merged_results:
            raise HTTPException(status_code=404, detail="No papers found for this query")
        
        return DiscoveryResponse(
            message=f"Found {len(merged_results)} unique papers matching your query.",
            papers=merged_results,
            analysis_id="", 
            status="idle"
        )
        
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
