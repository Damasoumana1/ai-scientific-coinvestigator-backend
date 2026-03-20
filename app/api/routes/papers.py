"""
Routes articles scientifiques
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services.paper_service import PaperService
from app.schemas.all_schemas import PaperCreate, PaperResponse
from uuid import UUID
from typing import List, Optional
import os
import shutil
import uuid

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload d'un fichier PDF"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Save file to disk
    file_id = str(uuid.uuid4())
    dest_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    paper_title = title or file.filename.replace(".pdf", "")

    # Only record in DB if project_id is provided and DB is available
    if project_id:
        try:
            service = PaperService(db)
            new_paper = service.add_paper(
                project_id=UUID(project_id),
                title=paper_title,
                pdf_path=dest_path
            )
            return {"message": "Paper uploaded and recorded", "file": dest_path, "id": str(new_paper.id)}
        except Exception:
            pass

    return {"message": "Paper uploaded successfully", "file": dest_path, "id": file_id, "filename": file.filename}


@router.post("/{project_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_paper_to_project(
    project_id: UUID,
    paper: PaperCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute un article à un projet"""
    service = PaperService(db)
    
    new_paper = service.add_paper(
        project_id=project_id,
        title=paper.title,
        authors=paper.authors,
        journal=paper.journal,
        publication_year=paper.publication_year,
        pdf_path=paper.pdf_path
    )
    
    return {
        "message": "Paper added successfully",
        "paper": new_paper
    }


@router.get("/{project_id}", response_model=List[PaperResponse])
async def get_project_papers(
    project_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Récupère les articles d'un projet"""
    service = PaperService(db)
    papers = service.get_project_papers(project_id, skip, limit)
    return papers
