# Arabic text processing utilities for the Muqattaat Cryptanalytic Lab

from __future__ import annotations

import re
from typing import Optional

# The 29 Surahs that open with Muqattaat sequences
MUQATTAAT_SURAH_NUMBERS: frozenset[int] = frozenset(
    [2, 3, 7, 10, 11, 12, 13, 14, 15, 19, 20, 26, 27, 28, 29, 30, 31, 32,
     36, 38, 40, 41, 42, 43, 44, 45, 46, 50, 68]
)

# Known Muqattaat sequences mapped by Surah number
KNOWN_MUQATTAAT: dict[int, str] = {
    2: "الم", 3: "الم", 7: "المص", 10: "الر", 11: "الر", 12: "الر", 13: "المر",
    14: "الر", 15: "الر", 19: "كهيعص", 20: "طه", 26: "طسم", 27: "طس", 28: "طسم",
    29: "الم", 30: "الم", 31: "الم", 32: "الم", 36: "يس", 38: "ص", 40: "حم",
    41: "حم", 42: "حم", 43: "حم", 44: "حم", 45: "حم", 46: "حم", 50: "ق", 68: "ن"
}

# Standard Basmalah text
BASMALAH = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"

# Arabic letter range (Unicode blocks for Arabic)
ARABIC_LETTER_PATTERN = re.compile(r'[\u0621-\u063A\u0641-\u064A\u0671-\u06D3\u06FA-\u06FF]')


def strip_basmalah(text: str) -> str:
    """
    Remove the opening Basmalah from Surah text.
    
    Args:
        text: Raw Surah text that may start with Basmalah
        
    Returns:
        Text with Basmalah removed if present
    """
    text = text.strip()
    
    # Check if text starts with the standard Basmalah
    if text.startswith(BASMALAH):
        # Remove Basmalah and any following whitespace
        remaining = text[len(BASMALAH):].strip()
        return remaining
    
    # Also check for Basmalah with slight variations in diacritics
    # Split into words and check if first few words match Basmalah pattern
    words = text.split()
    if len(words) >= 4:
        # Check if first 4 words match Basmalah structure
        potential_basmalah = " ".join(words[:4])
        # Simple heuristic: if it contains the key Basmalah words
        if "بِسْمِ" in potential_basmalah and "اللَّهِ" in potential_basmalah:
            # Remove first 4 words and rejoin
            remaining_words = words[4:]
            return " ".join(remaining_words)
    
    return text


def arabic_letters_only(text: str) -> list[str]:
    """
    Tokenize text into individual Arabic letters only.
    
    Filters out:
    - Diacritics (tashkeel marks)
    - Spaces and punctuation
    - Non-Arabic characters
    - Numbers
    
    Args:
        text: Input Arabic text
        
    Returns:
        List of individual Arabic letter characters (rasm layer)
    """
    # Find all Arabic letters using regex
    letters = ARABIC_LETTER_PATTERN.findall(text)
    
    # Additional filtering to remove any remaining non-letter characters
    filtered_letters = []
    for letter in letters:
        # Skip if it's a diacritic mark (tashkeel)
        if '\u064B' <= letter <= '\u065F':  # Diacritic range
            continue
        if '\u0670' <= letter <= '\u0671':  # Additional diacritic range
            continue
        if letter in '\u06D6\u06D7\u06D8\u06D9\u06DA\u06DB\u06DC\u06DD\u06DE\u06DF\u06E0\u06E1\u06E2\u06E3\u06E4\u06E5\u06E6\u06E7\u06E8\u06E9\u06EA\u06EB\u06EC\u06ED':
            continue
        
        filtered_letters.append(letter)
    
    return filtered_letters


def detect_muqattaat_in_text(text: str, surah_number: int) -> Optional[str]:
    """
    Check if the first non-Basmalah token is a known Muqattaat sequence.
    
    Args:
        text: Raw Surah text
        surah_number: Surah number (1-indexed)
        
    Returns:
        The Muqattaat sequence if found, None otherwise
    """
    # First check if this Surah is known to have Muqattaat
    if surah_number not in MUQATTAAT_SURAH_NUMBERS:
        return None
    
    # Strip Basmalah first
    clean_text = strip_basmalah(text).strip()
    
    if not clean_text:
        return None
    
    # Get the expected Muqattaat for this Surah
    expected_muqattaat = KNOWN_MUQATTAAT.get(surah_number)
    if not expected_muqattaat:
        return None
    
    # Check if the text starts with the expected Muqattaat
    # Split into words and check the first word/token
    words = clean_text.split()
    if not words:
        return None
    
    first_token = words[0].strip()
    
    # Direct match check
    if first_token == expected_muqattaat:
        return expected_muqattaat
    
    # Also check if the first token contains the Muqattaat
    # (in case there are attached diacritics or formatting)
    if expected_muqattaat in first_token:
        return expected_muqattaat
    
    # Check if we can extract Arabic letters from first token and match
    first_token_letters = arabic_letters_only(first_token)
    expected_letters = arabic_letters_only(expected_muqattaat)
    
    if first_token_letters == expected_letters:
        return expected_muqattaat
    
    return None
