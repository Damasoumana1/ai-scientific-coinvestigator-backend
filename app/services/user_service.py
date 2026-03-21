"""
Service métier pour utilisateurs
"""
from sqlalchemy.orm import Session
from typing import Optional
from app.db.repositories.user_repo import UserRepository
from app.core.security import hash_password, verify_password
from datetime import timedelta
from app.core.settings import settings


class UserService:
    """Service pour logique métier utilisateurs"""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
    
    def register_user(self, email: str, name: str, password: str, institution: Optional[str] = None, role: Optional[str] = None):
        """Enregistre un nouvel utilisateur"""
        # Check if user exists
        if self.user_repo.get_by_email(email):
            raise ValueError(f"User with email {email} already exists")
        
        hashed_password = hash_password(password)
        return self.user_repo.create_user(email, name, hashed_password, institution, role)
    
    def login_user(self, email: str, password: str):
        """Connecte un utilisateur"""
        user = self.user_repo.authenticate(email, password)
        if not user:
            return None
        return user
