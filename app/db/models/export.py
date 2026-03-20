"""
Database Models for Exports
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class Export(Base):
    """Export d'un protocole/analyse"""
    __tablename__ = "exports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    format = Column(Text)
    file_path = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("AnalysisRun", back_populates="exports")
    
    def __repr__(self):
        # The .value attribute would fail on a Text column.
        return f"<Export {self.format} - {self.file_path}>"
