
import os
import sys
from uuid import UUID

# Add the app directory to sys.path
backend_path = 'c:/Users/user/Desktop/ai-scientific-coinvestigator-backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.db.session import SessionLocal
from app.models.all_models import AnalysisRun

def check_analysis(analysis_id):
    db = SessionLocal()
    try:
        analysis = db.query(AnalysisRun).filter(AnalysisRun.id == UUID(analysis_id)).first()
        if not analysis:
            print(f"Analysis {analysis_id} not found in DB")
            return
        
        print(f"ID: {analysis.id}")
        print(f"Project ID: {analysis.project_id}")
        print(f"Status: {analysis.status}")
        print(f"Model: {analysis.model_used}")
        print(f"Result Data Type: {type(analysis.result_data)}")
        if analysis.result_data:
             import json
             print("Result Data JSON:")
             print(json.dumps(analysis.result_data, indent=2))
        else:
             print("Result Data: None")
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_analysis(sys.argv[1])
    else:
        print("Usage: python check_db.py <analysis_id>")
