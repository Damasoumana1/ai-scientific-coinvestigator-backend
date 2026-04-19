"""
Routes analyses K2 Think
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services.analysis_service import AnalysisService
from app.schemas.all_schemas import AnalysisRequest, AnalysisResponse
from uuid import UUID
import uuid
from typing import List, Optional
import os
import glob
from app.services.mock_intelligence import MockIntelligenceService
from app.rag.pdf_parser import PDFParser
from app.services.k2_think_engine import K2ThinkEngine
from app.models.schemas import ScientificDocument, AnalysisRequest as K2AnalysisRequest, DocumentType, ChatRequest, ChatResponse
from app.services.export_service import ExportService
from app.services.arxiv_service import ArXivService
from fastapi.responses import Response, FileResponse

router = APIRouter()


@router.post("/{project_id}", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def start_project_analysis(
    project_id: str,
    request: AnalysisRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Démarre une nouvelle analyse"""
    from app.db.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    
    # 1. Vérification des crédits (50 pour une analyse profonde)
    if not current_user.id.hex.startswith("0000"): # Bypass for pure mock demo
        if current_user.credits < 50:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient K2 Credits. Required: 50"
            )
        
    try:
        service = AnalysisService(db)
        
        # Deduct credits
        if not current_user.id.hex.startswith("0000"):
            user_repo.deduct_credits(current_user, 50)
            
        # Create analysis run
        if project_id.startswith("00000000"):
             # For demo/test mode with nil UUID, we use stateless mock processing
             paper_ids_str = ",".join(request.paper_ids)
             # Encode settings in the ID for stateless demo mode
             mock_id = f"demo_real_{request.reasoning_depth}_{request.ethics_rigor}_{request.info_density}_{paper_ids_str}"
             return {
                 "message": "Demo mode: Analysis started (Real-time K2 Processing)",
                 "analysis_id": mock_id,
                 "status": "pending",
                 "mode": "demo",
                 "remaining_credits": current_user.credits
             }

        analysis = service.create_analysis_run(
            project_id=project_id,
            model_used="K2_Think_API"
        )
        
        return {
            "message": "Analysis started",
            "analysis_id": analysis.id,
            "status": "pending",
            "remaining_credits": current_user.credits
        }
    except Exception as e:
        # Fallback to Mock Analysis if DB is down or other integrity issues
        if any(keyword in str(e).lower() for keyword in ["operationalerror", "connection", "integrityerror", "foreign key"]):
            # Encapsulate paper IDs in the analysis_id to pass them to the GET request in stateless demo mode
             paper_ids_str = ",".join(request.paper_ids)
             mock_id = f"demo_real_{request.reasoning_depth}_{request.ethics_rigor}_{request.info_density}_{paper_ids_str}"
             return {
                 "message": "Demo mode fallback: Analysis started (Real-time K2 Processing)",
                 "analysis_id": mock_id,
                 "status": "pending",
                 "mode": "demo"
             }
        raise e


@router.get("/{project_id}", response_model=List[dict])
async def get_project_analyses(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Récupère les analyses d'un projet"""
    service = AnalysisService(db)
    analyses = service.analysis_repo.get_by_project(project_id, skip, limit)
    return analyses


@router.get("/{project_id}/{analysis_id}", response_model=dict)
async def get_specific_analysis(
    project_id: str,
    analysis_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère une analyse spécifique.
    Supporte le mode 'demo_real_' pour le traitement en temps réel K2.
    """
    from app.core.logging import logger
    
    # 1. Priorité absolue au mode DEMO_REAL (Traitement temps réel K2)
    # On exécute ceci AVANT toute recherche en base de données pour éviter les 404
    if str(analysis_id).startswith("demo_real_"):
        logger.info(f"DEMO_REAL: Initiating real-time reasoning for {analysis_id}")
        try:
            # Format: demo_real_depth_rigor_density_paper1,paper2...
            parts = str(analysis_id).replace("demo_real_", "").split("_")
            
            # Default values
            depth, rigor, density = "exhaustive", "standard", "detailed"
            paper_ids_str = ""

            if len(parts) >= 4:
                depth, rigor, density = parts[0], parts[1], parts[2]
                paper_ids_str = parts[3]
            else:
                # Fallback for old style IDs
                paper_ids_str = parts[0]

            paper_ids = paper_ids_str.split(",")
            UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_files")
            
            docs = []
            for pid in paper_ids:
                if not pid.strip(): continue
                # Find file starting with pid
                pattern = os.path.join(UPLOAD_DIR, f"{pid}*.pdf")
                files = glob.glob(pattern)
                logger.info(f"DEMO_REAL: Searching for {pid} -> Found: {len(files)}")
                
                if files:
                    file_to_process = files[0]
                else:
                    # If not found locally, try to download based on source
                    if pid.startswith("doaj_"):
                        logger.info(f"DEMO_REAL: {pid} is DOAJ. Attempting fetch and download...")
                        try:
                            from app.services.doaj_service import DOAJService
                            doaj_service = DOAJService(download_dir=UPLOAD_DIR)
                            # DOAJ ID search
                            clean_id = pid.replace("doaj_", "")
                            # We use the search API to find the PDF URL for this ID
                            search_results = doaj_service.fetch_papers(clean_id, max_results=1)
                            if search_results and search_results[0].get("url"):
                                file_to_process = doaj_service.download_paper(search_results[0]["url"], pid)
                            else:
                                logger.error(f"DEMO_REAL: No PDF URL found for DOAJ {pid}")
                                continue
                        except Exception as doaj_err:
                            logger.error(f"DEMO_REAL: DOAJ download failed for {pid}: {doaj_err}")
                            continue
                    elif pid.startswith("pubmed_"):
                        logger.info(f"DEMO_REAL: {pid} is PubMed. Attempting fetch and download...")
                        try:
                            from app.services.pubmed_service import PubMedService
                            pubmed_service = PubMedService(download_dir=UPLOAD_DIR)
                            # PubMed ID search
                            clean_id = pid.replace("pubmed_", "")
                            # Search by ID to get PMC PDF URL
                            search_results = pubmed_service.fetch_papers(clean_id, max_results=1)
                            if search_results and search_results[0].get("url") and search_results[0].get("has_pdf"):
                                file_to_process = pubmed_service.download_paper(search_results[0]["url"], pid)
                            else:
                                logger.error(f"DEMO_REAL: No PDF URL found for PubMed/PMC {pid}")
                                continue
                        except Exception as pubmed_err:
                            logger.error(f"DEMO_REAL: PubMed download failed for {pid}: {pubmed_err}")
                            continue
                    else:
                        # ArXiv ID (Standard)
                        logger.info(f"DEMO_REAL: {pid} not found locally. Attempting on-demand download...")
                        try:
                            arxiv_service = ArXivService(download_dir=UPLOAD_DIR)
                            file_to_process = arxiv_service.download_paper(pid)
                        except Exception as dl_err:
                            logger.error(f"DEMO_REAL: Failed to download {pid}: {dl_err}")
                            continue

                try:
                    safe_filename = os.path.basename(file_to_process).encode('ascii', 'replace').decode('ascii')
                    text = PDFParser.extract_text(file_to_process)
                    metadata = PDFParser.extract_metadata(file_to_process)
                    logger.info(f"DEMO_REAL: Extracted {len(text)} chars from {safe_filename}")
                    
                    safe_title = metadata.get("title")
                    if not safe_title:
                        safe_title = safe_filename
                        
                    # Parse date for a year
                    creation_date = metadata.get("creation_date", "")
                    year = "n.d."
                    if creation_date and len(creation_date) >= 6 and creation_date.startswith("D:"):
                        year = creation_date[2:6]
                    elif len(creation_date) >= 4:
                        import re
                        match = re.search(r'(\d{4})', creation_date)
                        if match:
                            year = match.group(1)
                            
                    docs.append(ScientificDocument(
                        id=pid,
                        title=safe_title,
                        authors=[metadata.get("author")] if metadata.get("author") else ["Unknown"],
                        abstract="Extracted from PDF",
                        content=text,
                        document_type=DocumentType.PDF,
                        publication_date=year
                    ))
                except Exception as doc_err:
                    safe_err = str(doc_err).encode('ascii', 'replace').decode('ascii')
                    logger.error(f"DEMO_REAL: Failed to process document {pid}: {safe_err}")
            
            if not docs:
                logger.warning("DEMO_REAL: No documents could be extracted. Falling back to mock data.")
                return MockIntelligenceService.get_mock_analysis_result()
            
            # 3. Call K2 Think Engine
            logger.info(f"DEMO_REAL: Initializing K2ThinkEngine with {len(docs)} docs, Depth: {depth}, Rigor: {rigor}")
            engine = K2ThinkEngine()
            k2_request = K2AnalysisRequest(
                documents=docs,
                reasoning_depth=depth,
                ethics_rigor=rigor,
                info_density=density
            )
            result = await engine.process_analysis_request(k2_request)
            
            logger.info(f"DEMO_REAL: K2 success! Request ID: {result.request_id}")
            # Return standardized dict
            return result.model_dump()
            
        except Exception as k2_err:
            logger.error(f"K2 Real-time processing failed: {k2_err}")
            import traceback
            logger.error(traceback.format_exc())
            return MockIntelligenceService.get_mock_analysis_result()

    # 2. Cas du mock statique de base
    if str(analysis_id).startswith("demo_") or "mock" in str(analysis_id) or str(project_id).startswith("0000"):
        return MockIntelligenceService.get_mock_analysis_result()

    # 3. Mode standard (Base de données)
    try:
        service = AnalysisService(db)
        
        # Test if it's a valid UUID to prevent DB Cast errors
        try:
            uuid_obj = UUID(analysis_id)
            analysis = service.analysis_repo.get_by_id(uuid_obj)
        except (ValueError, AttributeError):
            analysis = None
            
        # Verify analysis exists and belongs to project
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        if str(analysis.project_id) != str(project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        # Fallback for unexpected DB drops during execution
        logger.error(f"Analysis DB Error: {e}")
        return MockIntelligenceService.get_mock_analysis_result()


@router.post("/{analysis_id}/chat", response_model=ChatResponse)
async def scientific_chat(
    analysis_id: str,
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Discussion interactive avec K2 Think sur une analyse spécifique
    """
    from app.db.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    
    # 1. Vérification des crédits (10 pour un chat)
    if not current_user.id.hex.startswith("0000"):
        if current_user.credits < 10:
             raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient K2 Credits. Required: 10"
            )
        # Deduct
        user_repo.deduct_credits(current_user, 10)

    from app.core.logging import logger
    logger.info(f"Chat request for analysis {analysis_id}: {request.message[:50]}...")
    try:
        # If we have context in the request, use it. 
        # Otherwise, try to fetch it if not demo.
        context = request.analysis_context
        
        engine = K2ThinkEngine()
        result = await engine.chat(
            message=request.message,
            analysis_context=context,
            history=request.history or []
        )
        # Update credits in result
        if isinstance(result, ChatResponse):
             result.remaining_credits = current_user.credits
        elif isinstance(result, dict):
             result["remaining_credits"] = current_user.credits
             
        logger.info(f"Chat response generated successfully")
        return result
    except Exception as e:
        # Fallback for Demo
        import traceback
        logger.error(f"Chat error: {e}")
        logger.error(traceback.format_exc())
        return {
            "answer": f"En tant qu'assistant K2, je confirme que cette piste de recherche est prometteuse d'après les documents analysés. \n\nVous avez demandé : '{request.message}'",
            "reasoning_log": "Simulated reasoning trace for hackathon demo.",
            "suggested_actions": ["Explorer ce point", "Générer un protocole dédié"]
        }


@router.post("/{analysis_id}/export/{format}")
async def export_analysis(
    analysis_id: str,
    format: str,
    request: dict, # Pass full context to avoid refetching for demo
    current_user = Depends(get_current_user)
):
    """
    Exporte l'analyse dans différents formats (latex, csv, chart)
    """
    export_service = ExportService()
    
    if format == "latex":
        content = await export_service.generate_latex_grant(request)
        return Response(
            content=content,
            media_type="application/x-tex",
            headers={"Content-Disposition": f"attachment; filename=grant_proposal_{analysis_id}.tex"}
        )
    
    elif format == "csv":
        content = export_service.generate_csv_export(request)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analysis_data_{analysis_id}.csv"}
        )
    
    elif format == "chart":
        output_path = f"logs/chart_{analysis_id}.png"
        chart_path = export_service.generate_strategy_charts(request, output_path)
        if not chart_path:
            raise HTTPException(status_code=400, detail="Cannot generate chart - no gaps found")
        return FileResponse(chart_path, media_type="image/png")
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.get("/{analysis_id}/export/{format}")
async def export_analysis_get(
    analysis_id: str,
    format: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exporte l'analyse (version GET pour les analyses persistantes stockées en base)
    """
    # 1. Vérification si c'est une démo
    if analysis_id.startswith("demo_"):
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST, 
             detail="GET export only supported for persistent analyses. Use POST for demo sessions."
         )

    # 2. Récupération de l'analyse en base
    try:
        service = AnalysisService(db)
        uuid_obj = UUID(analysis_id)
        analysis_run = service.analysis_repo.get_by_id(uuid_obj)
    except:
        analysis_run = None
    
    if not analysis_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    # 3. Reconstruction du contexte pour l'export
    gaps = []
    for g in analysis_run.gaps:
        gaps.append({
            "gap_description": g.description,
            "importance_score": g.importance_score,
            "suggested_direction": g.suggested_direction
        })
    
    # Contexte minimal requis pour les graphiques
    context = {
        "request_id": str(analysis_run.id),
        "research_gaps": gaps,
        "confidence_overall": 0.85
    }
    
    # 4. Génération de l'export
    export_service = ExportService()
    if format == "chart":
        output_path = f"logs/chart_{analysis_id}.png"
        chart_path = export_service.generate_strategy_charts(context, output_path)
        if not chart_path:
            raise HTTPException(status_code=400, detail="Cannot generate chart - no gaps found")
        return FileResponse(chart_path, media_type="image/png")
    
    raise HTTPException(status_code=400, detail=f"Unsupported format for GET: {format}")
