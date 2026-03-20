"""
Routes protocoles expérimentaux
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services.protocol_service import ProtocolService
from app.schemas.all_schemas import ProtocolCreate, ProtocolResponse
from uuid import UUID
from typing import List

router = APIRouter()


@router.post("/{analysis_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_analysis_protocol(
    analysis_id: UUID,
    protocol: ProtocolCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau protocole expérimental"""
    service = ProtocolService(db)
    
    new_protocol = service.create_protocol(
        analysis_id=analysis_id,
        hypothesis=protocol.hypothesis,
        independent_variables=protocol.independent_variables,
        dependent_variables=protocol.dependent_variables,
        control_variables=protocol.control_variables,
        methodology=protocol.methodology,
        risk_analysis=protocol.risk_analysis,
        estimated_cost=protocol.estimated_cost
    )
    
    return {
        "message": "Protocol created successfully",
        "protocol": new_protocol
    }


@router.get("/{analysis_id}", response_model=List[ProtocolResponse])
async def get_analysis_protocols(
    analysis_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Récupère les protocoles d'une analyse"""
    service = ProtocolService(db)
    protocols = service.get_analysis_protocols(analysis_id, skip, limit)
    return protocols
