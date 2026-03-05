# src/core/leaders.py
# Dual-leadership supervisors for the Muqattaat Cryptanalytic Lab

from __future__ import annotations

from src.core.state import ResearchState
from src.agents.micro_scout import MicroScout
from src.agents.static_scout import StaticScout
from src.agents.linguistic_scout import LinguisticScout
from src.agents.symbolic_scout import SymbolicScout
from src.agents.math_scout import MathScout
from src.agents.freq_scout import FreqScout
from src.agents.deep_scout import DeepScout
from src.agents.the_fool import TheFool
from src.agents.synthesizer import Synthesizer

class ExecutionerLeader:
    """
    Executioner leader that monitors performance metrics from scorer.py.
    If scores drop below 0.85, trigger a "Factory Spawn" for a new specialist agent.
    """
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Monitor performance metrics and trigger factory spawn if necessary.
        """
        # Implement dynamic respawning of Scouts with modified prompts
        # Get the current scores from the scorer
        scores = state.get("scores", [])
        
        # Check if any scores are below 0.85
        if any(score < 0.85 for score in scores):
            # Trigger factory spawn for a new specialist agent
            # Create a new MicroScout with a modified prompt
            new_scout = MicroScout(prompt="Modified prompt")
            # Add the new scout to the state
            state["scouts"].append(new_scout)
        
        return state

class AlchemistLeader:
    """
    Alchemist leader that audits goal_link fields to ensure they connect to "Meaning Anchors" like Muqattaat DNA or astronomical coordinates.
    """
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Audit goal_link fields and update state accordingly.
        """
        # Implement reward mechanism for hypotheses that map letters to physical, geographical, or biological realities
        # Get the current hypotheses from the state
        hypotheses = state.get("hypotheses", [])
        
        # Iterate over the hypotheses
        for hypothesis in hypotheses:
            # Check if the goal_link field contains any "Meaning Anchors"
            if any(keyword in hypothesis.goal_link.lower() for keyword in ["muqattaat dna", "jeddah coordinates", "dna base pairs"]):
                # Reward the hypothesis with a bonus score
                hypothesis.score += 0.1
        
        return state
