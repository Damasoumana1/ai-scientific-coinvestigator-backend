"""
Service pour exécution des analyses
"""
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.repositories.analysis_repo import AnalysisRepository
from app.db.models.analysis_run import AnalysisRun
from datetime import datetime
import json


class AnalysisService:
    """Service pour orchestration des analyses K2 Think"""
    
    def __init__(self, db: Session):
        self.analysis_repo = AnalysisRepository(db)
    
    def create_analysis_run(
        self,
        project_id: UUID,
        model_used: str
    ):
        """Crée une nouvelle run d' d'analyse"""
        analysis = AnalysisRun(
            project_id=project_id,
            model_used=model_used,
            status="PENDING",
            started_at=datetime.utcnow()
        )
        self.analysis_repo.create(analysis)
        return analysis
    
    def complete_analysis(
        self,
        analysis_id: UUID,
        result: dict = None,
        status: str = "COMPLETED"
    ):
        """Marque une analyse comme complétée"""
        analysis = self.analysis_repo.get_by_id(analysis_id)
        
        if analysis:
            analysis.status = status
            analysis.completed_at = datetime.utcnow()
            if result:
                analysis.result_data = json.dumps(result)
            self.analysis_repo.update(analysis_id, analysis)
        
        return analysis

    async def process_analysis(self, analysis_id: str, request):
        """Tâche de fond pour traiter l'analyse"""
        from app.services.k2_think_engine import K2ThinkEngine
        from app.db.repositories.paper_repo import PaperRepository
        from app.models.schemas import K2AnalysisRequest, ScientificDocument
        from app.db.models.reasoning_trace import ReasoningTrace
        
        db = self.analysis_repo.db
        try:
            # 1. Fetch papers from DB
            paper_repo = PaperRepository(db)
            db_papers = [paper_repo.get_by_id(pid) for pid in request.paper_ids]
            
            docs = []
            for p in db_papers:
                if p:
                    docs.append(ScientificDocument(
                        id=str(p.id),
                        title=p.title,
                        abstract=p.summary or "",
                        content=p.summary or "", # TODO: Full text if available
                        url=p.pdf_path or ""
                    ))

            # 2. Prepare K2 Request
            k2_req = K2AnalysisRequest(
                documents=docs,
                user_id=request.user_id,
                user_profile=request.user_profile,
                reasoning_depth=request.reasoning_depth,
                ethics_rigor=request.ethics_rigor,
                info_density=request.info_density
            )

            # 3. Call K2 Engine
            engine = K2ThinkEngine()
            result = await engine.process_analysis_request(k2_req)

            # 4. Save Reasoning Trace
            trace = ReasoningTrace(
                analysis_id=UUID(analysis_id),
                trace_data=json.dumps(result.get("reasoning_steps", [])),
                final_conclusion=result.get("strategic_recommendations", ""),
                tokens_used=0 
            )
            db.add(trace)
            
            # 5. Complete Analysis
            self.complete_analysis(UUID(analysis_id), result=result)
            db.commit()

        except Exception as e:
            from app.core.logging import logger
            logger.error(f"Background analysis error for {analysis_id}: {e}")
            self.complete_analysis(UUID(analysis_id), status="FAILED")
            db.commit()
