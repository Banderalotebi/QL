"""
tests/test_scouts.py
───────────────────
Tests for Scout agents to ensure they follow the architecture rules.
"""

import pytest
from src.core.state import ResearchState, Hypothesis
from src.agents.micro_scout import MicroScout
from src.agents.math_scout import MathScout


def create_test_state() -> ResearchState:
    """Create a test state with sample Muqattaat Surah data."""
    return {
        "surah_numbers": [2, 19],
        "rasm_matrices": {
            2: ["ا", "ل", "م", "ذ", "ل", "ك", "ا", "ل", "ك", "ت", "ا", "ب"],
            19: ["ك", "ه", "ي", "ع", "ص", "ذ", "ك", "ر", "ر", "ح", "م", "ت"]
        },
        "tashkeel_matrices": {
            2: ["CVCCVCVCVCVC"],  # Phonetic rhythm
            19: ["CVCCVCVCVCVC"]
        },
        "muqattaat_map": {
            2: "الم",
            19: "كهيعص"
        },
        "raw_hypotheses": [],
        "known_dead_ends": [],
        "errors": []
    }


def test_micro_scout_returns_hypotheses():
    """Test that MicroScout returns at least 1 hypothesis for Muqattaat Surah."""
    scout = MicroScout()
    state = create_test_state()
    
    hypotheses = scout.analyze(state)
    
    assert len(hypotheses) >= 1, "MicroScout should return at least 1 hypothesis"
    
    for h in hypotheses:
        assert isinstance(h, Hypothesis), "Should return Hypothesis objects"
        assert h.goal_link.strip(), "Goal link must not be empty"
        assert len(h.goal_link) > 20, "Goal link must be substantial"


def test_math_scout_returns_hypotheses():
    """Test that MathScout returns at least 1 hypothesis for Muqattaat Surah."""
    scout = MathScout()
    state = create_test_state()
    
    hypotheses = scout.analyze(state)
    
    assert len(hypotheses) >= 1, "MathScout should return at least 1 hypothesis"
    
    for h in hypotheses:
        assert isinstance(h, Hypothesis), "Should return Hypothesis objects"
        assert h.goal_link.strip(), "Goal link must not be empty"
        assert "abjad" in h.goal_link.lower() or "mathematical" in h.goal_link.lower(), \
            "MathScout goal_link should mention mathematical concepts"


def test_all_scouts_have_non_empty_goal_links():
    """Test that all scouts produce hypotheses with non-empty goal_link."""
    scouts = [
        MicroScout(),
        MathScout()
    ]
    
    state = create_test_state()
    
    for scout in scouts:
        hypotheses = scout.analyze(state)
        
        for h in hypotheses:
            assert h.goal_link.strip(), f"{scout.name} produced hypothesis with empty goal_link"
            assert len(h.goal_link) >= 20, f"{scout.name} goal_link too short: '{h.goal_link}'"


def test_rasm_scouts_only_access_rasm_matrices():
    """Test that Rasm-only scouts do NOT access tashkeel_matrices."""
    rasm_scouts = [
        MicroScout(),
        MathScout()
    ]
    
    state = create_test_state()
    
    for scout in rasm_scouts:
        assert scout.consumes_rasm == True, f"{scout.name} should consume rasm"
        assert scout.consumes_tashkeel == False, f"{scout.name} should not consume tashkeel"
        
        # Run the scout and verify it doesn't crash when tashkeel is missing
        state_no_tashkeel = state.copy()
        state_no_tashkeel["tashkeel_matrices"] = {}
        
        hypotheses = scout.analyze(state_no_tashkeel)
        # Should still work without tashkeel data
        assert isinstance(hypotheses, list), f"{scout.name} should work without tashkeel data"


def test_scouts_produce_valid_layer_assignments():
    """Test that scouts assign correct layer to their hypotheses."""
    scouts = [
        (MicroScout(), "rasm"),
        (MathScout(), "rasm")
    ]
    
    state = create_test_state()
    
    for scout, expected_layer in scouts:
        hypotheses = scout.analyze(state)
        
        for h in hypotheses:
            assert h.layer == expected_layer, \
                f"{scout.name} should produce {expected_layer} layer hypotheses, got {h.layer}"


def test_scouts_reference_muqattaat_surahs():
    """Test that scouts reference Muqattaat Surahs in their hypotheses."""
    scouts = [
        MicroScout(),
        MathScout()
    ]
    
    state = create_test_state()
    
    for scout in scouts:
        hypotheses = scout.analyze(state)
        
        for h in hypotheses:
            # Should reference at least one of the Muqattaat Surahs in the test state
            assert any(surah in [2, 19] for surah in h.surah_refs), \
                f"{scout.name} should reference Muqattaat Surahs 2 or 19"


def test_scouts_have_transformation_steps():
    """Test that all scouts assign reasonable transformation_steps."""
    scouts = [
        MicroScout(),
        MathScout()
    ]
    
    state = create_test_state()
    
    for scout in scouts:
        hypotheses = scout.analyze(state)
        
        for h in hypotheses:
            assert h.transformation_steps >= 0, \
                f"{scout.name} transformation_steps must be >= 0, got {h.transformation_steps}"
            assert h.transformation_steps <= 10, \
                f"{scout.name} transformation_steps seems too high: {h.transformation_steps}"


if __name__ == "__main__":
    pytest.main([__file__])
