import sys

# Add the missing import
from src.core.scorer import (
    occam_score, 
    compute_evidence_weight, 
    compute_goal_alignment_bonus,
    score_hypothesis,
    rank_theories,
    LAMBDA
)
