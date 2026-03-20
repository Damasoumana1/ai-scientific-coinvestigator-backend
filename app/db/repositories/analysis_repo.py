"""
Analysis Repository
"""
from sqlalchemy.orm import Session
from app.db.models.analysis_run import AnalysisRun
from uuid import UUID
from app.db.repositories.base_repo import BaseRepository
from app.schemas.all_schemas import AnalysisRequest
from typing import Optional, List


class AnalysisRepository(BaseRepository[AnalysisRun, AnalysisRequest, AnalysisRequest]):
    """Repository pour gestion des analyses"""
    
    def __init__(self, db: Session):
        super().__init__(db, AnalysisRun)
    
    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 100) -> List[AnalysisRun]:
        """Récupère analyses d'un projet"""
        return self.db.query(AnalysisRun).filter(
            AnalysisRun.project_id == project_id
        ).offset(skip).limit(limit).all()
    
    def get_pending(self) -> List[AnalysisRun]:
        """Récupère analyses en attente"""
        return self.db.query(AnalysisRun).filter(
            AnalysisRun.status == "pending"
        ).all()
