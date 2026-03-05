"""
Scorer module for hypothesis evaluation and ranking.

This module provides functions for scoring and ranking hypotheses
based on Occam's razor principles, evidence weight, and goal alignment.
"""

import sys

# Add the missing import
from src.utils.arabic import MUQATTAAT_SURAH_NUMBERS

# Occam's razor regularization parameter
LAMBDA = 0.1


def occam_score(hypothesis: str, complexity: int = None) -> float:
    """
    Calculate an Occam's razor score for a hypothesis.
    
    Simpler hypotheses are preferred over complex ones.
    
    Args:
        hypothesis: The hypothesis string to evaluate
        complexity: Optional explicit complexity measure (e.g., number of components)
    
    Returns:
        A score where lower complexity yields higher scores
    """
    if complexity is None:
        # Calculate complexity as the length of the hypothesis
        complexity = len(hypothesis)
    
    # Apply Occam's razor: simpler is better
    # Using exponential decay: score = e^(-lambda * complexity)
    import math
    return math.exp(-LAMBDA * complexity)


def compute_evidence_weight(hypothesis) -> float:
    """
    Compute the evidence weight for a hypothesis.
    
    Args:
        hypothesis: A dictionary containing hypothesis data with evidence
    
    Returns:
        A weight value based on the strength of supporting evidence
    """
    if isinstance(hypothesis, dict):
        evidence = hypothesis.get('evidence', [])
    else:
        evidence = []
    
    if not evidence:
        return 0.0
    
    # Calculate weight based on number and quality of evidence
    # Each piece of evidence contributes positively
    weight = min(len(evidence) * 0.5, 1.0)  # Cap at 1.0
    
    return weight


def compute_goal_alignment_bonus(hypothesis, goals=None) -> float:
    """
    Compute a bonus for how well the hypothesis aligns with goals.
    
    Args:
        hypothesis: A dictionary containing hypothesis data
        goals: Optional list of goal strings to check alignment against
    
    Returns:
        A bonus value (0.0 to 1.0) based on goal alignment
    """
    if goals is None:
        goals = []
    
    if isinstance(hypothesis, dict):
        hypothesis_text = str(hypothesis.get('description', hypothesis))
    else:
        hypothesis_text = str(hypothesis)
    
    if not goals:
        return 0.0
    
    # Check how many goals the hypothesis addresses
    aligned_count = sum(1 for goal in goals if goal.lower() in hypothesis_text.lower())
    
    return aligned_count / len(goals)


def score_hypothesis(hypothesis, goals=None) -> float:
    """
    Calculate an overall score for a hypothesis.
    
    Combines Occam's razor score, evidence weight, and goal alignment bonus.
    
    Args:
        hypothesis: A dictionary containing hypothesis data
        goals: Optional list of goal strings
    
    Returns:
        A composite score (0.0 to ~2.0)
    """
    # Get component scores
    occam = occam_score(str(hypothesis))
    evidence = compute_evidence_weight(hypothesis)
    goal_bonus = compute_goal_alignment_bonus(hypothesis, goals)
    
    # Combine scores (weighted average)
    total_score = occam + evidence + goal_bonus
    
    return total_score


def rank_theories(hypotheses, goals=None) -> list:
    """
    Rank a list of hypotheses by their scores.
    
    Args:
        hypotheses: A list of hypothesis dictionaries
        goals: Optional list of goal strings
    
    Returns:
        A list of hypotheses sorted by score (highest first)
    """
    scored = []
    
    for hypothesis in hypotheses:
        score = score_hypothesis(hypothesis, goals)
        scored.append((hypothesis, score))
    
    # Sort by score in descending order
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the hypotheses in ranked order
    return [h for h, s in scored]
