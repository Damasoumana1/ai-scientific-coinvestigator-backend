"""
Module 4: Experimental Design Engine
Transforme analyse → protocole actionnable avec raisonnement Socratique
"""
from typing import List, Dict, Any, Optional
from app.models.schemas import (
    ExperimentalProtocol, ExperimentalVariable, ExperimentalStep
)


class ExperimentalDesignEngine:
    """Engine pour conception de protocoles expérimentaux optimisés"""
    
    def __init__(self):
        self.design_prompts = self._init_design_prompts()
    
    def _init_design_prompts(self) -> Dict[str, str]:
        """K2 Think prompts pour design expérimental"""
        return {
            "socratic_design": """Applique le raisonnement Socratique pour concevoir protocole:
1. Quelle est l'hypothesis testée exactement?
2. Quelles variables causales? Dépendantes?
3. Quels confondeurs possibles?
4. Comment les contrôler?
5. Quelle puissance statistique?
6. Les résultats transfèrent-ils?

Valide cohérence à chaque étape""",
            
            "variable_identification": """Identifie TOUTES les variables:
1. Variables indépendantes (contrôlées par expérimentateur)
2. Variables dépendantes (mesurées comme outcome)
3. Variables contrôle (tenues constantes)
4. Facteurs confusion possibles

Pour chaque: plage, unité mesure, fidélité mesure""",
            
            "protocol_sequencing": """Séquence logique du protocole:
1. Préparation matériel
2. Baseline measurements
3. Intervention application
4. Outcome measurement (timing critique)
5. Wash-out si applicable
6. Final assessment

Temps, ressources, points de contrôle critiques""",
            
            "risk_assessment": """Identifie risques expérimentaux:
- Taux d'attrition possibles
- Dérives de protocole
- Variabilité mesure
- Effets adverses/inattendus
- Contamination cross-over

Pour chaque: probabilité + impact + mitigation""",
        }
    
    def design_experimental_protocol(
        self,
        hypothesis: str,
        research_gap: str,
        available_resources: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> ExperimentalProtocol:
        """
        Conçoit un protocole expérimental complet et cohérent
        
        Args:
            hypothesis: Hypothèse à tester
            research_gap: Gap de recherche adressé
            available_resources: Ressources disponibles
            constraints: Contraintes (budget, temps, lieu)
        """
        
        # Étape 1: Identification variables (K2 Think orchestrerait)
        variables = self._identify_variables(hypothesis)
        
        # Étape 2: Séquençage protocole
        steps = self._sequence_protocol(hypothesis, variables, available_resources)
        
        # Étape 3: Assessment risques
        risk_assessment = self._assess_risks(steps, variables)
        
        # Étape 4: Alternatives
        alternatives = self._generate_alternatives(hypothesis, variables)
        
        # Construction protocole complet
        protocol = ExperimentalProtocol(
            title=f"Experimental Protocol: {hypothesis[:80]}",
            hypothesis=hypothesis,
            objective=f"Test hypothesis regarding {research_gap}",
            variables=variables,
            steps=steps,
            expected_outcomes=self._draft_expected_outcomes(hypothesis),
            statistical_analysis_plan=self._design_statistics(variables),
            success_criteria=[
                "Primary outcome shows statistically significant effect (p < 0.05)",
                "Effect size in expected range",
                "No safety/adverse events above expected"
            ],
            estimated_duration_days=sum(s.duration_hours or 2 for s in steps) / 8,
            estimated_budget_usd=self._estimate_budget(variables, steps),
            material_constraints=constraints.get("material_unavailable", []) if constraints else None,
            alternative_approaches=alternatives,
            risk_assessment=risk_assessment
        )
        
        return protocol
    
    def _identify_variables(self, hypothesis: str) -> List[ExperimentalVariable]:
        """
        Identifie variables indépendantes, dépendantes, contrôles
        """
        variables = [
            ExperimentalVariable(
                name="Treatment Group",
                type="independent",
                measurement_unit=None,
                measurement_method="Randomized assignment",
                possible_values=["Control", "Treatment"]
            ),
            ExperimentalVariable(
                name="Primary Outcome Measure",
                type="dependent",
                measurement_unit="score/percentage",
                measurement_method="Validated scale/instrument",
                possible_values=None
            ),
            ExperimentalVariable(
                name="Age",
                type="control",
                measurement_unit="years",
                measurement_method="Self-report or medical record",
                possible_values=None
            ),
            ExperimentalVariable(
                name="Sex/Gender",
                type="control",
                measurement_unit=None,
                measurement_method="Self-report",
                possible_values=["M", "F", "Other"]
            ),
            ExperimentalVariable(
                name="Baseline Score",
                type="confounding",
                measurement_unit="score",
                measurement_method="Pre-intervention assessment",
                possible_values=None
            )
        ]
        return variables
    
    def _sequence_protocol(
        self,
        hypothesis: str,
        variables: List[ExperimentalVariable],
        resources: Optional[Dict] = None
    ) -> List[ExperimentalStep]:
        """
        Séquence logique des étapes du protocole
        """
        steps = [
            ExperimentalStep(
                step_number=1,
                description="Participant recruitment and screening",
                duration_hours=8.0,
                materials_required=["Recruitment platform", "Screening forms", "Informed consent"],
                critical_parameters=["Sample size targets", "Inclusion/exclusion critera"],
                validation_criteria="All participants meet criteria; informed consent obtained",
                risk_level="low"
            ),
            ExperimentalStep(
                step_number=2,
                description="Baseline measurements and randomization",
                duration_hours=2.0,
                materials_required=["Measurement instruments", "Randomization protocol"],
                critical_parameters=["Valid measurement", "Proper randomization"],
                validation_criteria="Baseline characteristics documented; allocation concealed",
                risk_level="low"
            ),
            ExperimentalStep(
                step_number=3,
                description="Intervention delivery",
                duration_hours=4.0,
                materials_required=["Treatment materials", "Intervention protocol"],
                critical_parameters=["Intervention fidelity", "Time/dosage consistency"],
                validation_criteria="Intervention administered per protocol",
                risk_level="medium",
                contingency_plan="Alternative delivery method if primary unavailable"
            ),
            ExperimentalStep(
                step_number=4,
                description="Outcome measurement (primary timepoint)",
                duration_hours=2.0,
                materials_required=["Outcome measurement instruments"],
                critical_parameters=["Timing accuracy", "Instrument validity"],
                validation_criteria="Valid outcome data collected",
                risk_level="medium"
            ),
            ExperimentalStep(
                step_number=5,
                description="Data analysis and interpretation",
                duration_hours=6.0,
                materials_required=["Statistical software", "Analysis plan"],
                critical_parameters=["Pre-registered analyses", "Sensitivity checks"],
                validation_criteria="Analyses match pre-registered plan",
                risk_level="low"
            )
        ]
        return steps
    
    def _draft_expected_outcomes(self, hypothesis: str) -> str:
        """Résultats attendus"""
        return f"""If hypothesis is supported:
- Primary outcome shows significant effect (p < 0.05)
- Effect size in range [0.3-0.8] (small-to-medium)
- Secondary outcomes support mechanism

If hypothesis is not supported:
- No significant difference between groups
- Confidence interval excludes meaningful effect
- Possible alternative explanations investigated"""
    
    def _design_statistics(self, variables: List[ExperimentalVariable]) -> str:
        """Plan d'analyse statistique"""
        return """Primary Analysis:
- Independent samples t-test (or non-parametric equivalent)
- Significance level: α = 0.05 (two-tailed)
- Confidence intervals: 95%

Secondary Analyses:
- ANCOVA controlling for baseline and key covariates
- Subgroup analyses by Age, Sex
- Sensitivity analyses for missing data

Power Calculation:
- Target power: 80%
- Assumed effect size: medium (d = 0.5)
- Sample size: calculated to achieve power"""
    
    def _assess_risks(
        self,
        steps: List[ExperimentalStep],
        variables: List[ExperimentalVariable]
    ) -> Dict[str, Any]:
        """
        Assessment des risques expérimentaux
        """
        risk_assessment = {
            "overall_risk_level": "medium",
            "critical_risks": [
                {
                    "risk": "Participant attrition",
                    "probability": 0.3,
                    "impact": "Reduced power if >20% loss",
                    "mitigation": "Engagement strategy; liberal criteria for follow-up"
                },
                {
                    "risk": "Intervention delivery deviation",
                    "probability": 0.25,
                    "impact": "Reduced effect size; internal validity threat",
                    "mitigation": "Fidelity monitoring; standardized training"
                },
                {
                    "risk": "Measurement variability",
                    "probability": 0.2,
                    "impact": "Increased noise; reduced power",
                    "mitigation": "Instrument validation; rater training"
                }
            ],
            "safety_considerations": {
                "adverse_event_monitoring": "Daily participant check-ins",
                "stopping_rules": "Stop if serious adverse event observed",
                "ethics_approval": "Required before commencement"
            }
        }
        return risk_assessment
    
    def _estimate_budget(
        self,
        variables: List[ExperimentalVariable],
        steps: List[ExperimentalStep]
    ) -> Optional[float]:
        """Estimation du budget"""
        # Simplifiée
        personnel_cost = 40 * 40 * 100  # 40 hrs @ $100/hr
        materials_cost = 50 * 200  # Supplies
        equipment_rental = 5000  # Equipment/Software
        misc = 2000
        
        return personnel_cost + materials_cost + equipment_rental + misc
    
    def _generate_alternatives(
        self,
        hypothesis: str,
        variables: List[ExperimentalVariable]
    ) -> List[str]:
        """Approches alternatives"""
        return [
            "Observational study design (if experimental infeasible)",
            "Quasi-experimental with controls (if randomization impossible)",
            "Computational modeling/simulation study (faster, lower cost)",
            "Meta-analysis combining existing data (if primary study not possible)"
        ]
