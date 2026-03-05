# src/agents/the_fool.py
# The Fool - Quality control agent that interrogates hypotheses for logical rigor.

from src.core.state import ResearchState, Hypothesis, RejectedHypothesis
import requests

class TheFool:
    """
    The Fool - Quality control agent that interrogates hypotheses for logical rigor.
    Rejects hypotheses with generic goal_link, circular reasoning, or insufficient evidence.
    """
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Interrogate all raw hypotheses and separate survivors from rejects.
        """
        raw_hypotheses = state.get("raw_hypotheses", [])
        survivors = []
        rejected = []
        
        # Iterate over the raw hypotheses
        for h in raw_hypotheses:
            # Use Ollama to try to logically dismantle the hypothesis
            ollama_response = requests.post("https://api.chatollama.com/v1", json={"prompt": h.goal_link})
            ollama_response.raise_for_status()
            ollama_response_json = ollama_response.json()
            
            # Check if the Ollama response contains any logical flaws
            if any(flaw in ollama_response_json["output"] for flaw in ["circular reasoning", "insufficient evidence"]):
                # Reject the hypothesis
                rejected.append(RejectedHypothesis(
                    hypothesis=h,
                    reason="Logical flaw detected",
                    auditor="TheFool"
                ))
            else:
                # Accept the hypothesis
                survivors.append(h)
        
        state["survivor_hypotheses"] = survivors
        state["rejected_hypotheses"] = rejected
        
        return state
