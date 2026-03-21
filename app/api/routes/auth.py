"""
Routes pour l'authentification OAuth2 (Google)
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from app.dependencies import get_db
from app.core.settings import settings
from app.core.security import create_access_token
from app.db.repositories.user_repo import UserRepository
from datetime import timedelta
import uuid

router = APIRouter()

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/google/login")
async def login_google(request: Request):
    """Redirige vers la page de connexion Google"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured on the server."
        )
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    """Gère le retour de Google après authentification"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not retrieve user info from Google."
            )
            
        email = user_info.get('email')
        name = user_info.get('name')
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(email)
        
        if not user:
            # Créer l'utilisateur s'il n'existe pas (sans mot de passe)
            user = user_repo.create_user(
                email=email,
                name=name,
                hashed_password=None, # OAuth users don't have a local password
                institution=None,
                role="user"
            )
            
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": {
                "id": str(user.id), 
                "name": user.name, 
                "email": user.email
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )
