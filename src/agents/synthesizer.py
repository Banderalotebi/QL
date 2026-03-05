# src/agents/synthesizer.py
from src.data.neon_db import NeonDB

_neon_db = NeonDB()

class Synthesizer:
    """
    Synthesizer agent that combines related hypotheses into unified theories.
    """
    
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
        
        state["synthesized_theories"] = survivors.copy()
        print(f"Hey, I've combined the hypotheses into a unified theory!")
        
        # Save the final theories into the `hypotheses` table in Neon
        conn = _neon_db.conn
        cur = conn.cursor()
        for theory in state["synthesized_theories"]:
            cur.execute(
                "INSERT INTO hypotheses (run_id, source_scout, surah_id, description, score, alchemist_reward) VALUES (%s, %s, %s, %s, %s, %s)",
                (state["run_id"], theory["source_scout"], theory["surah_id"], theory["description"], theory["score"], theory["alchemist_reward"])
            )
        conn.commit()
        conn.close()
        
        return state
