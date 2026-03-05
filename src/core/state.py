# src/core/state.py
import operator
from typing import TypedDict, List, Dict, Any, Annotated, Optional
from dataclasses import dataclass, field

@dataclass
class Hypothesis:
    source_scout: str
    goal_link: str
    transformation_steps: int
    evidence_snippets: List[str]
    description: str = ""
    score: float = 0.0
    surah_refs: List[int] = field(default_factory=list)

@dataclass
class RejectedHypothesis:
    hypothesis: Hypothesis
    reason: str

class ResearchState(TypedDict, total=False):
    surah_numbers: List[int]
    focus: str
    
    # LangGraph Reducers: ensures parallel agent results are merged
    raw_hypotheses: Annotated[List[Hypothesis], operator.add]
    survivor_hypotheses: Annotated[List[Hypothesis], operator.add]
    synthesized_theories: Annotated[List[Hypothesis], operator.add]
    scored_theories: Annotated[List[Hypothesis], operator.add]
    errors: Annotated[List[str], operator.add]
    known_dead_ends: Annotated[List[Any], operator.add]
    rejected_hypotheses: Annotated[List[RejectedHypothesis], operator.add]
    
    # Run Metadata
    input_surah_numbers: List[int]
    input_focus: str
    data_dir: str
    run_id: str
    lab_report: Dict[str, Any]

