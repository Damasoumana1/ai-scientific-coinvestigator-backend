"""
Database Models for User Management
"""
from sqlalchemy import Column, DateTime, Text, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class User(Base):
    """Utilisateur de l'application"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=True)

    institution = Column(Text)
    role = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.name}>"
