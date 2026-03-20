"""
Reasoning Trace Logger
"""
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.reasoning_trace import ReasoningTrace


class ReasoningLogger:
    """Logger pour tracer le raisonnement K2 Think"""
    
    def __init__(self, db: Session):
        self.db = db
        self.traces: List[Dict[str, Any]] = []
    
    def log_step(
        self,
        phase: str,
        step: str,
        description: str,
        input_data: Dict = None,
        output_data: Dict = None,
        reasoning: str = None
    ):
        """Enregistre une étape de raisonnement"""
        trace = {
            "phase": phase,
            "step": step,
            "description": description,
            "input_data": input_data,
            "output_data": output_data,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.traces.append(trace)
    
    def save_traces(self, analysis_id: int = None, protocol_id: int = None):
        """Sauvegarde les traces en base de données"""
        for trace in self.traces:
            db_trace = ReasoningTrace(
                analysis_id=analysis_id,
                protocol_id=protocol_id,
                phase=trace["phase"],
                step=trace["step"],
                description=trace["description"],
                input_data=str(trace.get("input_data", "")),
                output_data=str(trace.get("output_data", "")),
                reasoning=trace.get("reasoning", ""),
                model_used="K2_Think_V2"
            )
            self.db.add(db_trace)
        
        self.db.commit()
    
    def get_traces(self) -> List[Dict[str, Any]]:
        """Retourne les traces enregistrées"""
        return self.traces
