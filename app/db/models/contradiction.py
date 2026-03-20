"""
Database Models for Contradictions
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, Float, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class Contradiction(Base):
    """Contradiction détectée entre documents"""
    __tablename__ = "contradictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    paper_a = Column(UUID(as_uuid=True), ForeignKey("research_papers.id"))
    paper_b = Column(UUID(as_uuid=True), ForeignKey("research_papers.id"))
    variable = Column(Text)
    statement_a = Column(Text)
    statement_b = Column(Text)
    confidence_score = Column(Float)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("AnalysisRun", back_populates="contradictions")
    
    def __repr__(self):
        return f"<Contradiction {self.id}>"
