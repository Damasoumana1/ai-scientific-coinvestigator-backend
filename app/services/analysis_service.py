"""
Service pour exécution des analyses
"""
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.repositories.analysis_repo import AnalysisRepository
from app.db.models.analysis_run import AnalysisRun
from datetime import datetime
import json
from app.core.logging import logger

class AnalysisService:
    """Service pour orchestration des analyses K2 Think"""
    
    def __init__(self, db: Session):
        self.analysis_repo = AnalysisRepository(db)
    
    def create_analysis_run(
        self,
        project_id: UUID,
        model_used: str
    ):
        """Crée une nouvelle run d' d'analyse"""
        analysis = AnalysisRun(
            project_id=project_id,
            model_used=model_used,
            status="PENDING",
            started_at=datetime.utcnow()
        )
        self.analysis_repo.create(analysis)
        return analysis
    
    def complete_analysis(
        self,
        analysis_id: UUID,
        result: dict = None,
        status: str = "COMPLETED"
    ):
        """Marque une analyse comme complétée"""
        analysis = self.analysis_repo.get_by_id(analysis_id)
        
        if analysis:
            analysis.status = status
            analysis.completed_at = datetime.utcnow()
            if result:
                analysis.result_data = result # SQLAlchemy handles JSON serialization
            self.analysis_repo.db.add(analysis)
            self.analysis_repo.db.commit()
            self.analysis_repo.db.refresh(analysis)
        
        return analysis

    async def process_analysis(self, analysis_id: str, request):
        """Tâche de fond pour traiter l'analyse"""
        from app.services.k2_think_engine import K2ThinkEngine
        from app.db.repositories.paper_repo import PaperRepository
        from app.db.models.research_paper import ResearchPaper
        from app.models.schemas import AnalysisRequest as K2AnalysisRequest, ScientificDocument
        from app.db.models.reasoning_trace import ReasoningTrace
        from app.services.arxiv_service import ArXivService
        from app.services.doaj_service import DOAJService
        from app.services.pubmed_service import PubMedService
        from app.services.openalex_service import OpenAlexService
        
        db = self.analysis_repo.db
        try:
            # 1. Fetch papers from DB or Remote
            paper_repo = PaperRepository(db)
            analysis_run = self.analysis_repo.get_by_id(UUID(analysis_id))
            project_id = analysis_run.project_id
            
            docs = []
            for pid in request.paper_ids:
                # Try UUID search first
                paper = None
                try:
                    paper_uuid = UUID(pid)
                    paper = paper_repo.get_by_id(paper_uuid)
                except (ValueError, AttributeError):
                    # Try Remote ID search in DB
                    paper = db.query(ResearchPaper).filter(
                        ResearchPaper.remote_id == pid,
                        ResearchPaper.project_id == project_id
                    ).first()
                
                if not paper:
                    # FETCH FROM REMOTE AND SAVE
                    logger.info(f"Paper {pid} not in DB. Fetching metadata on-demand...")
                    remote_data = None
                    try:
                        if "doaj_" in pid:
                            svc = DOAJService(); remote_data = svc.fetch_papers(pid.replace("doaj_", ""), 1)
                        elif "pubmed_" in pid:
                            svc = PubMedService(); remote_data = svc.fetch_papers(pid.replace("pubmed_", ""), 1)
                        elif "openalex_" in pid:
                            svc = OpenAlexService(); remote_data = svc.fetch_papers(pid.replace("openalex_", ""), 1)
                        elif "arxiv_" in pid:
                            svc = ArXivService(); remote_data = svc.fetch_papers(pid.replace("arxiv_", ""), 1)
                        else:
                            # Fallback to ArXiv if no prefix (for old saved papers without prefix)
                            svc = ArXivService(); remote_data = svc.fetch_papers(pid, 1)
                        
                        if remote_data:
                            p_info = remote_data[0]
                            paper = ResearchPaper(
                                project_id=project_id,
                                remote_id=pid,
                                title=p_info.get("title", "Unknown"),
                                authors=", ".join(p_info.get("authors", [])),
                                summary=p_info.get("summary", ""),
                                publication_year=datetime.now().year # Fallback
                            )
                            db.add(paper)
                            db.commit()
                            db.refresh(paper)
                            logger.info(f"Saved remote paper {pid} to project {project_id}")
                        else:
                            logger.warning(f"No remote data found for {pid}")
                    except Exception as fetch_err:
                        logger.error(f"Failed to fetch/save remote paper {pid}: {fetch_err}")

                if paper:
                    # Convert authors string to list
                    author_list = [a.strip() for a in paper.authors.split(",")] if paper.authors else ["Unknown"]
                    
                    # Determine document type based on remote_id prefix
                    dtype = "custom"
                    if paper.remote_id:
                        if "pubmed_" in paper.remote_id: dtype = "pubmed"
                        elif "arxiv_" in paper.remote_id or "." in paper.remote_id: dtype = "arxiv"
                        else: dtype = "arxiv" # default for most research platforms

                    docs.append(ScientificDocument(
                        id=str(paper.id),
                        title=paper.title,
                        authors=author_list,
                        abstract=paper.summary or "",
                        content=paper.summary or "", 
                        document_type=dtype,
                        url=paper.pdf_path or ""
                    ))

            if not docs:
                logger.error(f"No documents found for analysis {analysis_id}")
                raise ValueError("Zero documents identified for analysis. Aborting.")

            # 2. Prepare K2 Request
            k2_req = K2AnalysisRequest(
                documents=docs,
                user_id=request.user_id,
                user_profile=request.user_profile,
                reasoning_depth=request.reasoning_depth,
                ethics_rigor=request.ethics_rigor,
                info_density=request.info_density
            )

            # 3. Call K2 Engine
            engine = K2ThinkEngine()
            result = await engine.process_analysis_request(k2_req)

            # 4. Save Reasoning Trace (Detailed audit log)
            trace = ReasoningTrace(
                analysis_id=UUID(analysis_id),
                step_number=1,
                reasoning=result.reasoning_summary or "Analysis complete",
                source_chunks=result.reasoning_trace # JSON field
            )
            db.add(trace)
            
            # 5. Complete Analysis
            # result is a Pydantic model, convert to dict for storage
            self.complete_analysis(UUID(analysis_id), result=result.model_dump())
            db.commit()

        except Exception as e:
            db.rollback() # CLEAN TRANSACTION
            import traceback
            logger.error(f"Background analysis error for {analysis_id}: {str(e)}")
            logger.error(traceback.format_exc())
            try:
                self.complete_analysis(UUID(analysis_id), status="FAILED")
                db.commit()
            except Exception as final_err:
                logger.error(f"Failed to even mark analysis as FAILED: {final_err}")
                db.rollback()
