"""
tests/test_ingestion.py
──────────────────────
Tests for the dual-layer ingestion pipeline.
"""

import pytest
from src.data.ingestion import extract_rasm, isolate_muqattaat, ingest_surah
from src.utils.arabic import strip_basmalah, arabic_letters_only, detect_muqattaat_in_text


def test_extract_rasm_strips_diacritics():
    """Test that extract_rasm correctly strips all diacritics."""
    # Text with diacritics
    text_with_diacritics = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    # Expected result without diacritics
    expected = "بسم الله الرحمن الرحيم"
    
    result = extract_rasm(text_with_diacritics)
    assert result == expected, f"Expected '{expected}', got '{result}'"


def test_isolate_muqattaat_surah_2():
    """Test that isolate_muqattaat returns correct sequence for Surah 2 (الم)."""
    # Sample text from Surah 2 starting with الم
    sample_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الم ذَٰلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ"
    
    result = isolate_muqattaat(sample_text, 2)
    assert result == ["الم"], f"Expected ['الم'], got {result}"


def test_detect_muqattaat_in_text_surah_2():
    """Test detect_muqattaat_in_text for Surah 2."""
    sample_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الم ذَٰلِكَ الْكِتَابُ"
    
    result = detect_muqattaat_in_text(sample_text, 2)
    assert result == "الم", f"Expected 'الم', got {result}"


def test_layer_separation():
    """Test that Layer A (rasm) and Layer B (tashkeel) never share the same data object."""
    sample_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الم ذَٰلِكَ الْكِتَابُ"
    
    rasm, tashkeel, muqattaat, raw = ingest_surah(2, sample_text)
    
    # Ensure they are different objects
    assert rasm is not tashkeel, "Rasm and Tashkeel matrices must be separate objects"
    assert id(rasm) != id(tashkeel), "Rasm and Tashkeel must have different memory addresses"
    
    # Ensure they have different types/structures
    assert isinstance(rasm, list), "Rasm should be a list of letters"
    assert isinstance(tashkeel, list), "Tashkeel should be a list"
    
    # Modify one and ensure the other is unaffected
    original_rasm_len = len(rasm) if rasm else 0
    original_tashkeel_len = len(tashkeel) if tashkeel else 0
    
    if rasm:
        rasm.append("test")
        assert len(tashkeel) == original_tashkeel_len, "Modifying rasm should not affect tashkeel"


def test_strip_basmalah():
    """Test that strip_basmalah correctly removes Basmalah."""
    text_with_basmalah = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الم ذَٰلِكَ الْكِتَابُ"
    expected = "الم ذَٰلِكَ الْكِتَابُ"
    
    result = strip_basmalah(text_with_basmalah)
    assert result == expected, f"Expected '{expected}', got '{result}'"


def test_arabic_letters_only():
    """Test that arabic_letters_only extracts only Arabic letters."""
    text = "الم 123 ذَٰلِكَ الْكِتَابُ !@#"
    result = arabic_letters_only(text)
    
    # Should only contain Arabic letters, no numbers or punctuation
    assert all(ord(c) >= 0x0621 for c in result), "All characters should be Arabic letters"
    assert "1" not in result, "Numbers should be filtered out"
    assert "!" not in result, "Punctuation should be filtered out"


def test_ingest_surah_returns_correct_types():
    """Test that ingest_surah returns the correct data types."""
    sample_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الم ذَٰلِكَ الْكِتَابُ"
    
    rasm, tashkeel, muqattaat, raw = ingest_surah(2, sample_text)
    
    assert isinstance(rasm, list), "Rasm should be a list"
    assert isinstance(tashkeel, list), "Tashkeel should be a list"
    assert isinstance(muqattaat, str) or muqattaat is None, "Muqattaat should be string or None"
    assert isinstance(raw, str), "Raw text should be string"


if __name__ == "__main__":
    pytest.main([__file__])
