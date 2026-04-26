"""
K2 Think Engine - Modèle d'IA Principal Unique
Hackathon: K2 Think API est le seul moteur d'IA du projet
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import (
    ScientificDocument, AnalysisResult, AnalysisRequest, AuditLog,
    ComparativeAnalysis, ExperimentalProtocol, ResearchGap, CounterHypothesis,
    ExperimentalStep, ExperimentalVariable, DocumentType
)
from app.reasoning.k2_client import K2ThinkClient
from app.core.settings import settings
from app.core.logging import logger
import json


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
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        
        request_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.reasoning_trace = []
        self.audit_logs = []
        
        try:
            logger.info(f"K2 Think Analysis (LangChain Orchestrated) Start: {request_id}")
            
            # 1. Configuration du LLM K2 via l'interface OpenAI de LangChain
            llm = ChatOpenAI(
                model="MBZUAI-IFM/K2-Think-v2",
                openai_api_key=settings.K2_THINK_API_KEY,
                openai_api_base=settings.K2_THINK_API_URL,
                temperature=0.7,
                max_tokens=4096,
                max_retries=3 
            )

            # 2. Préparation du contexte documentaire
            context_parts = []
            for doc in request.documents:
                snippet = doc.content[:30000]
                first_author = doc.authors[0].split()[-1] if doc.authors else "Unknown"
                year = "n.d."
                citation_key = f"({first_author}, {year})"
                context_parts.append(f"--- DOCUMENT: {doc.title} | KEY: {citation_key} ---\n{snippet}")
            context = "\n\n".join(context_parts)

            # 3. Récupération de la mémoire sémantique
            past_context = ""
            if request.user_id:
                query = f"Research regarding: {', '.join([d.title for d in request.documents[:2]])}"
                memories = await self.memory_service.search_memory(request.user_id, query)
                if memories:
                    past_context = "\n- ".join(memories)

            # 4. Définition du Prompt Système
            system_template = """You are the K2 Think V2 Scientific Co-Investigator.
Your primary directive is MULTI-DOCUMENT REASONING and KNOWLEDGE SYNTHESIS.

IMPORTANT: Your internal reasoning (thoughts) should be contained within <think></think> tags. 
However, your FINAL output MUST be a single, valid JSON object and NOTHING else. 
Do not include conversational filler outside the JSON.

PAST RESEARCH CONTEXT:
{past_context}

RESEARCHER PROFILE:
{user_profile}
"""
            
            # Re-ajouter les instructions de formatage spécifiques au JsonOutputParser
            system_template += "\n{format_instructions}\n"
            
            parser = JsonOutputParser()
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                ("user", "Analyze these documents and provide results:\n\n{context}")
            ])

            # 5. Exécution de la chaîne (on enlève le parser ici pour nettoyer manuellement après)
            chain = prompt | llm
            
            self._log_reasoning("K2_ANALYSIS", "Chain Execution", "Invoking LangChain LCEL with K2 Think V2")
            
            response = await chain.ainvoke({
                "past_context": past_context or "No past context.",
                "user_profile": request.user_profile or "General researcher.",
                "depth": request.reasoning_depth,
                "ethics": request.ethics_rigor,
                "density": request.info_density,
                "format_instructions": parser.get_format_instructions(),
                "context": context
            })

            # NETTOYAGE MANUEL DU JSON (Crucial pour les modèles "Thinking")
            raw_content = response.content
            
            # Supprimer les balises de réflexion (<think>, <think_faster>, etc.)
            import re
            content_no_think = re.sub(r'<think.*?>.*?</think.*?>', '', raw_content, flags=re.DOTALL).strip()
            
            # Extraction chirurgicale du bloc JSON
            # On cherche le PREMIER '{' et le DERNIER '}'
            start_idx = content_no_think.find('{')
            end_idx = content_no_think.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_json = content_no_think[start_idx:end_idx + 1]
            else:
                clean_json = content_no_think.replace("```json", "").replace("```", "").strip()

            # Parser le JSON nettoyé
            try:
                # On utilise un parseur de LangChain qui gère mieux les petits défauts
                from langchain_core.utils.json import parse_json_markdown
                k2_analysis = parse_json_markdown(clean_json)
            except Exception as e:
                logger.error(f"Failed to parse cleaned JSON: {e}")
                logger.debug(f"Cleaned JSON was: {clean_json}")
                raise e

            # 6. Conversion en schémas internes
            comparative_analysis = self._convert_k2_to_comparative_analysis(k2_analysis, request.documents)
            counter_hypotheses = self._convert_k2_to_counter_hypotheses(k2_analysis)
            protocol = await self._convert_k2_to_protocol(k2_analysis)
            
            result = AnalysisResult(
                request_id=request_id,
                documents_analyzed=len(request.documents),
                reasoning_summary=k2_analysis.get("reasoning_summary", "Analysis completed."),
                comparative_analysis=comparative_analysis,
                research_gaps=comparative_analysis.research_gaps,
                counter_hypotheses=counter_hypotheses,
                proposed_protocol=protocol,
                strategic_recommendations=k2_analysis.get("recommendations", []),
                reasoning_trace=self.reasoning_trace,
                confidence_overall=k2_analysis.get("confidence_score", 0.85)
            )

            # 7. Consolidation de la mémoire
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
            logger.error(f"K2 Think Analysis (LangChain) Failed: {str(e)}")
            self._log_reasoning("ERROR", "Analysis Failure", str(e))
            raise e

    async def chat(
        self,
        message: str,
        analysis_context: Optional[Dict[str, Any]] = None,
        history: List[Dict[str, str]] = [],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discussion interactive avec K2 Think sur l'analyse via LangChain
        """
        from langchain_openai import ChatOpenAI
        from langchain.schema import SystemMessage, HumanMessage, AIMessage
        
        system_prompt = f"""You are the K2 Think V2 Scientific Assistant. 
You are discussing a specific scientific analysis with a researcher.
CONTEXT OF ANALYSIS:
{json.dumps(analysis_context, indent=2) if analysis_context else "No specific context provided yet."}

Your goal:
1. Answer questions about the contradictions, gaps, or protocols found.
2. Provide deeper scientific insights based on the documents.
3. Help design further investigations.

Keep your tone professional, strategic, and scientifically rigorous.
"""
        # ============ LONG-TERM SEMANTIC MEMORY (CHAT) ============
        if user_id:
            memories = await self.memory_service.search_memory(user_id, message)
            if memories:
                memories_text = "\n- ".join(memories)
                system_prompt += f"\n\nPAST USER CONTEXT (Relevant to this query):\n- {memories_text}"

        llm = ChatOpenAI(
            model="MBZUAI-IFM/K2-Think-v2",
            openai_api_key=settings.K2_THINK_API_KEY,
            openai_api_base=settings.K2_THINK_API_URL,
            temperature=0.7
        )

        messages = [SystemMessage(content=system_prompt)]
        
        # Add history
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
            
        # Add current message
        messages.append(HumanMessage(content=message))
        
        response = await llm.ainvoke(messages)
        content = response.content
        
        # Handle reasoning if present
        reasoning = ""
        if "</think>" in content:
            parts = content.split("</think>")
            reasoning = parts[0].replace("<think>", "").strip()
            content = parts[-1].strip()
            
        return {
            "answer": content,
            "reasoning_log": reasoning,
            "suggested_actions": ["Design further experiments", "Explore related papers", "Stress test this hypothesis"]
        }
    
    def _convert_k2_to_comparative_analysis(
        self,
        k2_result: Dict[str, Any],
        docs: List[ScientificDocument]
    ) -> ComparativeAnalysis:
        """Convertit résultats K2 Think en ComparativeAnalysis"""
        
        # Extraire research gaps depuis K2
        research_gaps = []
        for gap in k2_result.get("research_gaps", []):
            research_gaps.append(ResearchGap(
                gap_description=gap.get("description", "Research gap"),
                importance_score=gap.get("importance_score", 0.5),
                related_variables=gap.get("related_variables", []),
                suggested_investigation=gap.get("suggested_investigation", "Further research needed"),
                source_documents=gap.get("source_documents", [doc.id for doc in docs]),
                citations=gap.get("citations", [])
            ))
        
        return ComparativeAnalysis(
            document_ids=[doc.id for doc in docs],
            divergences=k2_result.get("divergences", []),
            contradictions=k2_result.get("contradictions", []),
            common_findings=k2_result.get("common_findings", []),
            research_gaps=research_gaps,
            confidence_score=k2_result.get("confidence_score", 0.8)
        )
    
    def _convert_k2_to_counter_hypotheses(
        self,
        k2_result: Dict[str, Any]
    ) -> List[CounterHypothesis]:
        """Convertit résultats K2 Think en CounterHypotheses"""
        
        counter_hypotheses = []
        for counter in k2_result.get("counter_hypotheses", []):
            counter_hypotheses.append(CounterHypothesis(
                hypothesis=counter.get("hypothesis", "Alternative hypothesis"),
                rationale=counter.get("rationale", "Based on K2 Think analysis"),
                potential_bias=counter.get("potential_bias", "Identified by K2 Think"),
                validation_experiment=counter.get("validation_experiment", "Empirical validation recommended"),
                confidence_against=counter.get("confidence_against", 0.5),
                citations=counter.get("citations", [])
            ))
        
        return counter_hypotheses
    
    async def _convert_k2_to_protocol(
        self,
        k2_result: Dict[str, Any]
    ) -> ExperimentalProtocol:
        """Convertit résultats K2 Think en ExperimentalProtocol complet"""
        
        protocol_data = k2_result.get("protocol", {})
        
        # Construire les étapes
        steps = []
        for i, step_data in enumerate(protocol_data.get("steps", []), 1):
            steps.append(ExperimentalStep(
                step_number=i,
                description=step_data.get("description", f"Step {i}"),
                duration_hours=step_data.get("duration_hours"),
                materials=step_data.get("materials", []),
                critical_parameters=step_data.get("critical_parameters", []),
                validation_criteria=step_data.get("validation_criteria", "Protocol requirements"),
                risk_level=step_data.get("risk_level", "medium"),
                contingency_plan=step_data.get("contingency_plan")
            ))
        
        # Construire les variables
        variables = []
        for var_data in protocol_data.get("variables", []):
            variables.append(ExperimentalVariable(
                name=var_data.get("name", "Variable"),
                type=var_data.get("type", "independent"),
                measurement_unit=var_data.get("measurement_unit"),
                measurement_method=var_data.get("measurement_method", "TBD"),
                possible_values=var_data.get("possible_values")
            ))
        
        # Robust parsing for duration and budget
        def parse_float(val, default):
            if val is None: return default
            if isinstance(val, (int, float)): return float(val)
            try:
                cleaned = str(val).replace('$', '').replace(',', '').replace(' ', '')
                import re
                match = re.search(r"[-+]?\d*\.\d+|\d+", cleaned)
                if match:
                    return float(match.group())
                return default
            except:
                return default

        return ExperimentalProtocol(
            title=protocol_data.get("title", "K2 Think Generated Protocol"),
            hypothesis=protocol_data.get("hypothesis", "To be determined"),
            objective=protocol_data.get("objective", "Research objective"),
            variables=variables,
            steps=steps,
            expected_outcomes=protocol_data.get("expected_outcomes", "To be evaluated"),
            statistical_analysis_plan=protocol_data.get("statistical_analysis_plan", "TBD"),
            success_criteria=protocol_data.get("success_criteria", ["Protocol completed as designed"]),
            estimated_duration_days=parse_float(protocol_data.get("estimated_duration_days"), 30.0),
            estimated_budget_usd=parse_float(protocol_data.get("estimated_budget_usd"), None),
            resource_optimization=protocol_data.get("resource_optimization"),
            material_constraints=protocol_data.get("material_constraints"),
            alternative_approaches=protocol_data.get("alternative_approaches", []),
            risk_assessment=protocol_data.get("risk_assessment", {})
        )
    
    def _log_reasoning(
        self,
        phase: str,
        step: str,
        description: str
    ) -> None:
        """Enregistre trace de raisonnement pour transparence"""
        entry = {
            "phase": phase,
            "step": step,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        self.reasoning_trace.append(entry)
        logger.debug(f"[{phase}] {step}: {description}")
    
    def _add_audit_log(
        self,
        action: str,
        decision: str,
        reasoning: str
    ) -> None:
        """Ajoute entrée au journal d'audit"""
        log = AuditLog(
            timestamp=datetime.now().isoformat(),
            step=action,
            decision=decision,
            reasoning=reasoning,
            model_used="K2_Think_API"
        )
        self.audit_logs.append(log)
