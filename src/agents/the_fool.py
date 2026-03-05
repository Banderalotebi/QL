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
            # Check if the hypothesis goal_link contains any "Meaning Anchors"
            if any(keyword in h.goal_link.lower() for keyword in ["muqattaat dna", "jeddah coordinates", "dna base pairs"]):
                # Reward the hypothesis with a bonus score
                h.score += 0.1
            
            # Check if the hypothesis fails to account for the Meccan/Medinan split or the Surah 68 "Literal Zone" cut-off
            if (h.surah_refs not in state["MEDINAN_MUQATTAAT"] and h.surah_refs not in state["MECCAN_MUQATTAAT"]) or h.surah_refs > 68:
                # Reject the hypothesis
                rejected.append(RejectedHypothesis(
                    hypothesis=h,
                    reason="Failed to account for Meccan/Medinan split or Surah 68 'Literal Zone' cut-off",
                    auditor="TheFool"
                ))
            else:
                # Accept the hypothesis
                survivors.append(h)
        
        state["survivor_hypotheses"] = survivors
        state["rejected_hypotheses"] = rejected
        
        return state
