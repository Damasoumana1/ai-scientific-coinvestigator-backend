"""
Service pour gestion des protocoles expérimentaux
"""
from sqlalchemy.orm import Session
from app.db.repositories.protocol_repo import ProtocolRepository
from app.db.models.protocol import ExperimentalProtocol
from typing import Dict, List, Any, TYPE_CHECKING
from uuid import UUID
import json


class ProtocolService:
    """Service pour création et gestion des protocoles"""
    
    def __init__(self, db: Session):
        self.protocol_repo = ProtocolRepository(db)
    
    def create_protocol(
        self,
        analysis_id: UUID,
        hypothesis: str = None,
        independent_variables: Any = None,
        dependent_variables: Any = None,
        control_variables: Any = None,
        methodology: str = None,
        risk_analysis: str = None,
        estimated_cost: str = None
    ):
        """Crée un nouveau protocole expérimental"""
        protocol = ExperimentalProtocol(
            analysis_id=analysis_id,
            hypothesis=hypothesis,
            independent_variables=independent_variables,
            dependent_variables=dependent_variables,
            control_variables=control_variables,
            methodology=methodology,
            risk_analysis=risk_analysis,
            estimated_cost=estimated_cost
        )
        self.protocol_repo.create(protocol)
        return protocol
    
    def get_analysis_protocols(self, analysis_id: UUID, skip: int = 0, limit: int = 100):
        """Récupère protocoles d'une analyse"""
        return self.protocol_repo.get_by_analysis(analysis_id, skip, limit)
