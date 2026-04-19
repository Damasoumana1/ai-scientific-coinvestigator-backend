
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from app.services.doaj_service import DOAJService
from app.services.arxiv_service import ArXivService

def test_doaj_search():
    print("Testing DOAJ search...")
    service = DOAJService()
    results = service.fetch_papers("quantum computing", max_results=5)
    print(f"Found {len(results)} results from DOAJ")
    for r in results:
        print(f"- {r['title']} (Has PDF: {r['has_pdf']})")
        if r['has_pdf']:
            print(f"  URL: {r['url']}")

def test_merged_search():
    print("\nTesting Merged search logic simulation...")
    # Simulate the logic in discovery.py
    arxiv_service = ArXivService()
    doaj_service = DOAJService()
    
    query = "CRISPR"
    max_results = 5
    
    arxiv_data = arxiv_service.fetch_papers(query, max_results)
    doaj_data = doaj_service.fetch_papers(query, max_results)
    
    print(f"ArXiv: {len(arxiv_data)} papers")
    print(f"DOAJ: {len(doaj_data)} papers")
    
    merged = []
    seen = set()
    
    for p in arxiv_data:
        merged.append(p["title"])
        seen.add(p["title"].lower().strip())
        
    dupes = 0
    for p in doaj_data:
        if p["title"].lower().strip() in seen:
            dupes += 1
        else:
            merged.append(p["title"])
            
    print(f"Total unique papers: {len(merged)}")
    print(f"Duplicates found: {dupes}")

if __name__ == "__main__":
    test_doaj_search()
    test_merged_search()
