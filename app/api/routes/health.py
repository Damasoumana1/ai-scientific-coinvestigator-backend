"""
Health check endpoint
"""
from fastapi import APIRouter, HTTPException
from app.db.session import engine
from app.core.logging import logger
import asyncio

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "AI Scientific Co-Investigator API",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """Full readiness check - verify all dependencies"""
    checks = {
        "database": False,
        "qdrant": False,
        "embeddings": False
    }
    
    try:
        # Check database
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
    
    try:
        # Check Qdrant
        from app.rag.vector_store import VectorStore
        from app.core.settings import settings
        vs = VectorStore(url=settings.VECTOR_DB_URL)
        # Try to get collections
        vs.client.get_collections()
        checks["qdrant"] = True
    except Exception as e:
        logger.error(f"Qdrant check failed: {e}")
    
    try:
        # Check embeddings (quick test)
        from app.rag.embeddings import EmbeddingGenerator
        eg = EmbeddingGenerator()
        # Just verify it can be initialized
        checks["embeddings"] = True
    except Exception as e:
        logger.error(f"Embeddings check failed: {e}")
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "status": "ready" if all_ready else "not_ready"
    }


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}
