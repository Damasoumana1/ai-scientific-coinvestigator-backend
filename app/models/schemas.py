"""
Pydantic schemas pour AI Scientific Co-Investigator
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    """Types de documents supportés"""
    PDF = "pdf"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    CUSTOM = "custom"


class ScientificDocument(BaseModel):
    """Représentation d'un document scientifique"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    content: str
    document_type: DocumentType
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    publication_date: Optional[str] = None
    citations_count: Optional[int] = None


class ExtractedHypothesis(BaseModel):
    """Hypothèse extraite d'un document"""
    text: str
    confidence: float = Field(ge=0, le=1)
    source_document: str
    paragraph_reference: str


class Methodology(BaseModel):
    """Méthodologie d'étude"""
    name: str
    description: str
    variables: List[str]
    controls: List[str]
    statistical_methods: List[str]
    sample_size: Optional[int] = None
    study_type: str  # "experimental", "observational", etc.


class ResearchGap(BaseModel):
    """Gap de recherche identifié"""
    gap_description: str
    importance_score: float = Field(ge=0, le=1)
    related_variables: List[str]
    suggested_investigation: str
    source_documents: List[str]
    citations: List[str] = Field(default_factory=list, description="Citations au format (Auteur, Année)")


class ComparativeAnalysis(BaseModel):
    """Analyse comparative multi-documents"""
    document_ids: List[str]
    divergences: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
    common_findings: List[str]
    research_gaps: List[ResearchGap]
    confidence_score: float = Field(ge=0, le=1)


class CounterHypothesis(BaseModel):
    """Contre-hypothèse générée par le stress tester"""
    hypothesis: str
    rationale: str
    potential_bias: str
    validation_experiment: str
    confidence_against: float = Field(ge=0, le=1)
    citations: List[str] = Field(default_factory=list, description="Citations au format (Auteur, Année)")


class ExperimentalVariable(BaseModel):
    """Variable expérimentale"""
    name: str
    type: str  # "independent", "dependent", "control", "confounding"
    measurement_unit: Optional[str] = None
    measurement_method: str
    possible_values: Optional[List[Any]] = None


class ExperimentalStep(BaseModel):
    """Étape d'un protocole expérimental"""
    step_number: int
    description: str
    duration_hours: Optional[float] = None
    materials: List[str] = []
    critical_parameters: List[str] = []
    validation_criteria: str = "Standard validation"
    risk_level: str = "low"  # "low", "medium", "high"
    contingency_plan: Optional[str] = None


class ExperimentalProtocol(BaseModel):
    """Protocole expérimental complet"""
    title: str
    hypothesis: str
    objective: str
    variables: List[ExperimentalVariable]
    steps: List[ExperimentalStep]
    expected_outcomes: str
    statistical_analysis_plan: str
    success_criteria: List[str]
    estimated_duration_days: float
    estimated_budget_usd: Optional[float] = None
    material_constraints: Optional[List[str]] = None
    alternative_approaches: List[str]
    risk_assessment: Dict[str, Any]


class AnalysisRequest(BaseModel):
    """Requête d'analyse scientifique"""
    documents: List[ScientificDocument]
    analysis_type: str = "comprehensive"  # "comparative", "gap-detection", "protocol-design"
    focus_area: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    user_notes: Optional[str] = None


class AnalysisResult(BaseModel):
    """Résultat d'analyse complet"""
    request_id: str
    documents_analyzed: int
    reasoning_summary: Optional[str] = None
    comparative_analysis: Optional[ComparativeAnalysis] = None
    research_gaps: List[ResearchGap]
    counter_hypotheses: List[CounterHypothesis]
    proposed_protocol: Optional[ExperimentalProtocol] = None
    strategic_recommendations: List[str]
    reasoning_trace: List[Dict[str, Any]]
    confidence_overall: float = Field(ge=0, le=1)


class AuditLog(BaseModel):
    """Log d'audit pour traçabilité"""
    timestamp: str
    step: str
    decision: str
    reasoning: str
    intermediate_results: Optional[Dict[str, Any]] = None
    model_used: str
    
    model_config = {
        "protected_namespaces": ()
    }
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class ChatRequest(BaseModel):
    """Requête de chat scientifique"""
    message: str
    history: Optional[List[Dict[str, str]]] = []
    analysis_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Réponse du chat scientifique"""
    answer: str
    reasoning_log: Optional[str] = None
    suggested_actions: Optional[List[str]] = []
