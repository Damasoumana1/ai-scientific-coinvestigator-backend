"""
API Router principal
"""
from fastapi import APIRouter
from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router
from app.api.routes.papers import router as papers_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.protocols import router as protocols_router
from app.api.routes.discovery import router as discovery_router
from app.api.routes.auth import router as auth_router

router = APIRouter()

# Include all route groups
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(projects_router, prefix="/projects", tags=["Projects"])
router.include_router(papers_router, prefix="/papers", tags=["Papers"])
router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
router.include_router(protocols_router, prefix="/protocols", tags=["Protocols"])
router.include_router(discovery_router, prefix="/discovery", tags=["Discovery"])
