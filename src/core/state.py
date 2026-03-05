# src/core/state.py
from typing import TypedDict, List, Dict, Any
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

class ResearchState(TypedDict, total=False):
    surah_numbers: List[int]
    focus: str
    raw_hypotheses: List[Hypothesis]
    survivor_hypotheses: List[Hypothesis]
    synthesized_theories: List[Hypothesis]
    scored_theories: List[Hypothesis]
    errors: List[str]
    
    # Required by main.py
    input_surah_numbers: List[int]
    input_focus: str
    data_dir: str
    run_id: str
    known_dead_ends: List[Any]
    rejected_hypotheses: List[Any]
    lab_report: Dict[str, Any]
