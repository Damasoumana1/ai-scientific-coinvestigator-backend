"""
LangGraph Orchestration Workflow
Multi-step reasoning graph for scientific analysis
"""
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
from pathlib import Path


# --- Pydantic Models for Structured Output Parsing ---

class Contradiction(BaseModel):
    variable: str = Field(description="The variable or result area of the contradiction.")
    statement_a: str = Field(description="The statement from the first source.")
    statement_b: str = Field(description="The contradictory statement from the second source.")
    confidence: float = Field(description="Confidence score (0-1) of the contradiction.")
    explanation: str = Field(description="Brief explanation of why it's a contradiction.")

class ContradictionList(BaseModel):
    contradictions: List[Contradiction]

class Hypothesis(BaseModel):
    formulation: str = Field(description="Clear formulation of the hypothesis.")
    justification: str = Field(description="Justification based on documents and contradictions.")
    variables_to_test: List[str] = Field(description="Key variables to test.")
    impact_potential: str = Field(description="Potential impact of this hypothesis.")

class HypothesisList(BaseModel):
    hypotheses: List[Hypothesis]

class ResearchGap(BaseModel):
    description: str = Field(description="Description of the research gap.")
    importance: str = Field(description="Importance of addressing this gap (e.g., High, Medium, Low).")

class ResearchGapList(BaseModel):
    gaps: List[ResearchGap]

class Protocol(BaseModel):
    title: str = Field(description="Title of the experimental protocol.")
    hypothesis_tested: str = Field(description="The clear hypothesis being tested.")
    methodology: str = Field(description="Detailed step-by-step methodology.")
    success_criteria: str = Field(description="Clear criteria for success or failure.")

class Critique(BaseModel):
    logical_coherence: str = Field(description="Assessment of the logical coherence of the analysis.")
    scientific_feasibility: str = Field(description="Assessment of the scientific feasibility of the protocols.")
    originality_and_impact: str = Field(description="Assessment of the originality and potential impact.")
    identified_limitations: List[str] = Field(description="List of identified limitations in the analysis or protocols.")
    suggested_improvements: List[str] = Field(description="List of suggested improvements.")


class AnalysisState(TypedDict, total=False):
    """
    State for the analysis workflow.
    `total=False` means keys are optional and can be added progressively.
    """
    documents: List[str]
    analysis_type: str
    contradictions: List[Dict]
    hypotheses: List[Dict]
    research_gaps: List[Dict]
    protocols: List[Dict]
    reasoning_trace: List[str]
    error: str


class ResearchOrchestrator:
    """
    LangGraph-based orchestrator for multi-step reasoning
    Handles: Document analysis → Contradiction → Hypothesis → Protocol Generation
    """
    
    def __init__(self, openai_api_key: str, k2_client=None):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4-turbo",
            temperature=0.1
        )
        self.k2_client = k2_client
        
        # Utiliser un chemin absolu pour la base de données de mémoire pour plus de robustesse
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        db_path = log_dir / "reasoning_memory.db"
        self.memory = SqliteSaver(db_path=str(db_path))
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the orchestration graph
        Flow: Input → Extract → Analyze → Critique → Optimize → Export
        """
        workflow = StateGraph(AnalysisState)
        
        # Add nodes (processing steps)
        workflow.add_node("extract_documents", self._extract_documents)
        workflow.add_node("detect_contradictions", self._detect_contradictions)
        workflow.add_node("generate_hypotheses", self._generate_hypotheses)
        workflow.add_node("identify_gaps", self._identify_gaps)
        workflow.add_node("design_protocols", self._design_protocols)
        workflow.add_node("self_critique", self._self_critique)
        workflow.add_node("finalize_results", self._finalize_results)
        
        # Add edges (workflow flow)
        workflow.set_entry_point("extract_documents")
        workflow.add_edge("extract_documents", "detect_contradictions")
        workflow.add_edge("detect_contradictions", "generate_hypotheses")
        workflow.add_edge("generate_hypotheses", "identify_gaps")
        workflow.add_edge("identify_gaps", "design_protocols")
        workflow.add_edge("design_protocols", "self_critique")
        workflow.add_edge("self_critique", "finalize_results")
        workflow.add_edge("finalize_results", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _extract_documents(self, state: AnalysisState) -> AnalysisState:
        """Step 1: Extract and structure document content"""
        state["reasoning_trace"].append("📄 Extracting documents...")
        
        prompt = SystemMessage(content="""
        Extrait et structure les informations clés de ces documents scientifiques:
        1. Objectif de recherche
        2. Méthodologie
        3. Variables principales
        4. Résultats clés
        5. Limitations
        """) + HumanMessage(content=str(state["documents"]))
        
        response = await self.llm.ainvoke([prompt])
        state["reasoning_trace"].append(f"✓ Documents extracted: {response.content[:100]}...")
        
        return state
    
    async def _detect_contradictions(self, state: AnalysisState) -> AnalysisState:
        """Step 2: Detect contradictions between documents"""
        state["reasoning_trace"].append("🔍 Detecting contradictions...")
        
        if self.k2_client:
            try:
                results = await self.k2_client.analyze_documents(
                    documents=state["documents"],
                    analysis_type="contradiction_detection"
                )
                state["contradictions"] = results.get("contradictions", [])
            except Exception as e:
                state["error"] = f"K2 API error: {str(e)}"
                return state
        else:
            # Fallback to LLM
            parser = PydanticOutputParser(pydantic_object=ContradictionList)
            prompt = SystemMessage(content=f"""
            Identifie les contradictions ou divergences significatives entre ces documents.
            Pour chaque contradiction:
            - Variable ou résultat
            - Énoncés contradictoires
            - Confiance (0-1)
            - Explication
            
            {parser.get_format_instructions()}
            """) + HumanMessage(content=str(state["documents"]))
            
            chain = self.llm | parser
            result = await chain.ainvoke([prompt])
            state["contradictions"] = [c.dict() for c in result.contradictions]
        
        state["reasoning_trace"].append(
            f"✓ Found {len(state.get('contradictions', []))} contradictions"
        )
        return state
    
    async def _generate_hypotheses(self, state: AnalysisState) -> AnalysisState:
        """Step 3: Generate new hypotheses from analysis"""
        state["reasoning_trace"].append("💡 Generating hypotheses...")
        
        parser = PydanticOutputParser(pydantic_object=HypothesisList)
        prompt = SystemMessage(content=f"""
        Basé sur les documents et contradictions identifiées, génère 3-5 hypothèses
        scientifiques novatrices qui pourraient résoudre les gaps identifiés.
        
        Pour chaque hypothèse:
        - Formulation claire
        - Justification
        - Variables à tester
        - Potentiel d'impact
        
        {parser.get_format_instructions()}
        """) + HumanMessage(content=json.dumps({
            "documents": state["documents"],
            "contradictions": state["contradictions"]
        }))
        
        chain = self.llm | parser
        result = await chain.ainvoke([prompt])
        state["hypotheses"] = [h.dict() for h in result.hypotheses]
        state["reasoning_trace"].append(
            f"✓ Generated {len(state.get('hypotheses', []))} hypotheses"
        )
        
        return state
    
    async def _identify_gaps(self, state: AnalysisState) -> AnalysisState:
        """Step 4: Identify research gaps"""
        state["reasoning_trace"].append("🎯 Identifying research gaps...")
        
        parser = PydanticOutputParser(pydantic_object=ResearchGapList)
        prompt = SystemMessage(content=f"""
        Identifie les gaps de recherche importants:
        1. Variables explorées partiellement
        2. Paramètres ignorés
        3. Hypothèses jamais testées directement
        4. Intersections disciplinaires non exploitées
        
        Classifie par importance.
        
        {parser.get_format_instructions()}
        """) + HumanMessage(content=json.dumps({
            "documents": state["documents"],
            "hypotheses": state["hypotheses"]
        }))
        
        chain = self.llm | parser
        result = await chain.ainvoke([prompt])
        state["research_gaps"] = [g.dict() for g in result.gaps]
        state["reasoning_trace"].append(
            f"✓ Identified {len(state.get('research_gaps', []))} research gaps"
        )
        
        return state
    
    async def _design_protocols(self, state: AnalysisState) -> AnalysisState:
        """Step 5: Design experimental protocols"""
        state["reasoning_trace"].append("🧪 Designing protocols...")
        
        # Generate multiple protocol versions for self-consistency
        parser = PydanticOutputParser(pydantic_object=Protocol)
        versions = []
        for i in range(3):
            prompt = SystemMessage(content=f"""
            Version {i+1}: Conçois un protocole expérimental rigoureux pour tester ces hypothèses:
            
            Comprendre:
            - Hypothèse claire
            - Variables indépendantes/dépendantes/contrôle
            - Méthodologie détaillée
            - Critères de succès
            - Analyse de risques
            - Estimation coûts/durée
            
            {parser.get_format_instructions()}
            """) + HumanMessage(content=json.dumps({
                "hypotheses": state["hypotheses"][:2],
                "gaps": state["research_gaps"][:3]
            }))
            
            chain = self.llm | parser
            protocol_version = await chain.ainvoke([prompt])
            versions.append(protocol_version.dict())
        
        # Select best protocol (self-consistency)
        best_protocol = self._select_best_protocol(versions)
        state["protocols"] = [best_protocol]
        state["reasoning_trace"].append(
            "✓ Generated and selected best protocol (self-consistency)"
        )
        
        return state
    
    async def _self_critique(self, state: AnalysisState) -> AnalysisState:
        """Step 6: Self-critique and validation"""
        state["reasoning_trace"].append("🔬 Self-critique and validation...")
        
        parser = PydanticOutputParser(pydantic_object=Critique)
        prompt = SystemMessage(content=f"""
        Critique les résultats de l'analyse:
        1. Cohérence logique
        2. Faisabilité scientifique
        3. Originalité et impact potentiel
        4. Limitations
        5. Amélioration suggérées
        
        {parser.get_format_instructions()}
        """) + HumanMessage(content=json.dumps({
            "contradictions": state["contradictions"][:3],
            "hypotheses": state["hypotheses"],
            "protocols": state["protocols"]
        }))
        
        chain = self.llm | parser
        critique = await chain.ainvoke([prompt])
        state["reasoning_trace"].append("✓ Self-critique completed")
        
        return state
    
    def _finalize_results(self, state: AnalysisState) -> AnalysisState:
        """Step 7: Finalize and format results"""
        state["reasoning_trace"].append("📦 Finalizing results...")
        
        final_output = {
            "analysis_type": state["analysis_type"],
            "contradictions": state["contradictions"],
            "hypotheses": state["hypotheses"],
            "research_gaps": state["research_gaps"],
            "protocols": state["protocols"],
            "reasoning_trace": state["reasoning_trace"]
        }
        
        state["reasoning_trace"].append("✓ Analysis complete")
        return state
    
    def _select_best_protocol(self, versions: List[Dict]) -> Dict:
        """
        Select the best protocol from multiple versions
        Uses coherence and feasibility metrics
        """
        # TODO: Implement scoring logic
        return versions[0]
    
    async def run_analysis(
        self,
        documents: List[str],
        analysis_type: str = "comprehensive"
    ) -> AnalysisState:
        """Execute the full analysis workflow"""
        initial_state = {
            "documents": documents,
            "analysis_type": analysis_type,
            "contradictions": [],
            "hypotheses": [],
            "research_gaps": [],
            "protocols": [],
            "reasoning_trace": ["🚀 Starting analysis workflow..."]
        }
        
        result = await self.workflow.ainvoke(initial_state)
        return result
