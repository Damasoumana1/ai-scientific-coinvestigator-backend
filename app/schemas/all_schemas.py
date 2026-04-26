"""
Pydantic Schemas for API Requests/Responses
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
import uuid


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    institution: Optional[str] = None
    role: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    credits: int
    last_refill_date: Optional[date] = None
    research_profile: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ==================== PROJECT SCHEMAS ====================

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    research_field: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


# ==================== PAPER SCHEMAS ====================

class PaperBase(BaseModel):
    title: str
    authors: Optional[str] = None
    journal: Optional[str] = None
    publication_year: Optional[int] = None
    pdf_path: Optional[str] = None


class PaperCreate(PaperBase):
    pass


class PaperResponse(PaperBase):
    id: uuid.UUID
    project_id: uuid.UUID
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== ANALYSIS SCHEMAS ====================

class AnalysisRequest(BaseModel):
    analysis_type: str = "comprehensive"
    paper_ids: List[str]
    user_id: Optional[str] = None
    user_profile: Optional[str] = None
    reasoning_depth: Optional[str] = "exhaustive"
    ethics_rigor: Optional[str] = "standard"
    info_density: Optional[str] = "detailed"


class AnalysisResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    model_used: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)


# ==================== PROTOCOL SCHEMAS ====================

class ProtocolCreate(BaseModel):
    analysis_id: uuid.UUID
    hypothesis: Optional[str] = None
    independent_variables: Optional[dict] = None
    dependent_variables: Optional[dict] = None
    control_variables: Optional[dict] = None
    methodology: Optional[str] = None
    risk_analysis: Optional[str] = None
    estimated_cost: Optional[str] = None


class ProtocolResponse(BaseModel):
    id: uuid.UUID
    analysis_id: uuid.UUID
    hypothesis: Optional[str]
    independent_variables: Optional[dict]
    dependent_variables: Optional[dict]
    control_variables: Optional[dict]
    methodology: Optional[str]
    risk_analysis: Optional[str]
    estimated_cost: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== ERROR SCHEMA ====================

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None
