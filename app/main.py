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
    # Create tables on startup (dev convenience — use Alembic in production)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created / verified successfully")
    except Exception as e:
        logger.error(f"Could not connect to database: {e}")
        logger.error("Make sure PostgreSQL is running on localhost:5432")
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
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
