"""
API Router principal
"""
from fastapi import APIRouter
from app.api.routes import (
    users, 
    projects, 
    papers, 
    analysis, 
    protocols, 
    discovery,
    auth
)

router = APIRouter()

# Include all route groups
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(projects.router, prefix="/projects", tags=["Projects"])
router.include_router(papers.router, prefix="/papers", tags=["Papers"])
router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
router.include_router(protocols.router, prefix="/protocols", tags=["Protocols"])
router.include_router(discovery.router, prefix="/discovery", tags=["Discovery"])
