"""
Service pour gestion des articles scientifiques
"""
from sqlalchemy.orm import Session
from app.db.repositories.paper_repo import PaperRepository
from app.db.models.research_paper import ResearchPaper, UUID
from typing import List, Optional


class PaperService:
    """Service pour ingestion et gestion des articles"""
    
    def __init__(self, db: Session):
        self.paper_repo = PaperRepository(db)
    
    def add_paper(
        self,
        project_id: UUID,
        title: str,
        authors: Optional[str] = None,
        journal: Optional[str] = None,
        publication_year: Optional[int] = None,
        pdf_path: Optional[str] = None
    ):
        """Ajoute un article au projet"""
        paper = ResearchPaper(
            project_id=project_id,
            title=title,
            authors=authors,
            journal=journal,
            publication_year=publication_year,
            pdf_path=pdf_path
        )
        self.paper_repo.create(paper)
        return paper
    
    def get_project_papers(self, project_id: UUID, skip: int = 0, limit: int = 100):
        """Récupère articles d'un projet"""
        return self.paper_repo.get_by_project(project_id, skip, limit)
