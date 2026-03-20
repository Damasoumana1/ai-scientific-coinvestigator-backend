"""
Protocol Repository
"""
from sqlalchemy.orm import Session
from app.db.models.protocol import ExperimentalProtocol
from uuid import UUID
from app.db.repositories.base_repo import BaseRepository
from app.schemas.all_schemas import ProtocolCreate
from typing import Optional, List


class ProtocolRepository(BaseRepository[ExperimentalProtocol, ProtocolCreate, ProtocolCreate]):
    """Repository pour gestion des protocoles expérimentaux"""
    
    def __init__(self, db: Session):
        super().__init__(db, ExperimentalProtocol)
    
    def get_by_analysis(self, analysis_id: UUID, skip: int = 0, limit: int = 100) -> List[ExperimentalProtocol]:
        """Récupère protocoles d'une analyse"""
        return self.db.query(ExperimentalProtocol).filter(
            ExperimentalProtocol.analysis_id == analysis_id
        ).offset(skip).limit(limit).all()
