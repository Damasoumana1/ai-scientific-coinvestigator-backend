"""
Discovery API Routes — unified search across ArXiv, DOAJ, PubMed, and OpenAlex.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.dependencies import get_db
from app.services.arxiv_service import ArXivService
from app.services.doaj_service import DOAJService
from app.services.pubmed_service import PubMedService
from app.services.openalex_service import OpenAlexService
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
    Handles: ArXiv (category codes), PubMed (source), DOAJ (subjects), OpenAlex (topics).
    """
    source = paper.get("source", "")
    sources = paper.get("sources", [source])
    categories = paper.get("categories", [])   # ArXiv codes or topic names
    title = paper.get("title", "").lower()
    summary = paper.get("summary", "").lower()

    # Lowercase join of all category/topic labels for keyword matching
    cats_lower = " ".join(c.lower() for c in categories)

    # Priority 1: Life Sciences & Medicine
    if "PubMed" in sources:
        return "Life Sciences & Medicine"
    life_keywords = ["medicine", "biology", "clinical", "health", "disease", "genomics",
                     "pharmaceutical", "neuroscience", "biomedical", "cancer", "patient"]
    if any(k in cats_lower or k in title or k in summary for k in life_keywords):
        return "Life Sciences & Medicine"

    # Priority 2: Computer Science & AI
    cs_arxiv = any(c.startswith("cs.") for c in categories)
    cs_keywords = ["computer science", "machine learning", "deep learning", "neural network",
                   "artificial intelligence", "algorithm", "natural language", "computer vision",
                   "reinforcement learning", "large language model"]
    if cs_arxiv or any(k in cats_lower or k in title or k in summary for k in cs_keywords):
        return "Computer Science & AI"

    # Priority 3: Physics & Mathematics
    math_phys_arxiv = ["math.", "phys.", "stat.", "astro-ph.", "quant-ph.", "nlin.", "gr-qc.", "hep-"]
    math_phys_keywords = ["mathematics", "physics", "quantum", "statistics", "astrophysics",
                           "thermodynamics", "algebra", "topology", "calculus"]
    if (any(any(c.startswith(mp) for mp in math_phys_arxiv) for c in categories)
            or any(k in cats_lower or k in title or k in summary for k in math_phys_keywords)):
        return "Physics & Mathematics"

    # Priority 4: Engineering
    eng_keywords = ["engineering", "electronics", "circuits", "hardware", "material science",
                    "robotics", "signal processing", "nanotechnology", "semiconductor"]
    if (any(c.startswith("eess.") for c in categories)
            or any(k in cats_lower or k in title or k in summary for k in eng_keywords)):
        return "Engineering"

    # Priority 5: Social Sciences
    soc_keywords = ["sociology", "psychology", "economics", "philosophy", "social science",
                    "humanities", "political science", "anthropology", "education", "law"]
    if (any(c.startswith(("econ.", "q-fin.")) for c in categories)
            or any(k in cats_lower or k in title or k in summary for k in soc_keywords)):
        return "Social Sciences"

    return "General Science"

@router.post("/search", response_model=DiscoveryResponse)
async def discovery_search(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Search ArXiv, DOAJ, PubMed, and OpenAlex — returns merged, deduplicated metadata.
    """
    import re
    try:
        # 1. Fetch from ArXiv
        arxiv_service = ArXivService(download_dir="./uploaded_files")
        arxiv_data = arxiv_service.fetch_papers(request.query, request.max_results)
        for p in arxiv_data:
            p["source"] = "ArXiv"
            p["has_pdf"] = True  # ArXiv always has PDF

        # 2. Fetch from DOAJ
        doaj_service = DOAJService(download_dir="./uploaded_files")
        doaj_data = doaj_service.fetch_papers(request.query, request.max_results)

        # 3. Fetch from PubMed
        pubmed_service = PubMedService(download_dir="./uploaded_files")
        pubmed_data = pubmed_service.fetch_papers(request.query, request.max_results)

        # 4. Fetch from OpenAlex (only open-access works)
        openalex_service = OpenAlexService(download_dir="./uploaded_files")
        openalex_data = openalex_service.fetch_papers(request.query, request.max_results)

        # 5. Merge and deduplicate by normalized title
        seen_titles: dict = {}
        merged_results: list = []

        all_papers = arxiv_data + doaj_data + pubmed_data + openalex_data

        for paper in all_papers:
            source = paper.get("source", "Unknown")
            norm_title = re.sub(r'\W+', '', paper.get("title", "").lower())
            if not norm_title:
                continue

            if norm_title in seen_titles:
                # Merge into existing entry
                existing_index = seen_titles[norm_title]
                existing = merged_results[existing_index]

                if source not in existing["sources"]:
                    existing["sources"].append(source)

                # Upgrade to direct PDF URL if current entry doesn't have one
                if paper.get("has_pdf") and not existing.get("has_pdf"):
                    existing["url"] = paper["url"]
                    existing["has_pdf"] = True

                # Merge categories/topics
                current_cats = existing.get("raw_categories", [])
                new_cats = paper.get("categories", [])
                existing["raw_categories"] = list(dict.fromkeys(current_cats + new_cats))

                # Prefer longer/richer abstract
                if len(paper.get("summary", "")) > len(existing.get("summary", "")):
                    existing["summary"] = paper["summary"]

                # Carry cited_by_count if OpenAlex provides it
                if paper.get("cited_by_count") and not existing.get("cited_by_count"):
                    existing["cited_by_count"] = paper["cited_by_count"]
            else:
                seen_titles[norm_title] = len(merged_results)
                merged_results.append({
                    "id": paper["id"],
                    "title": paper["title"],
                    "authors": paper.get("authors", []),
                    "summary": paper.get("summary", "No abstract available."),
                    "publication_date": paper.get("publication_date", "n.d."),
                    "url": paper.get("url"),
                    "has_pdf": paper.get("has_pdf", False),
                    "sources": [source],
                    "raw_categories": paper.get("categories", []),
                    "cited_by_count": paper.get("cited_by_count", 0),
                })

        # 6. Assign disciplines and clean up temp fields
        for entry in merged_results:
            entry["discipline"] = map_to_discipline({
                "sources": entry["sources"],
                "categories": entry.get("raw_categories", []),
                "title": entry["title"],
                "summary": entry["summary"],
            })
            entry.pop("raw_categories", None)  # Remove internal field from response

        if not merged_results:
            raise HTTPException(status_code=404, detail="No papers found for this query")

        logger.info(
            f"Discovery: {len(merged_results)} unique papers "
            f"(ArXiv:{len(arxiv_data)} DOAJ:{len(doaj_data)} "
            f"PubMed:{len(pubmed_data)} OpenAlex:{len(openalex_data)})"
        )

        return DiscoveryResponse(
            message=(
                f"Found {len(merged_results)} unique papers from "
                f"ArXiv, DOAJ, PubMed & OpenAlex."
            ),
            papers=merged_results,
            analysis_id="",
            status="idle"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
