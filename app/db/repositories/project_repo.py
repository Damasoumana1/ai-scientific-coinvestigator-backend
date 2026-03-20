"""
Project Repository
"""
from sqlalchemy.orm import Session
from app.db.models.project import Project
from uuid import UUID
from app.db.repositories.base_repo import BaseRepository
from app.schemas.all_schemas import ProjectCreate, ProjectUpdate
from typing import Optional, List


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    """Repository pour gestion des projets"""
    
    def __init__(self, db: Session):
        super().__init__(db, Project)
    
    def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Project]:
        """Récupère projets d'un utilisateur"""
        return self.db.query(Project).filter(
            Project.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_by_user_and_id(self, user_id: UUID, project_id: UUID) -> Optional[Project]:
        """Récupère projet spécifique d'un utilisateur"""
        return self.db.query(Project).filter(
            Project.user_id == user_id,
            Project.id == project_id
        ).first()
