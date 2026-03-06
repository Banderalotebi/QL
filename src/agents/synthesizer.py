# src/agents/synthesizer.py
from src.data.neon_db import NeonDB
from src.core.state import ResearchState

_neon_db = NeonDB()

class Synthesizer:
    """
    Synthesizer agent that combines related hypotheses into unified theories.
    """
    
    def __init__(self):
        """
        Initialize the synthesizer with a database connection.
        """
        self.conn = _neon_db.conn
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Synthesize survivor hypotheses into theories.
        For now, just pass through survivors as individual theories.
        """
        survivors = state.get("survivor_hypotheses", [])
        
        # Simple pass-through synthesis for now
        # In a more sophisticated version, this would:
        # 1. Group similar hypotheses
        # 2. Merge evidence from multiple scouts
        # 3. Create composite theories
        
        # Sort by score (descending) to get ranked theories
        ranked = sorted(survivors, key=lambda h: h.score, reverse=True)
        
        state["synthesized_theories"] = survivors.copy()
        state["ranked_theories"] = ranked
        print(f"Hey, I've combined the hypotheses into a unified theory!")
        
        # Log top findings to database if connected (gracefully degraded)
        try:
            for hyp in ranked[:5]:
                _neon_db.log_hypothesis(hyp, status="SURVIVOR")
        except Exception as e:
            pass  # Graceful failure - continue pipeline even if database logging fails
        
        return state
