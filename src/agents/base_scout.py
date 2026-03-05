from abc import ABC, abstractmethod
from src.core.state import ResearchState, Hypothesis

class BaseScout(ABC):
    """Base class for all Scout agents."""
    
    name: str = "BaseScout"
    consumes_rasm: bool = True
    consumes_tashkeel: bool = False
    
    def run(self, state: ResearchState) -> ResearchState:
        """Standard run method that calls analyze and appends to raw_hypotheses."""
        hypotheses = self.analyze(state)
        
        # Validate each hypothesis has non-empty goal_link
        for h in hypotheses:
            if not h.goal_link.strip():
                raise ValueError(f"{self.name} produced hypothesis with empty goal_link")
        
        # Append to raw_hypotheses
        raw_hypotheses = state.get("raw_hypotheses", [])
        raw_hypotheses.extend(hypotheses)
        state["raw_hypotheses"] = raw_hypotheses
        
        return state
    
    @abstractmethod
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """Analyze the data and return hypotheses. Must be implemented by subclasses."""
        pass
