"""
Module 1: Ingestion & Normalisation
Transforme des documents scientifiques en représentation exploitable
"""
import json
from typing import List, Optional, Dict, Any
from app.models.schemas import ScientificDocument, DocumentType, ExtractedHypothesis
import re


class DocumentIngestionEngine:
    """Moteur d'ingestion et normalisation de documents"""
    
    def __init__(self):
        self.extraction_prompts = self._init_prompts()
    
    def _init_prompts(self) -> Dict[str, str]:
        """Initialise les prompts d'extraction K2 Think"""
        return {
            "extract_hypotheses": """Extrait TOUTES les hypothèses principales et secondaires du document scientifique.
Pour chaque hypothèse:
- Cite le texte exact
- Évalue la confiance (0-1)
- Identifie si c'est hypothèse principale ou secondaire

Format JSON:
{
  "hypotheses": [
    {"text": "...", "confidence": 0.9, "type": "main|secondary", "paragraph": "..."}
  ]
}""",
            
            "extract_methodology": """Analyse la méthodologie scientifique.
Extraction structurée:
- Type d'étude
- Variables indépendantes, dépendantes, contrôles
- Méthodes statistiques
- Taille d'échantillon
- Limitations méthodologiques

Format JSON avec toutes les sections""",
            
            "extract_gaps": """Identifie les lacunes de recherche:
- Variables non explorées
- Paramètres ignorés
- Hypothèses implicites non testées
- Questions soulevées mais non répondues

Pour chaque gap: description + importance (0-1)""",
            
            "build_knowledge_graph": """Construit une représentation relationnelle:
- Concepts clés
- Connexions concept->variable->résultat
- Flux causal
- Dépendances

Retour: graphe connexions"""
        }
    
    def ingest_pdf(self, file_path: str, metadata: Optional[Dict] = None) -> ScientificDocument:
        """
        Ingère un fichier PDF scientifique
        Note: Dans une impl réelle, utiliserait PyPDF2
        """
        # Simulation pour prototype
        doc = ScientificDocument(
            id=f"pdf_{hash(file_path)}",
            title="Extracted Title",
            authors=["Author Name"],
            abstract="Extracted abstract",
            content="Full document content",
            document_type=DocumentType.PDF,
            doi=metadata.get("doi") if metadata else None
        )
        return doc
    
    def ingest_arxiv(self, arxiv_id: str) -> ScientificDocument:
        """Ingère un article ArXiv"""
        # Simulation - dans la réalité, utiliserait l'API ArXiv
        doc = ScientificDocument(
            id=arxiv_id,
            title="ArXiv Paper Title",
            authors=["Researcher"],
            abstract="Paper abstract",
            content="Full paper",
            document_type=DocumentType.ARXIV,
            arxiv_id=arxiv_id
        )
        return doc
    
    def normalize_document(self, doc: ScientificDocument) -> ScientificDocument:
        """
        Normalise un document (nettoyage, structuration)
        """
        # Nettoyage du contenu
        doc.content = self._clean_text(doc.content)
        doc.abstract = self._clean_text(doc.abstract)
        doc.title = doc.title.strip()
        
        return doc
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte: supprime espaces doubles, caractères spéciaux"""
        text = re.sub(r'\s+', ' ', text)  # Espaces multiples → un espace
        text = re.sub(r'[^\w\s\-.,;:\'"()\"—]', '', text)  # Caractères spéciaux
        return text.strip()
    
    def extract_structures(self, doc: ScientificDocument) -> Dict[str, Any]:
        """
        Extrait les structures principales du document
        (hypothèses, méthodologie, résultats, limitations)
        
        Pour K2 Think: ce module retourne les extractions pour orchestration
        """
        extraction = {
            "document_id": doc.id,
            "hypotheses": self._extract_hypotheses_schema(doc),
            "methodology": self._extract_methodology_schema(doc),
            "results": self._extract_results_schema(doc),
            "limitations": self._extract_limitations_schema(doc),
            "citations": self._extract_citations(doc),
            "knowledge_graph": self._build_minimal_knowledge_graph(doc)
        }
        return extraction
    
    def _extract_hypotheses_schema(self, doc: ScientificDocument) -> List[Dict]:
        """Structure pour extraction d'hypothèses"""
        # Placeholder - orchestré par K2 Think via LLM
        return [
            {
                "text": "Primary hypothesis extracted from document",
                "confidence": 0.85,
                "type": "main",
                "section": "introduction"
            }
        ]
    
    def _extract_methodology_schema(self, doc: ScientificDocument) -> Dict:
        """Structure pour extraction de méthodologie"""
        return {
            "study_type": "experimental",
            "variables_count": 0,
            "sample_size": None,
            "statistical_methods": [],
            "duration": None
        }
    
    def _extract_results_schema(self, doc: ScientificDocument) -> Dict:
        """Structure pour extraction de résultats"""
        return {
            "main_finding": "",
            "supporting_evidence": [],
            "numerical_results": [],
            "confidence_level": 0.0
        }
    
    def _extract_limitations_schema(self, doc: ScientificDocument) -> List[str]:
        """Limitations identifiées"""
        return []
    
    def _extract_citations(self, doc: ScientificDocument) -> List[Dict]:
        """Extrait les citations et références"""
        # Placeholder
        return []
    
    def _build_minimal_knowledge_graph(self, doc: ScientificDocument) -> Dict:
        """Construit un mini graphe de connaissances"""
        return {
            "nodes": [],  # {"id": "concept", "type": "hypothesis|variable|result"}
            "edges": []   # {"source": "id1", "target": "id2", "relation": "causes|contradicts"}
        }
