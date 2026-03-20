"""
Service métier pour projets
"""
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from app.db.repositories.project_repo import ProjectRepository
from app.db.models.project import Project


class ProjectService:
    """Service pour logique métier projets"""
    
    def __init__(self, db: Session):
        self.project_repo = ProjectRepository(db)
    
    def create_project(self, user_id: UUID, title: str, description: Optional[str] = None, research_field: Optional[str] = None):
        """Crée un nouveau projet"""
        project = Project(
            user_id=user_id,
            title=title,
            description=description,
            research_field=research_field or "other"
        )
        return self.project_repo.create(project)
    
    def get_user_projects(self, user_id: UUID, skip: int = 0, limit: int = 100):
        """Récupère projets de l'utilisateur"""
        return self.project_repo.get_by_user(user_id, skip, limit)
