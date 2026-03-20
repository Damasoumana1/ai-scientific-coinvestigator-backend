import os
import glob
from app.rag.pdf_parser import PDFParser
from app.services.k2_think_engine import K2ThinkEngine
from app.models.schemas import AnalysisRequest as K2AnalysisRequest, ScientificDocument, DocumentType
import asyncio

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_files")
print(f"UPLOAD_DIR: {UPLOAD_DIR}")

# Test with actual uploaded files
test_pids = [
    "18c685f0-0658-4502-a9a1-b683e98962a0",
    "e7e941d6-16f8-4c3d-a927-e3788ce69581",
    "8c430616-b83f-45b3-a619-d0e73e02b936"
]

async def run_test():
    docs = []
    for pid in test_pids:
        pattern = os.path.join(UPLOAD_DIR, f"{pid}*.pdf")
        files = glob.glob(pattern)
        
        if files:
            try:
                safe_filename = os.path.basename(files[0]).encode('ascii', 'replace').decode('ascii')
                text = PDFParser.extract_text(files[0])
                metadata = PDFParser.extract_metadata(files[0])
                print(f"Extracted {len(text)} chars from {safe_filename}")
                
                docs.append(ScientificDocument(
                    id=pid,
                    title=metadata.get("title") or safe_filename,
                    authors=[metadata.get("author")] if metadata.get("author") else ["Unknown"],
                    abstract="Extracted from PDF",
                    content=text,
                    document_type=DocumentType.PDF
                ))
            except Exception as e:
                print(f"Extraction failed for {pid}: {e}")
                
    if not docs:
        print("No documents extracted!")
        return
        
    print(f"Testing K2ThinkEngine with {len(docs)} documents...")
    try:
        engine = K2ThinkEngine()
        k2_request = K2AnalysisRequest(documents=docs)
        result = await engine.process_analysis_request(k2_request)
        print("Success! Reasonning completed.")
        print(f"Comparisons found: {len(result.comparative_analysis.divergences) if result.comparative_analysis else 0}")
    except Exception as k2_err:
        print(f"K2 API Failed: {k2_err}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())

