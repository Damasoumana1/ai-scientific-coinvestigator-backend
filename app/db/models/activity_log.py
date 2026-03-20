"""
Database Models for Activity Logs
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class ActivityLog(Base):
    """Log d'activité utilisateur"""
    __tablename__ = "activity_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(Text)
    _metadata = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<ActivityLog {self.action}>"