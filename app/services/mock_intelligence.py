"""
Mock Intelligence Service for Hackathon Demo
Provides high-quality scientific insights when the K2 API or DB is unavailable.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List

class MockIntelligenceService:
    @staticmethod
    def get_mock_analysis_result(email: str = "researcher@example.com") -> Dict[str, Any]:
        return {
            "request_id": f"demo_{uuid.uuid4().hex[:8]}",
            "documents_analyzed": 3,
            "status": "COMPLETED",
            "confidence_overall": 0.94,
            "comparative_analysis": {
                "document_ids": ["doc1", "doc2", "doc3"],
                "divergences": [
                    {
                        "variable": "Hydrophobicity Importance",
                        "finding_a": "Critical for binding affinity (Smith et al.)",
                        "finding_b": "Non-significant in large scale trials (Johnson et al.)",
                        "impact": "High - affects compound selection strategy"
                    }
                ],
                "contradictions": [
                    {
                        "topic": "Temperature Sensitivity",
                        "conflict": "Smith claims stability up to 50°C, while Chen reports degradation at 37°C.",
                        "resolution_path": "Requires standardized pH control across both trials."
                    }
                ],
                "common_findings": [
                    "Molecular weight remains the primary predictor of passive diffusion.",
                    "All papers agree on the necessity of high-throughput screening."
                ]
            },
            "research_gaps": [
                {
                    "gap_description": "Interplay between temperature fluctuations and hydrophobicity in non-polar solvents.",
                    "importance_score": 0.89,
                    "related_variables": ["Temperature", "Octanol-water partition coefficient"],
                    "suggested_investigation": "Factorial design experiment spanning 20°C to 60°C."
                }
            ],
            "counter_hypotheses": [
                {
                    "hypothesis": "The perceived hydrophobicity importance is an artifact of pH-dependent ionization.",
                    "rationale": "Meta-analysis shows Smith used pH 7.2 while Johnson used pH 7.8.",
                    "potential_bias": "Experimental setup bias",
                    "validation_experiment": "Run parallel assays at tightly controlled pH intervals (7.0, 7.2, 7.4, 7.6, 7.8).",
                    "confidence_against": 0.76
                }
            ],
            "proposed_protocol": {
                "title": "Optimized K2-Think Validation Protocol",
                "hypothesis": "pH-Standardized binding affinity is the true metric of success.",
                "objective": "Resolve the Smith-Johnson contradiction via pH-swept assay.",
                "variables": [
                    {"name": "pH", "type": "independent", "measurement_unit": "pH", "measurement_method": "Digital pH-meter"},
                    {"name": "Binding Affinity", "type": "dependent", "measurement_unit": "nM", "measurement_method": "Surface Plasmon Resonance (SPR)"}
                ],
                "steps": [
                    {"step_number": 1, "description": "Prepare 5 buffer batches with pH 7.0 to 7.8.", "materials": ["HEPES", "NaCl"], "risk_level": "low"},
                    {"step_number": 2, "description": "Apply compound library to SPR chips at 37°C.", "materials": ["SPR Chips", "Compounds"], "risk_level": "medium"}
                ],
                "estimated_duration_days": 14,
                "estimated_budget_usd": 12500,
                "risk_assessment": {"technical_risk": "Medium", "mitigation": "Redundant SPR chips if binding is weak."}
            },
            "strategic_recommendations": [
                "Prioritize pH stabilization in all future drug-discovery pipelines.",
                "Invest in high-resolution SPR equipment to reduce measurement noise."
            ],
            "reasoning_trace": [
                {"phase": "Ingestion", "step": "Parsing", "description": "Extracted 45 variables from 3 documents.", "timestamp": datetime.now().isoformat()},
                {"phase": "Analysis", "step": "Comparison", "description": "Detected 1 major contradiction in hydrophobicity metrics.", "timestamp": datetime.now().isoformat()},
                {"phase": "Synthesis", "step": "Strategy", "description": "Generated optimized protocol to resolve conflicts.", "timestamp": datetime.now().isoformat()}
            ]
        }
