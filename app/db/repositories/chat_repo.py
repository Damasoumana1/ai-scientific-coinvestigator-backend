"""
Chat Repository
"""
from sqlalchemy.orm import Session
from app.db.models.chat_message import ChatMessage
from uuid import UUID
from typing import List

class ChatRepository:
    """Repository pour gestion des messages de chat"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_message(self, analysis_id: UUID, role: str, content: str, reasoning_log: str = None) -> ChatMessage:
        """Enregistre un nouveau message"""
        message = ChatMessage(
            analysis_id=analysis_id,
            role=role,
            content=content,
            reasoning_log=reasoning_log
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_history(self, analysis_id: UUID) -> List[ChatMessage]:
        """Récupère l'historique d'une analyse"""
        return self.db.query(ChatMessage).filter(
            ChatMessage.analysis_id == analysis_id
        ).order_by(ChatMessage.created_at.asc()).all()
