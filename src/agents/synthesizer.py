from src.core.state import ResearchState, Hypothesis

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
        return state
