# src/core/scorer.py
# Occam Razor scoring for the Muqattaat Cryptanalytic Lab

import math
import requests
from typing import Sequence
from src.core.state import ResearchState, Hypothesis
from src.data.neon_db import NeonDB

_neon_db = NeonDB()  # Add this line to import _neon_db

def occam_score(hypothesis: Hypothesis) -> float:
    """
    Compute the Occam score for a given Hypothesis.

    Heuristic rules (can be refined as the lab matures):
    - Base score = 1.0 / (transformation_steps + 1)
    - Penalty if description == goal_link (circular reasoning)
    - Bonus if surah_refs are all Muqattaat Surahs
    """
    base = 1.0 / (hypothesis.transformation_steps + 1)

    # Check if the hypothesis goal_link contains any "Meaning Anchors"
    if any(keyword in hypothesis.goal_link.lower() for keyword in ["muqattaat dna", "jeddah coordinates", "dna base pairs"]):
        # Reward the hypothesis with a bonus score
        base += 0.1

    # Check if the hypothesis is a rejected hypothesis
    if hypothesis in _neon_db.get_rejected_hypotheses():
        return 0.0

    return base
