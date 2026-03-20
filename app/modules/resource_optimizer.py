"""
Module 5: Resource & Budget Optimizer
La "Secret Sauce" - Adapte protocole aux contraintes réelles
"""
from typing import List, Dict, Any, Optional
from app.models.schemas import ExperimentalProtocol


class ResourceOptimizer:
    \"\"\"Optimise protocole expérimental en fonction des contraintes\"\"\"
    
    def __init__(self):
        self.optimization_prompts = self._init_optimization_prompts()
        self.material_equivalents = self._init_material_equivalents()
    
    def _init_optimization_prompts(self) -> Dict[str, str]:
        \"\"\"K2 Think prompts pour optimisation ressources\"\"\"
        return {
            "resource_mapping": \"\"\"Mappe les ressources requises aux ressources disponibles:
1. Matériaux/réactifs: identifier alternatives validées
2. Équipement: remplacer par équivalents disponibles
3. Personnel: adapter chronoprogramme
4. Locaux: adapter mise en place

Pour chaque adaptation: impact sur validité (0-1)
Proposer alternatives seulement si validité conservée\"\"\",
            
            "budget_optimization": \"\"\"Optimise budget sans perdre rigueur:
1. Identifier dépenses non-critiques
2. Proposer alternatives moins chères validées
3. Prioriser expériences clés
4. Stagner si nécessaire

Retour: protocole ajusté + budget minimum + recommandations\"\"\",
            
            "timeline_adjustment": \"\"\"Adapte calendrier aux contraintes temps:
1. Identifier étapes parallélisables
2. Compresser sans compromis validité
3. Proposer timeline alternatives
4. Indiquer impact sur conclusions\"\"\",
        }
    
    def _init_material_equivalents(self) -> Dict[str, List[Dict]]:
        \"\"\"Database d'équivalents matériaux validés\"\"\"
        return {
            "HPLC_system": [
                {
                    "original": "High-performance liquid chromatography system",
                    "alternative": "Gas chromatography",
                    "cost_ratio": 0.6,
                    "validity_impact": 0.95,
                    "conditions": "If compounds are volatile"
                },
                {
                    "original": "High-performance liquid chromatography system",
                    "alternative": "UV-Visible spectrophotometry",
                    "cost_ratio": 0.3,
                    "validity_impact": 0.75,
                    "conditions": "For qualitative confirmation only"
                }
            ],
            "cell_culture": [
                {
                    "original": "Primary cell culture from patient biopsies",
                    "alternative": "Established cell lines",
                    "cost_ratio": 0.2,
                    "validity_impact": 0.80,
                    "conditions": "If relevant cell line exists"
                },
                {
                    "original": "3D tissue culture system",
                    "alternative": "2D monolayer culture",
                    "cost_ratio": 0.4,
                    "validity_impact": 0.70,
                    "conditions": "For initial screening only"
                }
            ],
            "animal_model": [
                {
                    "original": "Primate model",
                    "alternative": "Rodent model with human-equivalent genetics",
                    "cost_ratio": 0.1,
                    "validity_impact": 0.85,
                    "conditions": "For mechanism study; translational risk"
                },
                {
                    "original": "In-vivo animal model",
                    "alternative": "Organoid model",
                    "cost_ratio": 0.6,
                    "validity_impact": 0.75,
                    "conditions": "For disease phenotyping"
                }
            ]
        }
    
    def optimize_protocol(
        self,
        protocol: ExperimentalProtocol,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        \"\"\"
        Optimise protocole selon contraintes
        
        Args:
            protocol: Protocole initial
            constraints: {
                "budget_usd": float,
                "duration_days": float,
                "unavailable_materials": [str],
                "available_equipment": [str],
                "location_type": str,
                "team_size": int
            }
        \"\"\"
        
        optimization = {
            "original_protocol": {
                "estimated_cost": protocol.estimated_budget_usd,
                "estimated_duration": protocol.estimated_duration_days,
                "sample_size": self._estimate_sample_size(protocol),
            },
            "constraints": constraints,
            "adaptations": [],
            "optimized_protocol": None,
            "optimized_cost": None,
            "validity_impact_score": 1.0,
            "recommendations": []
        }
        
        # Optimization round 1: Material substitutions
        material_adaptations = self._adapt_materials(
            protocol,
            constraints.get("unavailable_materials", [])
        )
        optimization["adaptations"].extend(material_adaptations)
        
        # Optimization round 2: Timeline compression
        if constraints.get("duration_days") and \
           constraints["duration_days"] < protocol.estimated_duration_days:
            timeline_adapt = self._compress_timeline(
                protocol,
                constraints["duration_days"]
            )
            optimization["adaptations"].append(timeline_adapt)
        
        # Optimization round 3: Budget reduction
        if constraints.get("budget_usd"):
            budget_adapt = self._reduce_budget(
                protocol,
                constraints["budget_usd"],
                material_adaptations
            )
            optimization["adaptations"].append(budget_adapt)
            optimization["optimized_cost"] = budget_adapt.get("new_cost")
        
        # Optimization round 4: Sample size adjustment
        if constraints.get("budget_usd"):
            sample_adapt = self._adjust_sample_size(
                protocol,
                optimization["optimized_cost"] or protocol.estimated_budget_usd
            )
            optimization["adaptations"].append(sample_adapt)
        
        # Calculate overall validity impact
        validity_impacts = [a.get("validity_impact", 1.0) for a in optimization["adaptations"]]
        optimization["validity_impact_score"] = min(validity_impacts) if validity_impacts else 1.0
        
        # Generate recommendations
        optimization["recommendations"] = self._generate_recommendations(
            optimization,
            constraints
        )
        
        return optimization
    
    def _adapt_materials(
        self,
        protocol: ExperimentalProtocol,
        unavailable_materials: List[str]
    ) -> List[Dict[str, Any]]:
        \"\"\"Substitue matériaux non-disponibles\"\"\"
        adaptations = []
        
        for unavailable in unavailable_materials:
            # Find equivalents in database
            if unavailable in self.material_equivalents:
                alternatives = self.material_equivalents[unavailable]
                best_alt = alternatives[0]  # Best match
                
                adaptation = {
                    "type": "material_substitution",
                    "original": unavailable,
                    "proposed_alternative": best_alt["alternative"],
                    "cost_ratio": best_alt["cost_ratio"],
                    "validity_impact": best_alt["validity_impact"],
                    "conditions": best_alt["conditions"],
                    "status": "validated" if best_alt["validity_impact"] > 0.85 else "requires_pilot"
                }
                adaptations.append(adaptation)
        
        return adaptations
    
    def _compress_timeline(
        self,
        protocol: ExperimentalProtocol,
        target_duration_days: float
    ) -> Dict[str, Any]:
        \"\"\"Compresse calendrier\"\"\"
        original_steps = len(protocol.steps)
        parallelizable_steps = [s for s in protocol.steps if self._is_parallelizable(s)]
        
        compression = {
            "type": "timeline_compression",
            "original_duration_days": protocol.estimated_duration_days,
            "target_duration_days": target_duration_days,
            "compression_ratio": target_duration_days / protocol.estimated_duration_days,
            "parallelizable_steps": len(parallelizable_steps),
            "recommended_measures": [
                f"Parallelize {len(parallelizable_steps)} non-dependent steps",
                "Add team members to compress serial steps",
                "Use overnight incubations for waiting periods"
            ],
            "validity_impact": 0.95 if target_duration_days / protocol.estimated_duration_days > 0.7 else 0.80,
            "risk_increase": "medium" if target_duration_days / protocol.estimated_duration_days < 0.7 else "low"
        }
        
        return compression
    
    def _reduce_budget(
        self,
        protocol: ExperimentalProtocol,
        target_budget_usd: float,
        material_adaptations: List[Dict]
    ) -> Dict[str, Any]:
        \"\"\"Réduit budget tout en conservant rigueur\"\"\"
        original_cost = protocol.estimated_budget_usd or 15000
        cost_savings = original_cost - target_budget_usd
        savings_percent = (cost_savings / original_cost) * 100
        
        reduction = {
            "type": "budget_reduction",
            "original_budget": original_cost,
            "target_budget": target_budget_usd,
            "required_savings": cost_savings,
            "savings_percent": savings_percent,
            "potential_reductions": [
                {
                    "category": "Equipment rental",
                    "potential_saving": "20-40%",
                    "method": "Use cheaper alternatives or institutional equipment"
                },
                {
                    "category": "Materials",
                    "potential_saving": "30-50%",
                    "method": "Bulk purchase; negotiate with suppliers"
                },
                {
                    "category": "Personnel",
                    "potential_saving": "10-20%",
                    "method": "Use graduate students for routine tasks"
                }
            ],
            "material_savings": self._calculate_material_savings(material_adaptations),
            "new_cost": target_budget_usd,
            "validity_impact": 0.90 if savings_percent < 50 else 0.75,
            "feasibility": "high" if savings_percent < 40 else "medium" if savings_percent < 60 else "low"
        }
        
        return reduction
    
    def _calculate_material_savings(self, adaptations: List[Dict]) -> float:
        \"\"\"Calcule économies matériaux\"\"\"
        total_savings = sum(
            1 - a.get("cost_ratio", 1) for a in adaptations if a.get("type") == "material_substitution"
        )
        return total_savings * 100
    
    def _adjust_sample_size(
        self,
        protocol: ExperimentalProtocol,
        available_budget: float
    ) -> Dict[str, Any]:
        \"\"\"Ajuste taille d'échantillon en fonction du budget\"\"\"
        # Cost per participant (simplified)
        cost_per_participant = (available_budget or 15000) / 50
        max_participants = int(available_budget / cost_per_participant) if available_budget else 50
        
        return {
            "type": "sample_size_adjustment",
            "cost_per_participant": cost_per_participant,
            "maximum_sample_size": max_participants,
            "statistical_power_impact": "Reduced to ~70-75% if N < 40",
            "recommendation": f"Prioritize primary outcome; accept reduced power for secondary"
        }
    
    def _is_parallelizable(self, step: Any) -> bool:
        \"\"\"Détermine si étape peut être parallélisée\"\"\"
        non_parallelizable = [
            "randomization",
            "baseline measurements",
            "data analysis"
        ]
        return not any(term in step.description.lower() for term in non_parallelizable)
    
    def _generate_recommendations(
        self,
        optimization: Dict,
        constraints: Dict
    ) -> List[str]:
        \"\"\"Généère recommandations basées sur optimisations\"\"\"
        recommendations = []
        
        if optimization["validity_impact_score"] < 0.85:
            recommendations.append(
                "WARNING: Proposed adaptations reduce protocol validity. "
                "Consider: (1) requesting additional resources, (2) narrowing research scope, "
                "(3) using pilot study for feasibility validation"
            )
        
        if len(optimization["adaptations"]) > 3:
            recommendations.append(
                "Multiple constraint adaptations required. Protocol fundamentally changed. "
                "Recommend consulting with methodology expert/biostatistician."
            )
        
        recommendations.extend([
            "Validate all material substitutions with pilot data before main study",
            "Pre-register protocol adaptations before study start",
            "Monitor validity indicators during conduct; adjust if needed"
        ])
        
        return recommendations
