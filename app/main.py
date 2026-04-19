"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.logging import logger
from app.core.settings import settings
from app.db.session import engine
from app.db.base import Base
from app.api.router import router
from app.api.routes.health import router as health_router

# Import all models to ensure they are registered with Base
from app.db.models.user import User
from app.db.models.project import Project
from app.db.models.research_paper import ResearchPaper
from app.db.models.paper_chunk import PaperChunk
from app.db.models.analysis_run import AnalysisRun
from app.db.models.protocol import ExperimentalProtocol
from app.db.models.contradiction import Contradiction
from app.db.models.research_gap import ResearchGap
from app.db.models.reasoning_trace import ReasoningTrace
from app.db.models.export import Export
from app.db.models.activity_log import ActivityLog





# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-migration: Add missing credit columns to existing users table
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check if 'credits' column exists, add it if not
            try:
                conn.execute(text("SELECT credits FROM users LIMIT 1"))
                logger.info("Column 'credits' already exists in users table.")
            except Exception:
                conn.execute(text("ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 2000"))
                conn.commit()
                logger.info("Added 'credits' column to users table with default 2000.")
            
            # Check if 'last_refill_date' column exists, add it if not
            try:
                conn.execute(text("SELECT last_refill_date FROM users LIMIT 1"))
                logger.info("Column 'last_refill_date' already exists in users table.")
            except Exception:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_refill_date DATE"))
                conn.commit()
                logger.info("Added 'last_refill_date' column to users table.")
                
            # Backfill NULL credits to 2000 for existing users
            conn.execute(text("UPDATE users SET credits = 2000 WHERE credits IS NULL"))
            conn.commit()
            logger.info("Backfilled NULL credits to 2000 for existing users.")
    except Exception as e:
        logger.warning(f"Auto-migration warning (non-fatal): {str(e)}")

    # Create tables on startup (dev convenience — use Alembic in production)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created / verified successfully")
    except Exception as e:
        logger.error(f"CRITICAL: Could not connect to database or create tables: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Check your DATABASE_URL and ensure the database is reachable.")
        if "ssl" in str(e).lower():
            logger.error("SSL Error detected. Try adding ?sslmode=require to your DATABASE_URL.")
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# --- PROXY FIX MIDDLEWARE (Required for Hugging Face / OAuth) ---
@app.middleware("http")
async def fix_proxy_headers(request: Request, call_next):
    # If we are behind a proxy that terminates SSL, force the scheme to https
    # This prevents 'MismatchingStateError' in Authlib/OAuth
    if request.headers.get("x-forwarded-proto") == "https":
        request.scope["scheme"] = "https"
    
    # Optional: Fix Host if forwarded
    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_host:
        request.scope["server"] = (forwarded_host, 443)
        
    response = await call_next(request)
    return response

# Session middleware (required for Authlib/Google OAuth)
# 'same_site=lax' is essential for cross-site redirects (Google -> HF)
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=False  # Must be False if perceive as http internally, but we fix scheme above
)

# CORS middleware — origins controlled via ALLOWED_ORIGINS in .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health_router)          # Health checks (/health/*)
app.include_router(router, prefix="/api/v1")  # Main API (/api/v1/*)


@app.get("/", tags=["Root"])
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": "AI Scientific Co-Investigator API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
