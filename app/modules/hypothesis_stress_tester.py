"""
Module 3: Hypothesis Stress Tester
Simulation de peer-review critique - DIFFÉRENCIANT CLEF
"""
from typing import List, Dict, Any
from app.models.schemas import CounterHypothesis, ExperimentalProtocol


class HypothesisStressTester:
    """Stress-teste les hypothèses comme un peer-reviewer critique"""
    
    def __init__(self):
        self.stress_test_prompts = self._init_stress_test_prompts()
    
    def _init_stress_test_prompts(self) -> Dict[str, str]:
        """K2 Think prompts pour stress testing"""
        return {
            "generate_counter_hypotheses": """Génère 3 contre-hypothèses plausibles et scientifiquement fondées:
1. Alternative concurrente basée sur données existantes
2. Explication confondante non contrôlée
3. Interprétation inverse des résultats

Pour chaque:
- Hypothèse alternative
- Justification scientifique
- Biais possibles dans l'étude originale
- Expérience critique de validation
- Confiance dans contre-hypothèse (0-1)""",
            
            "detect_biases": """Identifie biais méthodologiques possibles:
- Selection bias
- Confirmation bias
- Measurement bias
- Analyst bias
- Publication bias

Grave (0.8+) = invalide les conclusions
Modérée (0.5-0.8) = affecte interprétation
Légère (0.2-0.5) = contexte complémentaire""",
            
            "analyze_limitations": """Analyse critique des limitations:
1. Limitationen reconnues par auteurs
2. Limitations omises/implicites
3. Portée généralisation
4. Validité externe
5. Transférabilité résultats

Chaque limitation + impact sur robustesse (0-1)""",
            
            "hostile_reviewer_mode": """Simule un peer-reviewer hostile:
- Questions difficiles
- Critiques méthodologiques
- Demandes contexte additionnel
- Points de contradiction
- Alternatives explications

Ton: professionnel mais critique"""
        }
    
    def stress_test_hypothesis(
        self, 
        main_hypothesis: str,
        methodology_description: str,
        results_summary: str,
        source_documents: List[str]
    ) -> List[CounterHypothesis]:
        """
        Stress-teste une hypothèse principale
        Génère des contre-hypothèses crédibles
        """
        counter_hypotheses = [
            CounterHypothesis(
                hypothesis="Effect Y is actually caused by confounding variable Z rather than treatment X",
                rationale="Variable Z shows strong correlation with outcome and was not controlled in original study",
                potential_bias="Selection bias: patients with high Z were non-randomly assigned to treatment",
                validation_experiment="Randomized controlled trial with stratification on Z or IV analysis with Z as instrument",
                confidence_against=0.72
            ),
            CounterHypothesis(
                hypothesis="Observed results are due to measurement error and regression to mean",
                rationale="No reliability testing of measurement instruments reported; effect size consistent with statistical noise",
                potential_bias="Measurement bias + analyst bias in processing data",
                validation_experiment="Repeat measurements with different instruments; large effect-size replication",
                confidence_against=0.55
            ),
            CounterHypothesis(
                hypothesis="Alternative interpretation: moderate effect size, not clinically significant",
                rationale="Statistical significance does not imply practical relevance; confidence interval is wide",
                potential_bias="Publication bias: tendency to emphasize positive results",
                validation_experiment="Calculate NNT; compare to clinical standards; meta-analysis across similar studies",
                confidence_against=0.63
            )
        ]
        
        return counter_hypotheses
    
    def identify_critical_biases(
        self,
        study_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identifie risques de biais critiques
        Retourne liste ordonnée par gravité
        """
        identified_biases = [
            {
                "bias_type": "Selection Bias",
                "severity": 0.75,
                "description": "Enrollment criteria not clearly specified; potential self-selection",
                "impact": "Results may not be generalizable to broader population",
                "mitigation": "Use random sampling; report inclusion/exclusion criteria explicitly"
            },
            {
                "bias_type": "Confirmation Bias",
                "severity": 0.45,
                "description": "Authors may have emphasized supporting evidence",
                "impact": "Moderate - conclusions could be overstated",
                "mitigation": "Pre-register hypotheses; blind analysis when possible"
            },
            {
                "bias_type": "Publication Bias",
                "severity": 0.60,
                "description": "Likely positive publication bias in field",
                "impact": "Effect sizes in literature likely overestimate true effect",
                "mitigation": "Search for grey literature; conduct funnel plot analysis"
            }
        ]
        
        # Tri par gravité
        return sorted(identified_biases, key=lambda x: x["severity"], reverse=True)
    
    def simulate_peer_review(
        self,
        hypothesis: str,
        methodology: str,
        results: str,
        conclusions: str
    ) -> Dict[str, Any]:
        """
        Simule avis de peer-reviewer critique mais équitable
        """
        review = {
            "reviewer_role": "Critical but Fair Peer Reviewer",
            "overall_assessment": "Major Revisions Needed",
            "strengths": [
                "Clear research question and hypothesis",
                "Appropriate statistical methods",
                "Adequate sample size for primary analysis"
            ],
            "weaknesses": [
                "Insufficient control for known confounders",
                "Limited discussion of alternative explanations",
                "Generalizability limited to study population"
            ],
            "major_concerns": [
                {
                    "concern": "Methodology weakness",
                    "question": "How were participants assigned to treatment groups? Was randomization used?",
                    "impact": "Critical for internal validity"
                },
                {
                    "concern": "Alternative explanation",
                    "question": "Can results be explained by variable X rather than proposed mechanism?",
                    "impact": "Changes interpretation of findings"
                }
            ],
            "minor_comments": [
                "Figure 2 could be clearer with error bars",
                "Discussion should address recent competing publications"
            ],
            "requested_revisions": [
                "Add analysis controlling for confounders A, B, C",
                "Provide sensitivity analysis for parameter variations",
                "Include limitation discussion for mechanisms"
            ],
            "recommendation": "Desk-reject → Major Revisions → Potential Acceptance"
        }
        
        return review
    
    def generate_validation_experiments(
        self,
        counter_hypothesis: str,
        original_findings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Propose des expériences critiques de validation
        """
        validation_experiments = [
            {
                "experiment_name": "Direct Contradiction Test",
                "design": "Manipulate counter-hypothesis variable while controlling original",
                "expected_outcome": "If counter-hypothesis true, original effect should disappear",
                "feasibility": "medium",
                "cost_relative": 1.5
            },
            {
                "experiment_name": "Mechanism Confirmation",
                "design": "Measure proposed mechanism; verify it correlates with outcome",
                "expected_outcome": "Demonstrated causal chain if hypothesis correct",
                "feasibility": "medium",
                "cost_relative": 2.0
            },
            {
                "experiment_name": "Boundary Condition Analysis",
                "design": "Test hypothesis in populations where counter-hypothesis predicts null",
                "expected_outcome": "Original effect holds; counter-hypothesis fails",
                "feasibility": "high",
                "cost_relative": 1.0
            }
        ]
        
        return validation_experiments
