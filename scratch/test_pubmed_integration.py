
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from app.services.doaj_service import DOAJService
from app.services.arxiv_service import ArXivService
from app.services.pubmed_service import PubMedService

def test_pubmed_search():
    print("Testing PubMed search...")
    service = PubMedService()
    results = service.fetch_papers("cancer immunotherapy", max_results=5)
    print(f"Found {len(results)} results from PubMed")
    for r in results:
        print(f"- {r['title']} (Has PDF: {r['has_pdf']})")
        if r['has_pdf']:
            print(f"  URL: {r['url']}")

def test_discovery_logic_simulation():
    print("\nTesting Triple-Source Discovery logic simulation...")
    # Simulate the logic in discovery.py
    arxiv_service = ArXivService()
    doaj_service = DOAJService()
    pubmed_service = PubMedService()
    
    query = "Alzheimer's disease"
    max_results = 5
    
    arxiv_data = arxiv_service.fetch_papers(query, max_results)
    doaj_data = doaj_service.fetch_papers(query, max_results)
    pubmed_data = pubmed_service.fetch_papers(query, max_results)
    
    print(f"ArXiv: {len(arxiv_data)} papers")
    print(f"DOAJ: {len(doaj_data)} papers")
    print(f"PubMed: {len(pubmed_data)} papers")
    
    merged = []
    seen = set()
    
    for p in arxiv_data + doaj_data + pubmed_data:
        title_key = "".join(p["title"].lower().split())
        if title_key not in seen:
            merged.append(p["title"])
            seen.add(title_key)
            
    print(f"Total unique papers merged: {len(merged)}")

if __name__ == "__main__":
    test_pubmed_search()
    test_discovery_logic_simulation()
