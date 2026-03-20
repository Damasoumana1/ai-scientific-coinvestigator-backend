"""
Export Service for Scientific Analysis Results
Handles LaTeX grant generation, CSV export, and Matplotlib visualization
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional
from app.services.k2_think_engine import K2ThinkEngine
from app.core.logging import logger
from datetime import datetime

class ExportService:
    def __init__(self):
        self.engine = K2ThinkEngine()

    async def generate_latex_grant(self, analysis_data: Dict[str, Any]) -> str:
        """
        Génère une proposition de financement au format LaTeX via K2 Think
        """
        logger.info(f"Generating LaTeX grant for analysis {analysis_data.get('request_id')}")
        
        prompt = f"""You are a senior scientific grant writer for the European Research Council (ERC) and NIH.
Based on the following scientific analysis results, generate a complete, high-quality Grant Proposal in LaTeX format.

ANALYSIS CONTEXT:
{json.dumps(analysis_data, indent=2)}

REQUIREMENTS:
1. Use standard LaTeX article class.
2. Structure: Title, Abstract, Introduction, Research Gaps & Objectives, Methodology (based on the provided protocol), Budget & Resource Optimization, Conclusion.
3. Use professional terminology and a persuasive tone.
4. Ensure all (Author, Year) citations from the analysis are preserved and correctly formatted in the text.
5. The output MUST be valid LaTeX code starting with \\documentclass and ending with \\end{{document}}.
6. Do NOT include any explanations outside the LaTeX code."""

        messages = [
            {"role": "system", "content": "You are an expert LaTeX Grant Writer Assistant."},
            {"role": "user", "content": prompt}
        ]

        response = await self.engine.k2_client.chat_completion(messages=messages)
        latex_code = response['choices'][0]['message']['content']

        # Cleanup if markdown blocks exist
        if "```latex" in latex_code:
            latex_code = latex_code.split("```latex")[1].split("```")[0].strip()
        elif "```" in latex_code:
            latex_code = latex_code.split("```")[1].split("```")[0].strip()

        return latex_code

    def generate_csv_export(self, analysis_data: Dict[str, Any]) -> str:
        """
        Convertit les données structurées de l'analyse en CSV
        """
        logger.info(f"Generating CSV export for analysis {analysis_data.get('request_id')}")
        
        # Extract protocol steps
        protocol = analysis_data.get("proposed_protocol", {})
        steps = protocol.get("steps", [])
        
        if not steps:
            # Fallback for gaps if no protocol
            gaps = analysis_data.get("research_gaps", [])
            df = pd.DataFrame(gaps)
        else:
            df = pd.DataFrame(steps)
            
        csv_path = f"/tmp/export_{analysis_data.get('request_id', 'temp')}.csv"
        df.to_csv(csv_path, index=False)
        
        with open(csv_path, 'r') as f:
            content = f.read()
            
        os.remove(csv_path)
        return content

    def generate_strategy_charts(self, analysis_data: Dict[str, Any], output_path: str) -> str:
        """
        Génère des graphiques Matplotlib illustrant la stratégie
        """
        logger.info(f"Generating Matplotlib charts at {output_path}")
        
        gaps = analysis_data.get("research_gaps", [])
        if not gaps:
            return ""

        # Chart 1: Importance Score of Research Gaps
        descriptions = [g.get("gap_description", "")[:30] + "..." for g in gaps]
        scores = [g.get("importance_score", 0.5) * 100 for g in gaps]

        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        bars = plt.barh(descriptions, scores, color='#3b82f6')
        plt.xlabel('Importance Score (%)')
        plt.title('Identified Research Gaps - Priority Map')
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        plt.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, transparent=True)
        plt.close()
        
        return output_path
