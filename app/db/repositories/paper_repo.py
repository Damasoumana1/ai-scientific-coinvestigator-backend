"""
Paper Repository
"""
from sqlalchemy.orm import Session
from app.db.models.research_paper import ResearchPaper
from uuid import UUID
from app.db.repositories.base_repo import BaseRepository
from app.schemas.all_schemas import PaperCreate
from typing import Optional, List


class PaperRepository(BaseRepository[ResearchPaper, PaperCreate, PaperCreate]):
    """Repository pour gestion des articles scientifiques"""
    
    def __init__(self, db: Session):
        super().__init__(db, ResearchPaper)
    
    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 100) -> List[ResearchPaper]:
        """Récupère articles d'un projet"""
        return self.db.query(ResearchPaper).filter(
            ResearchPaper.project_id == project_id
        ).offset(skip).limit(limit).all()
