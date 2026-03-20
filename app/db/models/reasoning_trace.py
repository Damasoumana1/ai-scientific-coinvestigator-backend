"""
Database Models for Reasoning Traces
"""
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class ReasoningTrace(Base):
    """Trace de raisonnement pour audit/transparence"""
    __tablename__ = "reasoning_traces"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    step_number = Column(Integer)
    reasoning = Column(Text)
    source_chunks = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("AnalysisRun", back_populates="traces")
    
    def __repr__(self):
        return f"<ReasoningTrace {self.step_number}>"
