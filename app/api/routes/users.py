"""
Routes utilisateur
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services.user_service import UserService
from app.schemas.all_schemas import UserCreate, UserResponse, UserLogin
from app.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.repositories.user_repo import UserRepository
from datetime import timedelta
from app.core.settings import settings
from app.core.logging import logger
import uuid

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Crée un utilisateur (utilisé par les tests)"""
    try:
        service = UserService(db)
        return service.register_user(
            email=user.email,
            name=user.name,
            password=user.password,
            institution=user.institution,
            role=user.role
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Enregistre un nouvel utilisateur avec mot de passe"""
    try:
        service = UserService(db)
        new_user = service.register_user(
            email=user.email,
            name=user.name,
            password=user.password,
            institution=user.institution,
            role=user.role
        )
        return {
            "message": "User created successfully",
            "user": {
                "id": str(new_user.id),
                "name": new_user.name,
                "email": new_user.email
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=dict)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Connecte un utilisateur par email/password et retourne un JWT"""
    try:
        service = UserService(db)
        user = service.login_user(user_login.email, user_login.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
            
        token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": token, "token_type": "bearer", "user": {"id": str(user.id), "name": user.name, "email": user.email}}
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to Demo Mode ONLY if explicitly enabled or for testing connection issues
        if ("OperationalError" in str(type(e)) or "connection" in str(e).lower()) and settings.ENVIRONMENT == "development":
            mock_id = str(uuid.uuid4())
            token = create_access_token(
                data={"sub": mock_id, "demo": True},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            return {
                "access_token": token, 
                "token_type": "bearer", 
                "user": {"id": mock_id, "name": "Demo User", "email": user_login.email},
                "mode": "demo"
            }
        raise e


@router.post("/register-and-login", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_and_login(user: UserCreate, db: Session = Depends(get_db)):
    """Enregistre un nouvel utilisateur et retourne un JWT directement"""
    try:
        service = UserService(db)
        new_user = service.register_user(
            email=user.email,
            name=user.name,
            password=user.password,
            institution=user.institution,
            role=user.role
        )
        token = create_access_token(
            data={"sub": str(new_user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": token, "token_type": "bearer", "user": {"id": str(new_user.id), "name": new_user.name, "email": new_user.email}}
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        
        # Capture conflict errors (user already exists)
        if isinstance(e, ValueError) or "unique constraint" in str(e).lower() or "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="User with this email already exists."
            )
        
        # Determine if it's a database-related error
        is_db_error = any(term in str(e).lower() for term in ["operationalerror", "connection", "refused", "psycopg2", "target machine actively refused"])
        
        # Fallback to Demo Mode if DB is down (Dev only)
        if is_db_error and settings.ENVIRONMENT == "development":
            logger.warning("Database unavailable. Falling back to Demo Mode for registration.")
            mock_id = str(uuid.uuid4())
            token = create_access_token(
                data={"sub": mock_id, "demo": True},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            return {
                "access_token": token, 
                "token_type": "bearer", 
                "user": {"id": mock_id, "name": user.name, "email": user.email},
                "mode": "demo"
            }
            
        logger.exception("Unexpected error during registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Récupère les infos de l'utilisateur courant"""
    return current_user
