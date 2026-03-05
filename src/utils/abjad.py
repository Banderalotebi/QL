"""
src/utils/abjad.py
──────────────────
Abjad (أبجد) numerical system.
Maps Arabic letters to their classical numerical values.
Used by MathScout for Muqattaat numerical analysis.
"""

from __future__ import annotations

# Traditional Abjad values (Arabic Unicode characters)
ABJAD: dict[str, int] = {
    'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
    'ي': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
    'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000
}


def abjad_value_of_sequence(sequence: str) -> int:
    """Calculate the total Abjad value of an Arabic letter sequence."""
    from src.utils.arabic import arabic_letters_only
    letters = arabic_letters_only(sequence)
    return sum(ABJAD.get(letter, 0) for letter in letters)


def calculate_abjad_value(text: str) -> int:
    """Calculate the total Abjad value of Arabic text."""
    return abjad_value_of_sequence(text)


def abjad_value_of_arabic(arabic_text: str) -> int:
    """
    Calculate Abjad value from raw Arabic Unicode characters.
    Maps base Arabic letters to their Abjad values.
    """
    return sum(ABJAD.get(ch, 0) for ch in arabic_text)
