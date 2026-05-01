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
                temperature=0,
                max_tokens=None,
                timeout=300,
                max_retries=3 
            )

            # 2. Préparation du contexte documentaire
            context_parts = []
            for doc in request.documents:
                snippet = doc.content[:10000]
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

            parser = JsonOutputParser()
            
            # 4. Prompt autoritaire pour éviter la paresse (Laziness) - Version améliorée
            instruction_prompt = f"""[SCIENTIFIC MISSION]
Perform an EXHAUSTIVE and DETAILED comparative analysis of the attached documents.
CRITICAL RULES:
- NEVER use placeholders like "...", "etc.", or "[TBD]".
- EVERY field in the JSON must contain at least 2-3 sentences of technical content extracted from the documents.
- Use the specific citation keys provided (e.g., (Author, Year)).
- Your output must be a single, complete, and valid JSON object exactly matching the schema below.
- You MUST populate ALL fields with complete, real text. Do NOT abbreviate the JSON output.
- NEVER write `... JSON ...` or `{{"...": "..."}}`. You must write out the full, complete JSON object.
- IMPORTANT: Use DOUBLE QUOTES for all strings and keys. Do NOT use single quotes.
- IMPORTANT: Do NOT add comments or extra text outside the JSON structure.

[DOCUMENTS TO ANALYZE]
{context}

[REQUIRED SCHEMA - COPY THIS EXACTLY]
You must return a JSON object with the following structure:
{{
  "reasoning_summary": "Detailed summary of your analysis process and key findings",
  "confidence_score": 0.85,
  "divergences": [
    {{
      "variable": "specific_variable_name",
      "finding_a": "Complete finding from document A with citation",
      "finding_b": "Complete finding from document B with citation", 
      "impact": "Detailed explanation of the scientific impact of this divergence"
    }}
  ],
  "contradictions": [
    {{
      "topic": "specific_topic_of_contradiction",
      "conflict": "Detailed description of the conflicting findings",
      "resolution_path": "Step-by-step approach to resolve this contradiction experimentally"
    }}
  ],
  "common_findings": [
    "First common finding with full explanation",
    "Second common finding with full explanation"
  ],
  "research_gaps": [
    {{
      "description": "Detailed description of the research gap identified",
      "importance_score": 0.9,
      "related_variables": ["variable1", "variable2"],
      "suggested_investigation": "Detailed experimental approach to address this gap",
      "source_documents": ["Document title or citation"],
      "citations": ["(Author, Year)"]
    }}
  ],
  "counter_hypotheses": [
    {{
      "hypothesis": "Alternative hypothesis that contradicts common findings",
      "rationale": "Scientific rationale for considering this counter hypothesis",
      "potential_bias": "Potential sources of bias in the original studies",
      "validation_experiment": "Detailed experimental design to test this hypothesis",
      "confidence_against": 0.8,
      "citations": ["(Author, Year)"]
    }}
  ],
  "protocol": {{
    "title": "Complete protocol title describing the experimental approach",
    "hypothesis": "Clear, testable hypothesis statement",
    "objective": "Specific objectives of the experimental protocol",
    "expected_outcomes": "Expected results and their scientific significance",
    "statistical_analysis_plan": "Detailed statistical analysis approach",
    "success_criteria": ["Criterion 1", "Criterion 2"],
    "estimated_duration_days": 30.0,
    "estimated_budget_usd": 10000.0,
    "resource_optimization": "Strategy for optimizing resource usage",
    "material_constraints": "Any material or equipment constraints",
    "alternative_approaches": ["Alternative method 1", "Alternative method 2"],
    "risk_assessment": {{"risk_type": "Detailed mitigation strategy"}},
    "variables": [
      {{
        "name": "variable_name",
        "type": "independent",
        "measurement_unit": "unit_of_measurement",
        "measurement_method": "Detailed measurement procedure",
        "possible_values": ["value1", "value2"]
      }}
    ],
    "steps": [
      {{
        "description": "Detailed step description with all parameters",
        "duration_hours": 2.5,
        "materials": ["Material 1", "Material 2"],
        "critical_parameters": ["Parameter 1", "Parameter 2"],
        "validation_criteria": "How to validate this step was performed correctly",
        "risk_level": "medium",
        "contingency_plan": "What to do if this step fails"
      }}
    ]
  }},
  "recommendations": [
    "First detailed recommendation for future research",
    "Second detailed recommendation for future research"
  ]
}}

[FINAL OUTPUT INSTRUCTIONS]
1. Think step-by-step inside a <think> block about your analysis. KEEP YOUR THINKING VERY CONCISE (under 1000 words) to avoid truncation.
2. After your analysis is complete, output ONLY the JSON object
3. Do NOT include any text before or after the JSON
4. Ensure the JSON is valid and parseable
5. Use double quotes for all strings and keys
6. Do not use single quotes anywhere in the JSON

[RESULT]
"""

            # 5. Appel au modèle (on met tout dans le message humain pour plus d'impact)
            chat = ChatOpenAI(
                model="MBZUAI-IFM/K2-Think-v2",
                openai_api_key=settings.K2_THINK_API_KEY,
                openai_api_base=settings.K2_THINK_API_URL,
                temperature=0.1,  # Lower temperature for more stable JSON
                max_tokens=8192,
                timeout=300,
                max_retries=3 
            )

            logger.info("Sending command-style request to K2 Think...")
            self._log_reasoning("K2_ANALYSIS", "Chain Execution", "Invoking LangChain LCEL with K2 Think V2")
            
            from langchain.schema import HumanMessage, SystemMessage
            response = await chat.ainvoke([
                SystemMessage(content="You are a precise scientific data extractor. You must analyze the documents step by step, and then provide the final output strictly in JSON format."),
                HumanMessage(content=instruction_prompt)
            ])

            # NETTOYAGE MANUEL DU JSON (Crucial pour les modèles "Thinking")
            raw_content = response.content
            
            # 5. NETTOYAGE ET RÉPARATION DU JSON (Version améliorée)
            raw_content = response.content
            import re
            import json

            logger.info(f"Raw K2 response length: {len(raw_content)}")
            logger.debug(f"Raw K2 response preview: {raw_content[:500]}...")

            # 0. STRIP OUT THINK TAGS TO PREVENT BRACE MATCHING INSIDE IT
            if "<think>" in raw_content and "</think>" in raw_content:
                raw_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL)
                logger.info("Stripped <think> block from response")
            elif "<think>" in raw_content:
                logger.warning("Found <think> but no </think>. The response was likely truncated. Attempting to extract JSON from what we have.")
                raw_content = re.sub(r'<think>.*', '', raw_content, flags=re.DOTALL)

            # 1. Tentative d'extraction via bloc markdown standard
            json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_content, re.DOTALL)
            
            if json_block_match:
                clean_json = json_block_match.group(1).strip()
                logger.info("JSON extracted from markdown block")
            else:
                # 2. Tentative d'extraction via balises [RESULT]
                result_match = re.search(r'\[RESULT\]\s*(\{.*?\})\s*$', raw_content, re.DOTALL)
                if result_match:
                    clean_json = result_match.group(1).strip()
                    logger.info("JSON extracted from [RESULT] tag")
                else:
                    # 3. Recherche du bloc JSON le plus large possible
                    start_idx = raw_content.find('{')
                    end_idx = raw_content.rfind('}')
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        clean_json = raw_content[start_idx:end_idx + 1]
                        logger.info("JSON extracted by finding outermost braces")
                    else:
                        clean_json = ""

            if not clean_json:
                logger.error(f"No JSON block found in content. Full content: {raw_content[:1000]}...")
                raise ValueError("The AI model did not return a valid scientific result block. Please try again.")

            # 4. LOG RAW CONTENT FOR DEBUGGING
            try:
                os.makedirs("logs", exist_ok=True)
                with open("logs/k2_raw_response.log", "a", encoding="utf-8") as f:
                    f.write(f"\n--- ANALYSIS {request_id} ({datetime.now().isoformat()}) ---\n")
                    f.write(raw_content)
                    f.write("\n--- END ---\n")
            except Exception as log_err:
                logger.error(f"Failed to log raw response: {log_err}")

            # 5. Nettoyage final des résidus de Markdown et erreurs LLM communes
            clean_json = clean_json.replace("```json", "").replace("```", "").strip()
            clean_json = re.sub(r'^\s*//.*$', '', clean_json, flags=re.MULTILINE)
            clean_json = re.sub(r',\s*([\]\}])', r'\1', clean_json)

            logger.info(f"Cleaned JSON length: {len(clean_json)}")
            logger.debug(f"Cleaned JSON preview: {clean_json[:200]}...")

            try:
                k2_analysis = json.loads(clean_json)
                logger.info("JSON parsing successful")
            except json.JSONDecodeError as e:
                logger.error(f"JSON.LOADS failed: {e}")
                logger.error(f"Failed JSON content: {clean_json}")

                # Tentative ultime : nettoyage avancé et correction d'erreurs courantes LLM
                try:
                    clean_json_fixed = clean_json.replace("```json", "").replace("```", "").strip()

                    # Fix single quotes around keys: {'key': ...} -> {"key": ...}
                    clean_json_fixed = re.sub(r"([{,]\s*)'([^']+)'(\s*:)", r'\1"\2"\3', clean_json_fixed)

                    # Fix unquoted keys: {key: ...} -> {"key": ...}
                    clean_json_fixed = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', clean_json_fixed)

                    # Fix trailing commas before closing braces/brackets
                    clean_json_fixed = re.sub(r',\s*(\}|\])', r'\1', clean_json_fixed)

                    logger.info("Attempting to parse with fixes applied")
                    k2_analysis = json.loads(clean_json_fixed)
                    logger.info("JSON parsing successful after fixes")

                except json.JSONDecodeError as e2:
                    logger.error(f"All JSON parsing attempts failed. Error: {e2}")
                    
                    # ULTIMATE ATTEMPT: If "Extra data", try to take only the first object
                    if "Extra data" in str(e2):
                        try:
                            import re
                            # Simple approach: find the first matching brace
                            count = 0
                            end_pos = -1
                            for i, char in enumerate(clean_json_fixed):
                                if char == '{': count += 1
                                elif char == '}':
                                    count -= 1
                                    if count == 0:
                                        end_pos = i + 1
                                        break
                            if end_pos > 0:
                                logger.info(f"Extra data detected. Attempting to parse first {end_pos} chars.")
                                k2_analysis = json.loads(clean_json_fixed[:end_pos])
                                logger.info("JSON parsing successful using first object extraction")
                        except Exception as e3:
                            logger.error(f"First object extraction failed: {e3}")
                            k2_analysis = None
                    else:
                        k2_analysis = None

                    if not k2_analysis:
                        logger.error(f"Final cleaned JSON was: {clean_json_fixed[:1000]}...")

                    # Si tout échoue, créer un résultat par défaut avec les informations disponibles
                    logger.warning("Creating fallback analysis result due to JSON parsing failure")
                    k2_analysis = {
                        "reasoning_summary": f"Analysis completed but JSON parsing failed. Raw response length: {len(raw_content)} characters. Error: {str(e2)}",
                        "confidence_score": 0.5,
                        "divergences": [],
                        "contradictions": [],
                        "common_findings": ["Analysis attempted but result parsing failed"],
                        "research_gaps": [],
                        "counter_hypotheses": [],
                        "protocol": {
                            "title": "Analysis Failed - Manual Review Required",
                            "hypothesis": "Unable to parse AI response",
                            "objective": "Manual review of raw AI output needed",
                            "expected_outcomes": "Manual analysis required",
                            "statistical_analysis_plan": "TBD",
                            "success_criteria": ["Manual review completed"],
                            "estimated_duration_days": 1.0,
                            "estimated_budget_usd": 0.0,
                            "resource_optimization": "N/A",
                            "material_constraints": "N/A",
                            "alternative_approaches": ["Manual analysis"],
                            "risk_assessment": {"parsing_failure": "Manual intervention required"},
                            "variables": [],
                            "steps": []
                        },
                        "recommendations": ["Review raw AI response manually", "Consider retrying analysis"]
                    }

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
        
        def ensure_list(val):
            if val is None: return []
            if isinstance(val, str): return [val]
            if not isinstance(val, list): return [str(val)]
            return val
        
        # Construire les étapes
        steps = []
        for i, step_data in enumerate(protocol_data.get("steps", []), 1):
            steps.append(ExperimentalStep(
                step_number=i,
                description=step_data.get("description", f"Step {i}"),
                duration_hours=step_data.get("duration_hours"),
                materials=ensure_list(step_data.get("materials", [])),
                critical_parameters=ensure_list(step_data.get("critical_parameters", [])),
                validation_criteria=step_data.get("validation_criteria", "Protocol requirements"),
                risk_level=step_data.get("risk_level", "medium"),
                contingency_plan=step_data.get("contingency_plan")
            ))
        
        # Construire les variables
        variables = []
        for var_data in protocol_data.get("variables", []):
            possible_vals = var_data.get("possible_values")
            if isinstance(possible_vals, str):
                possible_vals = [possible_vals]
                
            variables.append(ExperimentalVariable(
                name=var_data.get("name", "Variable"),
                type=var_data.get("type", "independent"),
                measurement_unit=var_data.get("measurement_unit"),
                measurement_method=var_data.get("measurement_method", "TBD"),
                possible_values=possible_vals
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
            success_criteria=ensure_list(protocol_data.get("success_criteria", ["Protocol completed as designed"])),
            estimated_duration_days=parse_float(protocol_data.get("estimated_duration_days"), 30.0),
            estimated_budget_usd=parse_float(protocol_data.get("estimated_budget_usd"), None),
            resource_optimization=protocol_data.get("resource_optimization"),
            material_constraints=ensure_list(protocol_data.get("material_constraints", [])),
            alternative_approaches=ensure_list(protocol_data.get("alternative_approaches", [])),
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
