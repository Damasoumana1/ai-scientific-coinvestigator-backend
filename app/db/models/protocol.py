"""
Database Models for Experimental Protocols
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class ExperimentalProtocol(Base):
    """Protocole expérimental généré"""
    __tablename__ = "experimental_protocols"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    hypothesis = Column(Text)
    independent_variables = Column(JSON)
    dependent_variables = Column(JSON)
    control_variables = Column(JSON)
    methodology = Column(Text)
    risk_analysis = Column(Text)
    estimated_cost = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("AnalysisRun", back_populates="protocols")
    
    def __repr__(self):
        return f"<ExperimentalProtocol {self.id}>"
