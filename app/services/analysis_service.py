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
        status: str = "COMPLETED"
    ):
        """Marque une analyse comme complétée"""
        analysis = self.analysis_repo.get_by_id(analysis_id)
        
        if analysis:
            analysis.status = status
            analysis.completed_at = datetime.utcnow()
            self.analysis_repo.update(analysis_id, analysis)
        
        return analysis
