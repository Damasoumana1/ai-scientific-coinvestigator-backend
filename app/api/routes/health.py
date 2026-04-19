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

@router.get("/migrate-credits")
async def manual_migration():
    """Manual migration endpoint to debug Supabase and force schema updates"""
    from sqlalchemy import text
    results = []
    try:
        # Create a new connection with explicit isolation level for DDL
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            # 1. Add credits column
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 2000;"))
                results.append({"step": "add_credits", "status": "success"})
            except Exception as e:
                results.append({"step": "add_credits", "error": str(e)})

            # 2. Add last_refill_date column
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_refill_date DATE;"))
                results.append({"step": "add_date", "status": "success"})
            except Exception as e:
                results.append({"step": "add_date", "error": str(e)})

            # 3. Backfill missing values
            try:
                conn.execute(text("UPDATE users SET credits = 2000 WHERE credits IS NULL;"))
                results.append({"step": "backfill", "status": "success"})
            except Exception as e:
                results.append({"step": "backfill", "error": str(e)})
                
            # 4. Verification
            try:
                res = conn.execute(text("SELECT email, credits, last_refill_date FROM users LIMIT 5;"))
                rows = [dict(r._mapping) for r in res]
                results.append({"step": "verify", "users_sample": rows})
            except Exception as e:
                results.append({"step": "verify", "error": str(e)})

    except Exception as e:
        results.append({"step": "connection", "error": str(e)})

    return {"status": "migration_attempted", "details": results}
