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
    
    async def process_analysis_request(
        self,
        request: AnalysisRequest
    ) -> AnalysisResult:
        """
        Processus complet d'analyse utilisant UNIQUEMENT K2 Think API (Chat Completion)
        """
        import json
        request_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.reasoning_trace = []
        self.audit_logs = []
        
        try:
            logger.info(f"K2 Think Analysis Start: {request_id}")
            logger.info(f"   Documents: {len(request.documents)}")
            
            # Préparer le contexte documentaire avec troncature pour éviter les erreurs 500 (limite de tokens API)
            max_chars_per_doc = 40000 # environ 10k tokens par doc
            context_parts = []
            for doc in request.documents:
                snippet = doc.content[:max_chars_per_doc]
                if len(doc.content) > max_chars_per_doc:
                    snippet += "\n...[CONTENT TRUNCATED FOR API LIMITS]..."
                
                # Extract first author and year for citation baseline
                first_author = doc.authors[0].split()[-1] if doc.authors else "Unknown"
                
                year = "n.d."
                if doc.publication_date:
                    import re
                    year_match = re.search(r'(\d{4})', doc.publication_date)
                    if year_match:
                        year = year_match.group(1)
                
                citation_key = f"({first_author}, {year})"
                
                context_parts.append(f"--- DOCUMENT: {doc.title} | CITATION_KEY: {citation_key} ---\n{snippet}")
            context = "\n\n".join(context_parts)
            
            # ============ K2 THINK API - ANALYSE COMPLÈTE ============
            self._log_reasoning(
                "K2_ANALYSIS",
                "K2 Think Deep Reasoning",
                f"Sending {len(request.documents)} documents to K2 Think V2 for multi-step reasoning"
            )
            
            # Dynamic prompt adjustments based on user settings
            depth_instruction = ""
            if request.reasoning_depth == "exhaustive":
                depth_instruction = "\n- EXHAUSTIVE MODE: Perform a deep methodological audit. Analyze every statistical nuance and minor contradiction."
            else:
                depth_instruction = "\n- EXECUTIVE MODE: Focus on high-level strategic outcomes and clear, actionable summaries."

            ethics_instruction = ""
            if request.ethics_rigor == "clinical":
                ethics_instruction = "\n- CLINICAL RIGOR: Apply maximum clinical safety standards. Audit protocols for patient consent and bio-data anonymization."
            elif request.ethics_rigor == "strict":
                ethics_instruction = "\n- STRICT RIGOR: Enforce extreme academic integrity and data privacy. Flag any potential citation or data handling bias."

                ethics_instruction = "STRICT PRIVACY AUDIT: Identify any potential data anonymization failures or strict regulatory compliance issues."

            density_instruction = "Use compact, dense bullet points." if request.info_density == "compact" else "Use comfortable, explanatory paragraphs where needed."

            system_prompt = f"""You are the K2 Think V2 Scientific Co-Investigator. 
Your core capability and primary directive is MULTI-DOCUMENT REASONING and KNOWLEDGE SYNTHESIS.
Do NOT just summarize individual papers. You MUST cross-reference, compare, and contrast the provided documents to uncover deeper strategic insights.

REASONING GUIDELINES:
- DEPTH: {depth_instruction}
- ETHICS: {ethics_instruction}
- DENSITY: {density_instruction}

MANDATORY CITATION RULE: Every claim, contradiction, or gap you identify MUST be attributed to its source using the exact (Author, Year) format as provided in the DOCUMENT header CITATION_KEY.

Analyze the provided documents to formulate a comprehensive research strategy:
1. METHODOLOGICAL COMPARISON: Explicitly compare how different documents approach the same problem (e.g., Paper A uses X, Paper B uses Y).
2. SCIENTIFIC CONTRADICTIONS: Identify exact points where the documents disagree on findings, variables, or conclusions. Explain the conflict.
3. RESEARCH GAPS & SYNTHESIS: Find the "white space" between the papers. What did none of them evaluate? What new hybrid approach could be taken?
4. HYPOTHESIS STRESS TESTER: Generate counter-hypotheses based on biases or limitations observed *across* the methodology of the combined papers.
5. RESOURCE-OPTIMIZED EXPERIMENTAL PROTOCOL: Design a *net-new* experiment specifically engineered to resolve the contradictions or fill the gaps you just found. 
   CRITICAL: Optimize the protocol for modern resource constraints (e.g., Budget, Time, Hardware like NVIDIA GPUs).
6. REASONING TRACE: Show your chain of thought (e.g., "Compared metric X from Doc 1 with Doc 2 -> Found contradiction -> Designed Step 3 to resolve").

OUTPUT FORMAT: You MUST respond ONLY with a valid JSON object matching this structure:
{{
  "confidence_score": 0.95,
  "reasoning_summary": "Summary of steps taken...",
  "contradictions": [{{ "topic": "...", "conflict": "...", "resolution_path": "...", "citations": ["(Author, Year)"] }}],
  "research_gaps": [{{ "description": "...", "importance_score": 0.9, "related_variables": ["...", "..."], "suggested_investigation": "...", "citations": ["(Author, Year)"] }}],
  "counter_hypotheses": [{{ "hypothesis": "...", "rationale": "...", "potential_bias": "...", "validation_experiment": "...", "citations": ["(Author, Year)"] }}],
  "protocol": {{
    "title": "...",
    "hypothesis": "...",
    "objective": "...",
    "estimated_duration_days": 30,
    "estimated_budget_usd": 5000,
    "resource_optimization": "...",
    "steps": [{{ "description": "...", "duration_hours": 2, "materials": ["..."], "risk_level": "low" }}],
    "variables": [{{ "name": "...", "type": "independent|dependent|control", "measurement_unit": "..." }}]
  }},
  "recommendations": ["Recommendation 1"]
}}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze these documents and provide results in JSON:\n\n{context}"}
            ]
            
            # Appel K2 Think
            response = await self.k2_client.chat_completion(messages=messages)
            
            # Extraction robuste du JSON
            content = response['choices'][0]['message']['content']
            
            # 1. Supprimer le bloc <think>...</think> ou le tag </think> s'ils existent
            if "</think>" in content:
                content = content.split("</think>")[-1].strip()
            
            # 2. Extraire le bloc JSON (entre ```json et ``` ou par les premières/dernières accolades)
            import re
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            elif "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            k2_analysis = json.loads(content)
            
            logger.info(f"K2 Think reasoning completed and parsed")
            self._add_audit_log(
                "k2_reasoning_completion",
                "K2 Think V2 multi-doc analysis",
                f"Successfully parsed JSON results from K2 API"
            )
            
            # ============ CONVERSION K2 RESULTS -> SCHEMAS ============
            comparative_analysis = self._convert_k2_to_comparative_analysis(
                k2_analysis, request.documents
            )
            
            counter_hypotheses = self._convert_k2_to_counter_hypotheses(k2_analysis)
            
            protocol = await self._convert_k2_to_protocol(k2_analysis)
            
            research_gaps = comparative_analysis.research_gaps
            
            # ============ SYNTHÈSE FINALE ============
            result = AnalysisResult(
                request_id=request_id,
                documents_analyzed=len(request.documents),
                reasoning_summary=k2_analysis.get("reasoning_summary"),
                comparative_analysis=comparative_analysis,
                research_gaps=research_gaps,
                counter_hypotheses=counter_hypotheses,
                proposed_protocol=protocol,
                strategic_recommendations=k2_analysis.get("recommendations", []),
                reasoning_trace=self.reasoning_trace,
                confidence_overall=k2_analysis.get("confidence_score", 0.8)
            )
            
            self._log_reasoning(
                "COMPLETION",
                "Analysis Complete",
                f"K2 Think analysis finished with confidence: {result.confidence_overall:.1%}"
            )
            
            logger.info(f"Analysis {request_id} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"K2 Think Analysis Failed: {str(e)}")
            self._log_reasoning(
                "ERROR",
                "K2 Think Analysis Failed",
                str(e)
            )
    async def chat(
        self,
        message: str,
        analysis_context: Optional[Dict[str, Any]] = None,
        history: List[Dict[str, str]] = []
    ) -> Dict[str, Any]:
        """
        Discussion interactive avec K2 Think sur l'analyse
        """
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
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history
        for msg in history:
            messages.append(msg)
            
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = await self.k2_client.chat_completion(messages=messages)
        content = response['choices'][0]['message']['content']
        
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
                # Remove common non-numeric chars like $, commas, etc.
                cleaned = str(val).replace('$', '').replace(',', '').replace(' ', '')
                # Extract first number found
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
