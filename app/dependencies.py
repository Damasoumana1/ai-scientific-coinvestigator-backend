"""
Dépendances FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.db.repositories.user_repo import UserRepository


def get_db() -> Generator[Session, None, None]:
    """Dependency pour obtenir une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Récupère l'utilisateur courant depuis le token JWT"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # If it's a demo token, bypass DB lookup
    if payload.get("demo"):
        class MockUser:
            def __init__(self, id, email, name):
                self.id = id
                self.email = email
                self.name = name
                self.institution = "Demo"
                self.role = "Researcher"
                self.is_admin = False
        
        return MockUser(user_id, "demo@example.com", "Demo User")

    user_repo = UserRepository(db)
    try:
        user = user_repo.get_by_id(user_id)
    except Exception as e:
        # If DB is down, we can't verify the user unless it's a demo token
        from app.core.logging import logger
        logger.error(f"Database error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed. Please use Demo Mode."
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_admin_user(
    current_user = Depends(get_current_user)
):
    """Vérifie que l'utilisateur est admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
