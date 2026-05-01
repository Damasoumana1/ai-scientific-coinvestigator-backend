"""
K2 Think Engine - Modèle d'IA Principal Unique
Hackathon: K2 Think API est le seul moteur d'IA du projet
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import re
import traceback
from app.models.schemas import (
    ScientificDocument, AnalysisResult, AnalysisRequest, AuditLog,
    ComparativeAnalysis, ExperimentalProtocol, ResearchGap, CounterHypothesis,
    ExperimentalStep, ExperimentalVariable, DocumentType
)
from app.reasoning.k2_client import K2ThinkClient
from app.core.settings import settings
from app.core.logging import logger
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


class K2ThinkEngine:
    """
    Moteur K2 Think - IA Principal Unique
    Toutes les analyses passent par l'API K2 Think exclusivement
    """
    
    def __init__(self):
        if not settings.K2_THINK_API_KEY:
            raise ValueError("K2_THINK_API_KEY must be configured in .env")
        
        self.k2_client = K2ThinkClient(
            api_key=settings.K2_THINK_API_KEY,
            api_url=settings.K2_THINK_API_URL
        )
        logger.info(f"K2 Think Engine initialized - UNIQUE AI MODEL for this hackathon")
        logger.info(f"   API URL: {settings.K2_THINK_API_URL}")
        
        self.audit_logs: List[AuditLog] = []
        self.reasoning_trace: List[Dict[str, Any]] = []
        
        from app.services.memory_service import MemoryService
        self.memory_service = MemoryService()
    
    async def process_analysis_request(
        self,
        request: AnalysisRequest
    ) -> AnalysisResult:
        """
        Processus complet d'analyse utilisant LangChain + K2 Think API
        """
        request_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.reasoning_trace = []
        self.audit_logs = []
        
        try:
            logger.info(f"K2 Think Analysis (LangChain Orchestrated) Start: {request_id}")
            
            # 1. Préparation du contexte documentaire
            context_parts = []
            for doc in request.documents:
                snippet = doc.content[:6000] # Limite pour économiser les tokens
                first_author = doc.authors[0].split()[-1] if doc.authors else "Unknown"
                year = "n.d."
                citation_key = f"({first_author}, {year})"
                context_parts.append(f"--- DOCUMENT: {doc.title} | KEY: {citation_key} ---\n{snippet}")
            context = "\n\n".join(context_parts)

            # 2. Prompt (Optimisé pour K2-Think-v2)
            instruction_prompt = f"""You are a senior scientific investigator. Analyze the provided research documents and produce a detailed comparative analysis.

[DOCUMENTS]
{context}

[YOUR TASK]
1. Synthesize findings across all documents.
2. Identify divergences, contradictions, and gaps.
3. Propose a new experimental protocol.

[FORMATTING RULES]
- Output ONLY a valid JSON object.
- NO preamble, NO explanations before or after JSON.
- NO single quotes in the JSON keys or values.
- Use valid citations e.g. (Author, Year).

[JSON SCHEMA]
{{
  "reasoning_summary": "Extensive 200+ word technical summary of findings",
  "confidence_overall": 0.95,
  "comparative_analysis": {{
    "document_ids": {json.dumps([doc.id for doc in request.documents])},
    "divergences": [
      {{ "variable": "name", "finding_a": "...", "finding_b": "...", "impact": "..." }}
    ],
    "contradictions": [
      {{ "topic": "name", "conflict": "...", "resolution_path": "..." }}
    ],
    "common_findings": ["Finding 1", "Finding 2"],
    "research_gaps": ["Gap 1", "Gap 2"],
    "confidence_score": 0.9
  }},
  "research_gaps": [],
  "counter_hypotheses": [
    {{ "hypothesis": "...", "rationale": "...", "potential_bias": "...", "validation_experiment": "...", "confidence_against": 0.5 }}
  ],
  "proposed_protocol": {{
    "title": "...",
    "objective": "...",
    "steps": [
       {{ "description": "...", "duration_hours": 1, "materials": [], "critical_parameters": [] }}
    ]
  }},
  "strategic_recommendations": [],
  "reasoning_trace": "Internal logic summary",
  "confidence_overall": 0.95
}}

[FINAL INSTRUCTION]
Start directly with <think> if needed, then output the JSON inside [RESULT] tags.
"""

            # 3. Appel au modèle
            chat = ChatOpenAI(
                model="MBZUAI-IFM/K2-Think-v2",
                openai_api_key=settings.K2_THINK_API_KEY,
                openai_api_base=settings.K2_THINK_API_URL,
                temperature=0.1,
                max_tokens=16000,
                timeout=400,
                max_retries=2 
            )

            logger.info("Sending request to K2 Think...")
            response = await chat.ainvoke([HumanMessage(content=instruction_prompt)])
            raw_content = response.content
            logger.info(f"Raw K2 response length: {len(raw_content)}")

            # 4. Extraction du JSON
            clean_json = ""
            
            # Nettoyage des balises de pensée
            processed_content = raw_content
            if "<think>" in processed_content and "</think>" in processed_content:
                processed_content = re.sub(r'<think>.*?</think>', '', processed_content, flags=re.DOTALL)
            elif "<think>" in processed_content:
                processed_content = re.sub(r'<think>.*', '', processed_content, flags=re.DOTALL)

            # Recherche de bloc JSON
            # a) Balises [RESULT]
            result_match = re.search(r'\[RESULT\]\s*(.*)', processed_content, re.DOTALL | re.IGNORECASE)
            if result_match:
                candidate = result_match.group(1).strip()
                json_inner = re.search(r'(\{.*\})', candidate, re.DOTALL)
                if json_inner:
                    clean_json = json_inner.group(1).strip()

            # b) Blocs Markdown
            if not clean_json:
                json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', processed_content, re.DOTALL)
                if json_block_match:
                    clean_json = json_block_match.group(1).strip()

            # c) Accolades les plus larges
            if not clean_json:
                start_idx = processed_content.find('{')
                end_idx = processed_content.rfind('}')
                if start_idx != -1:
                    if end_idx != -1 and end_idx > start_idx:
                        clean_json = processed_content[start_idx:end_idx + 1]
                    else:
                        clean_json = processed_content[start_idx:] # Tronqué

            # 5. Parsing et Réparation
            k2_analysis = None
            if clean_json:
                try:
                    # Tentative 1: Standard
                    k2_analysis = json.loads(clean_json)
                except json.JSONDecodeError:
                    # Tentative 2: Réparation (Fermeture des balises)
                    logger.warning("JSON parsing failed, attempting auto-repair...")
                    repaired = clean_json.strip()
                    open_braces = repaired.count('{')
                    close_braces = repaired.count('}')
                    open_brackets = repaired.count('[')
                    close_brackets = repaired.count(']')
                    while open_brackets > close_brackets:
                        repaired += ']'
                        close_brackets += 1
                    while open_braces > close_braces:
                        repaired += '}'
                        close_braces += 1
                    
                    try:
                        k2_analysis = json.loads(repaired)
                        logger.info("JSON parsing successful after repair")
                    except Exception as e:
                        logger.error(f"Auto-repair failed: {e}")

            # 6. Fallback en cas d'échec total de parsing
            if not k2_analysis:
                logger.error("All JSON parsing attempts failed. Creating technical fallback.")
                self._log_reasoning("ERROR", "Parsing", f"Raw content snippet: {raw_content[:1000]}...")
                k2_analysis = {
                    "reasoning_summary": f"ERREUR DE PARSING. Voici le début de la réponse brute : {raw_content[:1000]}...",
                    "confidence_overall": 0.1,
                    "comparative_analysis": {
                        "document_ids": [doc.id for doc in request.documents],
                        "divergences": [],
                        "contradictions": [],
                        "common_findings": ["Échec de l'extraction structurée"],
                        "research_gaps": [],
                        "confidence_score": 0.1
                    },
                    "proposed_protocol": {
                        "title": "Analyse échouée - Révision manuelle requise",
                        "objective": "Extraire manuellement les données des logs",
                        "steps": []
                    },
                    "recommendations": ["Réessayez l'analyse", "Vérifiez les documents sources"]
                }

            # 7. Conversion en objets schemas.py
            comp_analysis = self._convert_k2_to_comparative_analysis(k2_analysis, request.documents)
            hypotheses = self._convert_k2_to_counter_hypotheses(k2_analysis)
            protocol = await self._convert_k2_to_protocol(k2_analysis)
            
            result = AnalysisResult(
                request_id=request_id,
                documents_analyzed=len(request.documents),
                reasoning_summary=k2_analysis.get("reasoning_summary", "Analysis completed."),
                comparative_analysis=comp_analysis,
                research_gaps=comp_analysis.research_gaps,
                counter_hypotheses=hypotheses,
                proposed_protocol=protocol,
                strategic_recommendations=k2_analysis.get("recommendations", k2_analysis.get("strategic_recommendations", [])),
                reasoning_trace=self.reasoning_trace,
                confidence_overall=k2_analysis.get("confidence_overall", 0.85)
            )

            # 8. Mémoire sémantique
            if request.user_id:
                try:
                    await self.memory_service.consolidate_analysis(
                        user_id=request.user_id,
                        project_id="auto_consolidation",
                        analysis_result=result
                    )
                except Exception as mem_err:
                    logger.error(f"Memory consolidation failed: {mem_err}")

            return result

        except Exception as e:
            logger.error(f"FATAL K2 Engine Error: {str(e)}")
            traceback.print_exc()
            raise e

    def _convert_k2_to_comparative_analysis(
        self,
        k2_result: Dict[str, Any],
        docs: List[ScientificDocument]
    ) -> ComparativeAnalysis:
        raw_comp = k2_result.get("comparative_analysis", {})
        if not isinstance(raw_comp, dict): raw_comp = {}
        
        gaps = []
        raw_gaps = k2_result.get("research_gaps", raw_comp.get("research_gaps", []))
        for gap in raw_gaps:
            if isinstance(gap, dict):
                gaps.append(ResearchGap(
                    gap_description=gap.get("description", "Gap"),
                    importance_score=gap.get("importance_score", 0.5),
                    related_variables=gap.get("related_variables", []),
                    suggested_investigation=gap.get("suggested_investigation", "TBD"),
                    source_documents=[doc.id for doc in docs],
                    citations=gap.get("citations", [])
                ))
            else:
                gaps.append(ResearchGap(gap_description=str(gap), source_documents=[doc.id for doc in docs]))

        return ComparativeAnalysis(
            document_ids=[doc.id for doc in docs],
            divergences=raw_comp.get("divergences", []),
            contradictions=raw_comp.get("contradictions", []),
            common_findings=raw_comp.get("common_findings", []),
            research_gaps=gaps,
            confidence_score=raw_comp.get("confidence_score", 0.8)
        )

    def _convert_k2_to_counter_hypotheses(
        self,
        k2_result: Dict[str, Any]
    ) -> List[CounterHypothesis]:
        hypotheses = []
        for h in k2_result.get("counter_hypotheses", []):
            if isinstance(h, dict):
                hypotheses.append(CounterHypothesis(
                    hypothesis=h.get("hypothesis", "Hypothesis"),
                    rationale=h.get("rationale", ""),
                    potential_bias=h.get("potential_bias", ""),
                    validation_experiment=h.get("validation_experiment", ""),
                    confidence_against=h.get("confidence_against", 0.5)
                ))
        return hypotheses

    async def _convert_k2_to_protocol(
        self,
        k2_result: Dict[str, Any]
    ) -> ExperimentalProtocol:
        proto_data = k2_result.get("proposed_protocol", k2_result.get("protocol", {}))
        if not isinstance(proto_data, dict): proto_data = {}
        
        steps = []
        for i, s in enumerate(proto_data.get("steps", []), 1):
            if isinstance(s, dict):
                steps.append(ExperimentalStep(
                    step_number=i,
                    description=s.get("description", f"Step {i}"),
                    duration_hours=float(s.get("duration_hours", 1)),
                    materials=s.get("materials", []),
                    critical_parameters=s.get("critical_parameters", [])
                ))

        return ExperimentalProtocol(
            title=proto_data.get("title", "New Protocol"),
            objective=proto_data.get("objective", "Objective"),
            steps=steps,
            hypothesis=proto_data.get("hypothesis", "TBD"),
            expected_outcomes=proto_data.get("expected_outcomes", "TBD")
        )

    def _log_reasoning(self, phase: str, step: str, description: str):
        self.reasoning_trace.append({
            "phase": phase, "step": step, "description": description, "timestamp": datetime.now().isoformat()
        })
        logger.debug(f"[{phase}] {step}: {description}")

    async def chat(self, message: str, analysis_context: Optional[Dict[str, Any]] = None, history: List[Dict[str, str]] = [], user_id: Optional[str] = None) -> Dict[str, Any]:
        # Minimal chat implementation for K2
        llm = ChatOpenAI(model="MBZUAI-IFM/K2-Think-v2", openai_api_key=settings.K2_THINK_API_KEY, openai_api_base=settings.K2_THINK_API_URL)
        resp = await llm.ainvoke([HumanMessage(content=message)])
        return {"answer": resp.content, "reasoning_log": "", "suggested_actions": []}
