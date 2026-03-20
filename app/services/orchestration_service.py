"""
Orchestration Service - K2 Think API
Hackathon: Utilise UNIQUEMENT K2 Think API comme modèle d'IA
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.k2_think_engine import K2ThinkEngine
from app.db.models.analysis_run import AnalysisRun
from app.models.schemas import AnalysisRequest, DocumentType
from app.core.logging import logger
from datetime import datetime
import uuid


class OrchestrationService:
    """
    Service d'Orchestration - Moteur K2 Think Unique
    Toutes les analyses utilisent UNIQUEMENT K2 Think API
    """
    
    def __init__(self):
        self.engine = K2ThinkEngine()
        logger.info("✅ OrchestrationService initialized with K2 Think Engine (UNIQUE AI MODEL)")
    
    async def run_comprehensive_analysis(
        self,
        project_id: str,
        documents: List[str],
        db: Session,
        k2_client=None
    ) -> Dict[str, Any]:
        """
        Exécute analyse complète avec K2 Think
        """
        analysis_id = str(uuid.uuid4())
        analysis_run = None
        
        try:
            # Valider input
            if not documents or len(documents) == 0:
                logger.warning(f"Analysis {analysis_id}: No documents provided")
                return {
                    "analysis_id": analysis_id,
                    "status": "error",
                    "error": "No documents provided"
                }
            
            logger.info(f"🚀 K2 Think Analysis {analysis_id}: Starting with {len(documents)} documents for project {project_id}")
            
            # Créer enregistrement analyse
            analysis_run = AnalysisRun(
                id=analysis_id,
                project_id=project_id,
                model_used="K2_Think_API_EXCLUSIVE",
                status="processing",
                started_at=datetime.utcnow()
            )
            db.add(analysis_run)
            db.commit()
            logger.info(f"✓ Analysis record created: {analysis_id}")
            
            # Créer AnalysisRequest pour K2 Think Engine
            from app.models.schemas import ScientificDocument
            analysis_request = AnalysisRequest(
                documents=[
                    ScientificDocument(
                        id=f"doc_{i}",
                        title=f"Document {i+1}",
                        authors=[],
                        abstract="",
                        content=doc,
                        document_type=DocumentType.CUSTOM,
                        doi=None,
                        arxiv_id=None,
                        publication_date=None,
                        citations_count=None
                    )
                    for i, doc in enumerate(documents)
                ],
                analysis_type="comprehensive"
            )
            
            # Exécuter analyse K2 Think
            logger.info(f"🤖 Calling K2 Think Engine...")
            result = await self.engine.process_analysis_request(analysis_request)
            
            # Mettre à jour enregistrement
            db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).update(
                {"status": "completed", "completed_at": datetime.utcnow()},
                synchronize_session=False
            )
            db.commit()
            logger.info(f"✅ Analysis {analysis_id} completed successfully")
            
            return {
                "analysis_id": analysis_id,
                "status": "success",
                "result": result.dict() if hasattr(result, 'dict') else result
            }
        except Exception as e:
            logger.error(f"❌ Analysis {analysis_id} failed: {str(e)}", exc_info=True)
            if analysis_run:
                db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).update(
                    {"status": "failed"},
                    synchronize_session=False
                )
                db.commit()
            
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error": str(e),
                "type": type(e).__name__
            }
    
    async def run_stress_test(
        self,
        hypothesis: str,
        documents: List[str],
        db: Session
    ) -> Dict[str, Any]:
        """
        Stress test hypothèse avec K2 Think
        """
        test_id = str(uuid.uuid4())
        try:
            logger.info(f"🧪 K2 Think Stress Test {test_id}: Testing hypothesis")
            
            # Utiliser K2 Think Engine pour stress testing
            from app.models.schemas import ScientificDocument
            analysis_request = AnalysisRequest(
                documents=[
                    ScientificDocument(
                        id="hyp_0",
                        title=f"Hypothesis Test",
                        authors=[],
                        abstract="",
                        content=hypothesis,
                        document_type=DocumentType.CUSTOM
                    )
                ],
                analysis_type="hypothesis_validation"
            )
            
            result = await self.engine.process_analysis_request(analysis_request)
            
            return {
                "test_id": test_id,
                "status": "success",
                "hypothesis_validation": result
            }
        except Exception as e:
            logger.error(f"Stress test {test_id} failed: {str(e)}")
            return {
                "test_id": test_id,
                "status": "error",
                "error": str(e)
            }
    
    async def generate_optimal_protocol(
        self,
        hypotheses: List[str],
        constraints: Dict,
        db: Session
    ) -> Dict[str, Any]:
        """
        Génère protocole optimal avec K2 Think
        """
        protocol_id = str(uuid.uuid4())
        try:
            logger.info(f"📋 K2 Think Protocol Generation {protocol_id}: Generating protocol for {len(hypotheses)} hypotheses")
            
            # Utiliser K2 Think Engine pour génération protocole
            from app.models.schemas import ScientificDocument
            combined_content = "\n".join([f"Hypothesis {i+1}: {h}" for i, h in enumerate(hypotheses)])
            
            analysis_request = AnalysisRequest(
                documents=[
                    ScientificDocument(
                        id="proto_0",
                        title="Protocol Generation Request",
                        authors=[],
                        abstract="",
                        content=combined_content,
                        document_type=DocumentType.CUSTOM
                    )
                ],
                analysis_type="protocol_design",
                constraints=constraints
            )
            
            result = await self.engine.process_analysis_request(analysis_request)
            
            return {
                "protocol_id": protocol_id,
                "status": "success",
                "protocol": result.proposed_protocol if result.proposed_protocol else {}
            }
        except Exception as e:
            logger.error(f"Protocol generation {protocol_id} failed: {str(e)}")
            return {
                "protocol_id": protocol_id,
                "status": "error",
                "error": str(e)
            }


