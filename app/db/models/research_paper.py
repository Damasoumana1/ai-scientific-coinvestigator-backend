"""
Database Models for Research Papers
"""
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class ResearchPaper(Base):
    """Article scientifique ingéré"""
    __tablename__ = "research_papers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    remote_id = Column(Text, index=True) # ID ArXiv, PubMed, etc.
    title = Column(Text)
    authors = Column(Text)
    journal = Column(Text)
    summary = Column(Text) # Abstract
    publication_year = Column(Integer)
    pdf_path = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="papers")
    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ResearchPaper {self.title[:50]}...>"
