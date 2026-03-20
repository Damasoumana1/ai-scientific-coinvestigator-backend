"""
Database Models for Research Gaps
"""
from sqlalchemy import Column, Text, ForeignKey, Float, UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class ResearchGap(Base):
    """Lacune de recherche identifiée"""
    __tablename__ = "research_gaps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    description = Column(Text)
    importance_score = Column(Float)
    suggested_direction = Column(Text)
    
    # Relationships
    analysis = relationship("AnalysisRun", back_populates="gaps")
    
    def __repr__(self):
        return f"<ResearchGap {self.id}>"
