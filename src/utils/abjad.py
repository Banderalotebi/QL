"""
src/utils/abjad.py
──────────────────
Abjad (أبجد) numerical system.
Maps Arabic letters to their classical numerical values.
Used by MathScout for Muqattaat numerical analysis.
"""

from __future__ import annotations

# Standard Abjad values (Eastern Arabic order)
ABJAD: dict[str, int] = {
    "Alif":  1,    # ا
    "Ba":    2,    # ب
    "Jim":   3,    # ج
    "Dal":   4,    # د
    "Ha":    5,    # ه
    "Waw":   6,    # و
    "Zay":   7,    # ز
    "Ha2":   8,    # ح
    "Ta":    9,    # ط
    "Ya":    10,   # ي
    "Kaf":   20,   # ك
    "Lam":   30,   # ل
    "Mim":   40,   # م
    "Nun":   50,   # ن
    "Sin":   60,   # س
    "Ain":   70,   # ع
    "Fa":    80,   # ف
    "Sad":   90,   # ص
    "Qaf":   100,  # ق
    "Ra":    200,  # ر
    "Shin":  300,  # ش
    "Ta2":   400,  # ت
    "Tha":   500,  # ث
    "Kha":   600,  # خ
    "Dhal":  700,  # ذ
    "Dad":   800,  # ض
    "Dha":   900,  # ظ
    "Ghain": 1000, # غ
}


def abjad_value_of_sequence(letter_names: list[str]) -> int:
    """Sum the Abjad values of a sequence of letter names."""
    return sum(ABJAD.get(name, 0) for name in letter_names)


def abjad_value_of_arabic(arabic_text: str) -> int:
    """
    Approximate Abjad value from raw Arabic Unicode characters.
    Maps base Arabic letters to their Abjad values.
    """
    ARABIC_TO_ABJAD: dict[str, int] = {
        "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5,
        "و": 6, "ز": 7, "ح": 8, "ط": 9, "ي": 10,
        "ك": 20, "ل": 30, "م": 40, "ن": 50, "س": 60,
        "ع": 70, "ف": 80, "ص": 90, "ق": 100, "ر": 200,
        "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700,
        "ض": 800, "ظ": 900, "غ": 1000,
    }
    return sum(ARABIC_TO_ABJAD.get(ch, 0) for ch in arabic_text)
