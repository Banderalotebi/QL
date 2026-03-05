"""
src/data/ingestion.py
─────────────────────
Dual-Layer Ingestion Pipeline

Splits raw Arabic Quran text into:
  Layer A — Rasm Matrix  (skeletal letters, no diacritics)
  Layer B — Tashkeel Matrix (diacritics overlay)

Also isolates and tags Muqattaat sequences as Isolated_Sequence nodes,
which receive priority routing to MathScout + SymbolicScout.

INVARIANT: Rasm and Tashkeel layers NEVER mix after this stage.
"""

from __future__ import annotations
import os
import re
import unicodedata
from pathlib import Path

from src.core.state import ResearchState
from src.utils.arabic import strip_basmalah, arabic_letters_only, detect_muqattaat_in_text, KNOWN_MUQATTAAT

# ── Arabic Unicode ranges ─────────────────────────────────────────────────────

# Tashkeel (diacritics) codepoints
TASHKEEL = set("\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0653\u0654\u0655\u0656\u0670")

# Arabic letter range (base letters only)
ARABIC_LETTERS_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')

# Basmalah prefix (strip before analysis)
BASMALAH = "بِسمِ اللَّهِ الرَّحمـٰنِ الرَّحيمِ"


# ── Rasm extraction ───────────────────────────────────────────────────────────

def extract_rasm(text: str) -> str:
    """
    Strip all Tashkeel diacritics, leaving only the skeletal letter sequence.
    This is the Layer A baseline — pure mathematical and geometric foundation.
    """
    return "".join(ch for ch in text if ch not in TASHKEEL)


def tokenize_letters(rasm: str) -> list[str]:
    """Split Rasm string into individual Arabic letter tokens (ignoring spaces/punctuation)."""
    return [ch for ch in rasm if ARABIC_LETTERS_RE.match(ch)]


# ── Tashkeel extraction ───────────────────────────────────────────────────────

def extract_tashkeel_map(text: str) -> dict[int, str]:
    """
    Build a positional map of diacritics.
    Returns { original_char_index → diacritic_character }.
    Only positions that carry a diacritic are stored.
    """
    dmap: dict[int, str] = {}
    for i, ch in enumerate(text):
        if ch in TASHKEEL:
            dmap[i] = ch
    return dmap


def derive_phonetic_rhythm(text: str) -> str:
    """
    Build a compact C (consonant) / V (vowel-marked) rhythm string.
    Used by LinguisticScout for syllable pattern analysis.
    """
    rhythm: list[str] = []
    prev_was_letter = False
    for ch in text:
        if ARABIC_LETTERS_RE.match(ch):
            rhythm.append("C")
            prev_was_letter = True
        elif ch in TASHKEEL and prev_was_letter:
            if rhythm:
                rhythm[-1] = "V"   # Mark the preceding consonant as vowelled
            prev_was_letter = False
    return "".join(rhythm)


# ── Muqattaat isolation ───────────────────────────────────────────────────────

def isolate_muqattaat(raw_text: str, surah_number: int) -> list[str]:
    """
    Detect and return Muqattaat sequences in the text.
    These are tagged as Isolated_Sequence — do not read as words.

    Strategy: The Muqattaat appear at the very start of the Surah
    (after Basmalah). We extract the first 1–5 letter tokens and check
    against the canonical registry.
    """
    # Use the detect_muqattaat_in_text function from arabic utils
    muqattaat = detect_muqattaat_in_text(raw_text, surah_number)
    if muqattaat:
        return [muqattaat]
    return []


# ── Surah file loader ─────────────────────────────────────────────────────────

def load_surah_text(surah_number: int, data_dir: str = "/Users/bander/QL/data") -> str | None:
    """Load raw Quran text for a given Surah number from the dataset."""
    # Construct path to the Surah file
    data_dir_path = Path(data_dir)
    candidates = [
        data_dir_path / f"Surah_{surah_number}.txt",
        data_dir_path / "quran-uthmani-min" / f"Surah_{surah_number}.txt",
        data_dir_path / f"surah_{surah_number}.txt",
        data_dir_path / "raw" / f"Surah_{surah_number}.txt",
        data_dir_path / "raw" / "quran-uthmani-min" / f"Surah_{surah_number}.txt",
    ]
    
    for path in candidates:
        try:
            if path.exists():
                content = path.read_text(encoding="utf-8").strip()
                if content:
                    return content
        except Exception as e:
            print(f"Error reading {path}: {e}")
            continue

    print(f"Warning: Surah file not found for Surah {surah_number}")
    return None


# ── Main ingestion function ───────────────────────────────────────────────────

def ingest_surah(surah_number: int, raw_text: str | None = None) -> tuple[list[str] | None, list[str] | None, str | None, str | None]:
    """
    Process one Surah's raw text into the dual-layer matrices.

    Args:
        surah_number: Surah number (1-indexed)
        raw_text: Optional raw text, if None will load from file

    Returns:
        Tuple of (rasm_matrix, tashkeel_matrix, muqattaat, raw_text)
    """
    # Load raw text if not provided
    if raw_text is None:
        raw_text = load_surah_text(surah_number)
    
    if not raw_text:
        return None, None, None, None
    
    # Strip Basmalah first
    clean_text = strip_basmalah(raw_text)
    
    # For rasm layer: extract only Arabic letters (no diacritics)
    rasm_letters = arabic_letters_only(clean_text)
    
    # For tashkeel layer: extract diacritic map and convert to list format
    tashkeel_map = extract_tashkeel_map(clean_text)
    # Convert tashkeel map to a format that preserves positional diacritic info
    tashkeel_matrix = [derive_phonetic_rhythm(clean_text)]  # Use phonetic rhythm for tashkeel layer
    
    # Detect Muqattaat
    muqattaat = detect_muqattaat_in_text(raw_text, surah_number)
    
    return rasm_letters, tashkeel_matrix, muqattaat, raw_text


def run_ingestion(state: ResearchState) -> ResearchState:
    """
    Main ingestion pipeline that populates the ResearchState.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with ingested data
    """
    surah_numbers = state.get("surah_numbers", [])
    if not surah_numbers:
        state["errors"] = state.get("errors", []) + ["No Surah numbers specified for ingestion"]
        return state
    
    # Initialize state dictionaries
    state["rasm_matrices"] = {}
    state["tashkeel_matrices"] = {}
    state["muqattaat_map"] = {}
    state["raw_text"] = {}
    # Load known dead ends from Knowledge Graph
    try:
        from src.data.knowledge_graph import KnowledgeGraphLinker
        kg_linker = KnowledgeGraphLinker()
        state["known_dead_ends"] = kg_linker.get_dead_end_fingerprints()
    except Exception:
        state["known_dead_ends"] = []  # Fallback to empty list
    
    # Also populate known dead ends in the state for scouts to check
    if not state.get("known_dead_ends"):
        state["known_dead_ends"] = []
    
    errors = state.get("errors", [])
    
    # Process each Surah
    for surah_num in surah_numbers:
        try:
            rasm, tashkeel, muqattaat, raw = ingest_surah(surah_num)
            
            if rasm is None:
                errors.append(f"Failed to ingest Surah {surah_num}")
                continue
            
            # Store in state
            state["rasm_matrices"][surah_num] = rasm
            state["tashkeel_matrices"][surah_num] = tashkeel
            state["raw_text"][surah_num] = raw
            
            # Store Muqattaat if found
            if muqattaat:
                state["muqattaat_map"][surah_num] = muqattaat
                
        except Exception as e:
            errors.append(f"Error processing Surah {surah_num}: {str(e)}")
    
    state["errors"] = errors
    return state
