"""
tests/test_scorer.py
───────────────────
Tests for the Occam Razor scoring system.
"""

import pytest
import math
from src.core.scorer import (
    occam_score, 
    compute_evidence_weight, 
    compute_goal_alignment_bonus,
    score_hypothesis,
    rank_theories,
    LAMBDA
)
from src.core.state import Hypothesis


def create_test_hypothesis(
    steps: int = 1,
    evidence_count: int = 3,
    goal_link: str = "Muqattaat letters Alif-Lam-Mim dominate frequency patterns.",
    surah_refs: list[int] = None
) -> Hypothesis:
    """Create a test hypothesis with specified parameters."""
    if surah_refs is None:
        surah_refs = [2]
    
    return Hypothesis(
        source_scout="TestScout",
        goal_link=goal_link,
        description="Test description",
        transformation_steps=steps,
        evidence_snippets=[f"Evidence {i}" for i in range(evidence_count)],
        surah_refs=surah_refs,
        layer="rasm"
    )


def test_zero_step_hypothesis_high_score():
    """Test that a 0-step hypothesis with full evidence scores > 0.8."""
    h = create_test_hypothesis(steps=0, evidence_count=5)
    scored = score_hypothesis(h)
    
    assert scored.score > 0.8, f"0-step hypothesis should score > 0.8, got {scored.score}"


def test_ten_step_hypothesis_low_score():
    """Test that a 10-step hypothesis scores < 0.5."""
    h = create_test_hypothesis(steps=10, evidence_count=5)
    scored = score_hypothesis(h)
    
    assert scored.score < 0.5, f"10-step hypothesis should score < 0.5, got {scored.score}"


def test_goal_alignment_bonus_added():
    """Test that goal_alignment_bonus is added for Muqattaat-targeting hypotheses."""
    # Hypothesis with Muqattaat keywords
    h_muqattaat = create_test_hypothesis(
        steps=1,
        goal_link="Muqattaat letters Alif-Lam-Mim reveal the phonetic key to the chapter.",
        surah_refs=[2]  # Muqattaat Surah
    )
    
    # Hypothesis without Muqattaat keywords
    h_generic = create_test_hypothesis(
        steps=1,
        goal_link="This pattern shows interesting frequency distributions in the text.",
        surah_refs=[2]
    )
    
    scored_muqattaat = score_hypothesis(h_muqattaat)
    scored_generic = score_hypothesis(h_generic)
    
    # The Muqattaat-focused hypothesis should score higher due to bonus
    assert scored_muqattaat.score > scored_generic.score, \
        "Muqattaat-focused hypothesis should score higher due to goal alignment bonus"


def test_rank_theories_descending_order():
    """Test that rank_theories returns theories in descending score order."""
    hypotheses = [
        create_test_hypothesis(steps=5),  # Lower score
        create_test_hypothesis(steps=0),  # Higher score
        create_test_hypothesis(steps=3),  # Medium score
    ]
    
    # Score all hypotheses
    scored = [score_hypothesis(h) for h in hypotheses]
    
    # Rank them
    ranked = rank_theories(scored)
    
    # Should be in descending order
    for i in range(len(ranked) - 1):
        assert ranked[i].score >= ranked[i + 1].score, \
            f"Theories not in descending order: {ranked[i].score} < {ranked[i + 1].score}"


def test_occam_formula_correctness():
    """Test that the Occam formula matches the specification."""
    evidence_weight = 0.8
    steps = 3
    bonus = 0.1
    
    expected = evidence_weight * math.exp(-LAMBDA * steps) + bonus
    actual = occam_score(evidence_weight, steps, bonus)
    
    assert abs(actual - expected) < 1e-10, \
        f"Occam formula incorrect: expected {expected}, got {actual}"


def test_lambda_constant():
    """Test that LAMBDA = 0.15 as specified in CONVENTIONS.md."""
    assert LAMBDA == 0.15, f"LAMBDA must be 0.15, got {LAMBDA}"


def test_evidence_weight_calculation():
    """Test evidence weight calculation heuristics."""
    # Hypothesis with 5 evidence snippets (should get full weight)
    h_full = create_test_hypothesis(evidence_count=5)
    weight_full = compute_evidence_weight(h_full)
    assert weight_full == 1.0, f"5 evidence snippets should give weight 1.0, got {weight_full}"
    
    # Hypothesis with 2 evidence snippets
    h_partial = create_test_hypothesis(evidence_count=2)
    weight_partial = compute_evidence_weight(h_partial)
    expected_partial = 2.0 / 5.0  # min(2/5, 1.0)
    assert abs(weight_partial - expected_partial) < 1e-10, \
        f"2 evidence snippets should give weight {expected_partial}, got {weight_partial}"


def test_goal_alignment_bonus_detection():
    """Test goal alignment bonus detection for various keywords."""
    test_cases = [
        ("Muqattaat letters reveal patterns", True),
        ("isolated letter sequences show structure", True),
        ("الحروف المقطعة contain meaning", True),
        ("Alif Lam Mim frequency analysis", True),
        ("phonetic key discovered in opening letters", True),
        ("General frequency analysis of text", False),
        ("Statistical patterns in Arabic", False),
    ]
    
    for goal_link, should_have_bonus in test_cases:
        h = create_test_hypothesis(goal_link=goal_link)
        bonus = compute_goal_alignment_bonus(h)
        
        if should_have_bonus:
            assert bonus > 0, f"'{goal_link}' should have goal alignment bonus"
        else:
            assert bonus == 0, f"'{goal_link}' should not have goal alignment bonus"


def test_muqattaat_surah_bonus():
    """Test that hypotheses referencing Muqattaat Surahs get bonus."""
    # Hypothesis referencing Muqattaat Surah
    h_muqattaat = create_test_hypothesis(surah_refs=[2, 19])  # Both are Muqattaat Surahs
    weight_muqattaat = compute_evidence_weight(h_muqattaat)
    
    # Hypothesis referencing non-Muqattaat Surah
    h_regular = create_test_hypothesis(surah_refs=[1])  # Surah 1 has no Muqattaat
    weight_regular = compute_evidence_weight(h_regular)
    
    # Muqattaat Surah references should get bonus
    assert weight_muqattaat > weight_regular, \
        "Hypotheses referencing Muqattaat Surahs should get evidence weight bonus"


if __name__ == "__main__":
    pytest.main([__file__])
