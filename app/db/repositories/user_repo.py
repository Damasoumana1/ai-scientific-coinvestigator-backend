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
        institution: Optional[str] = None,
        role: Optional[str] = None
    ) -> User:
        """Crée un nouvel utilisateur"""
        user = User(
            email=email,
            name=name,
            institution=institution,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    # authenticate removed as there is no password in SQL schema
