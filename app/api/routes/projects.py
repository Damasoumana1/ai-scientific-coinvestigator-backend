"""
Routes projets
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services.project_service import ProjectService
from app.schemas.all_schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from uuid import UUID
from typing import List

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau projet"""
    service = ProjectService(db)
    new_project = service.create_project(
        user_id=current_user.id,
        title=project.title,
        description=project.description,
        research_field=project.research_field
    )
    return {
        "message": "Project created successfully",
        "project": new_project
    }
...
@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Récupère les projets de l'utilisateur"""
    service = ProjectService(db)
    projects = service.get_user_projects(current_user.id, skip, limit)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère un projet spécifique"""
    service = ProjectService(db)
    project = service.project_repo.get_by_user_and_id(current_user.id, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project
