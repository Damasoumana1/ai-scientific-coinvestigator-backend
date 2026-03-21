"""
User Repository
"""
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.repositories.base_repo import BaseRepository
from app.core.security import hash_password, verify_password
from app.schemas.all_schemas import UserCreate
from typing import Optional


class UserRepository(BaseRepository[User, UserCreate, UserCreate]):
    """Repository pour gestion des utilisateurs"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Récupère utilisateur par email"""
        return self.db.query(User).filter(User.email == email).first()
    
    # get_by_username removed as it's not in SQL schema
    
    def create_user(
        self,
        email: str,
        name: str,
        hashed_password: str,
        institution: Optional[str] = None,
        role: Optional[str] = None
    ) -> User:
        """Crée un nouvel utilisateur"""
        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            institution=institution,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur (vérifie email et password hash)"""
        user = self.get_by_email(email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
