"""
Database Models for Projects
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class Project(Base):
    """Projet de recherche"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    research_field = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    papers = relationship("ResearchPaper", back_populates="project", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.title}>"
