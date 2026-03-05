# src/core/scorer.py
# Occam Razor scoring for the Muqattaat Cryptanalytic Lab

import math
import requests
from typing import Sequence
from src.core.state import ResearchState

# ── Constants ────────────────────────────────────────────────────────────────

CHAT_OLLAMA_API_URL = "https://api.chatollama.com/v1"

# Restoring required constants for the scoring formula
LAMBDA: float = 0.15
"""
Occam complexity penalty rate. Non-negotiable per CONVENTIONS.md.
A theory needing >5 transformations starts below 0.47 regardless of evidence.
"""

GOAL_ALIGNMENT_BONUS: float = 0.10
"""
Bonus added when a hypothesis explicitly targets the Muqattaat sequences
(i.e. surah_refs overlap with known Muqattaat Surahs).
"""

MUQATTAAT_SURAH_NUMBERS: frozenset[int] = frozenset(
    [2, 3, 7, 10, 11, 12, 13, 14, 15, 19, 20, 26, 27, 28, 29, 30, 31, 32,
     36, 38, 40, 41, 42, 43, 44, 45, 46, 50, 68]
)

# ── Core formula ─────────────────────────────────────────────────────────────

def occam_score(
    evidence_weight: float,
    transformation_steps: int,
    goal_alignment_bonus: float = 0.0,
) -> float:
    """
    Compute the Occam-penalised score for a hypothesis.

    Formula (from CONVENTIONS.md):
        score = evidence_weight * exp(-λ * transformation_steps) + bonus

    Args:
        evidence_weight: A value in [0.0, 1.0] representing how strong the
            evidence is. 1.0 = maximally supported, 0.0 = no evidence.
        transformation_steps: Number of logical operations applied. More steps
            → heavier penalty.
        goal_alignment_bonus: Extra credit for hypotheses that directly target
            the Muqattaat. Added AFTER the exponential penalty.

    Returns:
        Float score. Typically in [0.0, 1.1] but not clamped — callers may
        normalise if needed.
    """
    if not (0.0 <= evidence_weight <= 1.0):
        raise ValueError(
            f"evidence_weight must be in [0.0, 1.0], got {evidence_weight}."
        )
    if transformation_steps < 0:
        raise ValueError(
            f"transformation_steps must be >= 0, got {transformation_steps}."
        )

    penalty = math.exp(-LAMBDA * transformation_steps)
    return evidence_weight * penalty + goal_alignment_bonus


# ── Evidence weight helpers ───────────────────────────────────────────────────

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

    # Penalise circular hypotheses (description mirrors goal_link)
    if hypothesis.description.strip() == hypothesis.goal_link.strip():
        base *= 0.5

    # Bonus if all referenced Surahs are Muqattaat Surahs
    if hypothesis.surah_refs and all(
        s in MUQATTAAT_SURAH_NUMBERS for s in hypothesis.surah_refs
    ):
        base = min(base + 0.1, 1.0)

    return base


def compute_goal_alignment_bonus(hypothesis: Hypothesis) -> float:
    """
    Return GOAL_ALIGNMENT_BONUS if the hypothesis goal_link explicitly
    references Muqattaat concepts, else 0.0.
    """
    goal_lower = hypothesis.goal_link.lower()
    if any(kw in goal_lower for kw in _MUQATTAAT_KEYWORDS):
        return GOAL_ALIGNMENT_BONUS
    return 0.0


# ── Scorer entry point ────────────────────────────────────────────────────────

def score_hypothesis(hypothesis: Hypothesis) -> Hypothesis:
    """
    Score a single Hypothesis in-place (mutates `.score`) and return it.

    Steps:
    1. Compute evidence_weight from evidence_snippets and metadata.
    2. Compute goal_alignment_bonus.
    3. Apply occam_score formula.
    4. Store result in hypothesis.score.
    """
    ew = compute_evidence_weight(hypothesis)
    bonus = compute_goal_alignment_bonus(hypothesis)
    hypothesis.score = occam_score(
        evidence_weight=ew,
        transformation_steps=hypothesis.transformation_steps,
        goal_alignment_bonus=bonus,
    )
    return hypothesis


def rank_theories(theories: Sequence[Hypothesis]) -> list[Hypothesis]:
    """
    Return a new list of Hypothesis objects sorted by score descending.

    Args:
        theories: Any sequence of scored Hypothesis instances.

    Returns:
        List sorted highest score first.
    """
    return sorted(theories, key=lambda h: h.score, reverse=True)


def score_all(hypotheses: Sequence[Hypothesis]) -> list[Hypothesis]:
    """
    Score every hypothesis in the sequence and return them ranked.

    Args:
        hypotheses: Unscored (or partially scored) Hypothesis instances.

    Returns:
        All hypotheses with `.score` populated, sorted descending by score.
    """
    scored = [score_hypothesis(h) for h in hypotheses]
    return rank_theories(scored)
