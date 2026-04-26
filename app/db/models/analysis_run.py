"""
Database Models for Analysis Runs
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class AnalysisRun(Base):
    """Execution d'une analyse multi-documents"""
    __tablename__ = "analysis_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    model_used = Column(Text)
    status = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result_data = Column(JSON) # JSON blob for frontend consumption
    
    # Relationships
    project = relationship("Project", back_populates="analysis_runs")
    contradictions = relationship("Contradiction", back_populates="analysis")
    gaps = relationship("ResearchGap", back_populates="analysis")
    protocols = relationship("ExperimentalProtocol", back_populates="analysis")
    exports = relationship("Export", back_populates="analysis")
    traces = relationship("ReasoningTrace", back_populates="analysis")
    
    def __repr__(self):
        return f"<AnalysisRun {self.id} - {self.status}>"
