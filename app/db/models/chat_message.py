"""
Database Model for Chat Messages
"""
from sqlalchemy import Column, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class ChatMessage(Base):
    """Message d'une conversation scientifique"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    role = Column(Text, nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    reasoning_log = Column(Text, nullable=True) # Logs de raisonnement de l'IA
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("AnalysisRun", backref="chat_messages")
    
    def __repr__(self):
        return f"<ChatMessage {self.role}: {self.content[:20]}...>"
