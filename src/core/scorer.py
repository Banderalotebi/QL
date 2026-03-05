# src/core/scorer.py
# Occam Razor scoring for the Muqattaat Cryptanalytic Lab

import math
import requests
from typing import Sequence
from src.core.state import ResearchState
from src.data.neon_db import NeonDB

_neon_db = NeonDB()

# ...

def compute_evidence_weight(hypothesis: Hypothesis) -> float:
    """
    Derive an evidence_weight in [0.0, 1.0] from a Hypothesis.

    Heuristic rules (can be refined as the lab matures):
    - Base weight = min(len(evidence_snippets) / 5, 1.0)
      (5 or more distinct snippets → full weight)
    - Penalty if description == goal_link (circular reasoning)
    - Bonus if surah_refs are all Muqattaat Surahs
    """
    base = min(len(hypothesis.evidence_snippets) / 5.0, 1.0)

    # ...

    # Check if the hypothesis goal_link contains any "Meaning Anchors"
    if any(keyword in hypothesis.goal_link.lower() for keyword in ["muqattaat dna", "jeddah coordinates", "dna base pairs"]):
        # Reward the hypothesis with a bonus score
        base += 0.1

    # Check if the hypothesis is a rejected hypothesis
    if hypothesis in _neon_db.get_rejected_hypotheses():
        return 0.0

    return base
