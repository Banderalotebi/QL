"""
src/core/scorer.py
──────────────────
Occam's Razor evaluation function.

Formula:
    score = evidence_weight * exp(-λ * transformation_steps)

λ (lambda) default = 0.15
A theory requiring >5 transformations scores below 0.47 regardless of evidence.
This mathematically forces the system to favor simple, elegant truths.

PRIMARY GOAL ALIGNMENT:
The scorer adds a `goal_alignment_bonus` when a hypothesis directly
addresses the Muqattaat's meaning (not just statistical patterns around them).
"""

from __future__ import annotations
import math
from src.core.state import Hypothesis

# ── Tuning constants ──────────────────────────────────────────────────────────
LAMBDA: float = 0.15          # Complexity penalty decay rate
GOAL_BONUS: float = 0.20      # Bonus for direct Muqattaat meaning hypothesis
MAX_EVIDENCE_WEIGHT: float = 1.0


# ── Keyword signals that a hypothesis directly addresses Muqattaat meaning ────
DIRECT_MEANING_SIGNALS = [
    "meaning of", "stands for", "abbreviation", "cipher key",
    "decode", "represents", "symbolic of", "geometric key",
    "phonetic key", "mathematical key", "numerical value",
    "abjad", "letter name", "isolated letter"
]


def compute_evidence_weight(hypothesis: Hypothesis) -> float:
    """
    Estimate evidence weight from 0.0 to 1.0 based on:
    - Number of evidence snippets
    - Number of Surah references (cross-Surah = stronger)
    - Whether it has both Rasm + phonetic corroboration (metadata flag)
    """
    snippet_score = min(len(hypothesis.evidence_snippets) / 5.0, 0.6)
    surah_score = min(len(set(hypothesis.surah_refs)) / 10.0, 0.3)
    dual_layer_bonus = 0.1 if hypothesis.metadata.get("dual_layer_corroborated") else 0.0
    return round(snippet_score + surah_score + dual_layer_bonus, 4)


def goal_alignment_bonus(hypothesis: Hypothesis) -> float:
    """
    Add a bonus if the hypothesis directly targets Muqattaat meaning discovery.
    Checks both description and goal_link for signal words.
    """
    combined = (hypothesis.description + hypothesis.goal_link).lower()
    if any(signal in combined for signal in DIRECT_MEANING_SIGNALS):
        return GOAL_BONUS
    return 0.0


def score_hypothesis(hypothesis: Hypothesis, lam: float = LAMBDA) -> Hypothesis:
    """
    Apply the Occam Razor formula and write the score back onto the hypothesis.

    score = evidence_weight * exp(-λ * steps) + goal_alignment_bonus
    Capped at 1.0.
    """
    ew = compute_evidence_weight(hypothesis)
    steps = max(hypothesis.transformation_steps, 0)
    complexity_penalty = math.exp(-lam * steps)
    bonus = goal_alignment_bonus(hypothesis)

    raw_score = (ew * complexity_penalty) + bonus
    hypothesis.score = round(min(raw_score, 1.0), 4)
    return hypothesis


def rank_theories(theories: list[Hypothesis]) -> list[Hypothesis]:
    """Return theories sorted descending by score."""
    scored = [score_hypothesis(h) for h in theories]
    return sorted(scored, key=lambda h: h.score, reverse=True)
