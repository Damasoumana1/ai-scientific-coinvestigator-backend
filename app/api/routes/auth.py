"""
Routes pour l'authentification OAuth2 (Google)
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
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

    # Always use the explicit setting — never derive from request.url
    # (Hugging Face proxies strip https → causes redirect_uri mismatch)
    redirect_uri = settings.GOOGLE_REDIRECT_URI

    # Tell Authlib the real scheme so the state URL is correct too
    request.scope["scheme"] = "https"

    return await oauth.google.authorize_redirect(request, redirect_uri)


from app.core.logging import logger

@router.get("/google/callback")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    """Gère le retour de Google après authentification"""
    try:
        logger.info("Google callback received")
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            logger.error("No userinfo found in Google token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not retrieve user info from Google."
            )
            
        email = user_info.get('email')
        name = user_info.get('name') or email.split('@')[0] if email else "User"
        
        logger.info(f"Google login attempt for email: {email}")
        
        if not email:
            logger.error("Email not provided by Google")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google."
            )
            
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(email)
        
        if not user:
            logger.info(f"Creating new user for email: {email}")
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
        
        logger.info(f"Successfully authenticated user: {email}")
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}", exc_info=True)
        # Redirect to frontend with error info instead of showing raw JSON
        error_msg = str(e).replace('"', "'")
        frontend_error_url = f"{settings.FRONTEND_URL}/login?error={error_msg[:200]}"
        return RedirectResponse(url=frontend_error_url)
