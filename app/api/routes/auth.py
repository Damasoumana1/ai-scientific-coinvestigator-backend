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
from app.core.logging import logger

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
        logger.error("Google OAuth client ID or secret missing in configuration")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured on the server."
        )

    # If settings.GOOGLE_REDIRECT_URI is set, use it. 
    # Otherwise, derive it from the current request URL (base) + callback path.
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    if not redirect_uri:
        # Construct redirect URI from the request base URL
        base_url = str(request.base_url).rstrip('/')
        # Ensure we use https if we are behind a proxy that terminates SSL
        if "hf.space" in base_url or request.headers.get("x-forwarded-proto") == "https":
            base_url = base_url.replace("http://", "https://")
        redirect_uri = f"{base_url}/api/v1/auth/google/callback"
    
    # MASK CLIENT ID FOR LOGGING (e.g. 6300...eat64)
    cid = settings.GOOGLE_CLIENT_ID or "MISSING"
    masked_cid = f"{cid[:10]}...{cid[-10:]}" if len(cid) > 20 else cid
    
    logger.info(f"Initiating Google OAuth login")
    logger.info(f"Using Google Redirect URI: {redirect_uri}")
    logger.info(f"Using Client ID: {masked_cid}")
    logger.info(f"Request Headers: {dict(request.headers)}")
    
    # Ensure Authlib uses https for the state param if we are in production
    if "https" in redirect_uri:
        request.scope["scheme"] = "https"

    try:
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Error during oauth authorize_redirect: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authorization error: {str(e)}"
        )


@router.get("/google/callback")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    """Gère le retour de Google après authentification"""
    logger.info("Google callback route reached")
    
    # Determine the redirect_uri used during the initial request
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    if not redirect_uri:
        base_url = str(request.base_url).rstrip('/')
        if "hf.space" in base_url or request.headers.get("x-forwarded-proto") == "https":
            base_url = base_url.replace("http://", "https://")
            request.scope["scheme"] = "https"
        redirect_uri = f"{base_url}/api/v1/auth/google/callback"

    try:
        logger.info(f"Callback full URL: {request.url}")
        
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            logger.error("No userinfo found in Google token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not retrieve user info from Google."
            )
            
        email = user_info.get('email')
        name = user_info.get('name') or (email.split('@')[0] if email else "User")
        
        logger.info(f"Google login successful for email: {email}")
        
        if not email:
            logger.error("Email not provided by Google")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google."
            )
            
        from app.services.user_service import UserService
        service = UserService(db)
        user = service.register_user_oauth(email=email, name=name)
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"Successfully authenticated user: {email}")
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}", exc_info=True)
        # Redirect to frontend with error info
        error_msg = str(e).replace('"', "'")
        frontend_error_url = f"{settings.FRONTEND_URL}/login?error={error_msg[:200]}"
        return RedirectResponse(url=frontend_error_url)
