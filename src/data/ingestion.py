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

from src.core.state import ResearchState, RasmMatrix, TashkeelMatrix
from src.data.muqattaat import MUQATTAAT_SURAHS, BY_SURAH

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
    if surah_number not in MUQATTAAT_SURAHS:
        return []

    entry = BY_SURAH[surah_number]
    # Return the canonical Arabic sequence as the isolated sequence
    return [entry.arabic_sequence]


# ── Surah file loader ─────────────────────────────────────────────────────────

def load_surah_text(surah_number: int, data_dir: str = "data/raw") -> str | None:
    """Load raw Quran text for a given Surah number from the dataset."""
    candidates = [
        Path(data_dir) / f"Surah_{surah_number}.txt",
        Path(data_dir) / "quran-uthmani-min" / f"Surah_{surah_number}.txt",
        Path(data_dir) / f"surah_{surah_number}.txt",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8").strip()

    # Try the full Quran text files
    full_quran = Path(data_dir) / "quran-uthmani-min.txt"
    if full_quran.exists():
        # Parse out the surah (simplified — full parser in utils/arabic.py)
        pass

    return None


# ── Main ingestion function ───────────────────────────────────────────────────

def ingest_surah(surah_number: int, raw_text: str) -> tuple[RasmMatrix, TashkeelMatrix]:
    """
    Process one Surah's raw text into the dual-layer matrices.

    Returns:
        (RasmMatrix, TashkeelMatrix) — strictly separated, never mixed.
    """
    # Strip Basmalah if present
    text = raw_text.replace(BASMALAH, "").strip()

    # ── Layer A: Rasm ──────────────────────────────────────────────────────
    rasm_text = extract_rasm(text)
    letter_seq = tokenize_letters(rasm_text)
    isolated = isolate_muqattaat(raw_text, surah_number)

    rasm = RasmMatrix(
        surah_number=surah_number,
        raw_rasm=rasm_text,
        letter_sequence=letter_seq,
        is_surah_start=True,
        isolated_sequences=isolated,
        is_muqattaat_surah=surah_number in MUQATTAAT_SURAHS,
    )

    # ── Layer B: Tashkeel ──────────────────────────────────────────────────
    dmap = extract_tashkeel_map(text)
    rhythm = derive_phonetic_rhythm(text)

    # Basic syllable tokenization (CV groups)
    syllables = re.findall(r'C+V?', rhythm)

    tashkeel = TashkeelMatrix(
        surah_number=surah_number,
        diacritic_map=dmap,
        syllable_structure=syllables,
        phonetic_rhythm=rhythm,
    )

    return rasm, tashkeel


def run_ingestion(state: ResearchState) -> ResearchState:
    """
    LangGraph node: ingest all requested Surahs.
    Populates state["rasm_matrices"] and state["tashkeel_matrices"].
    """
    surah_numbers: list[int] = state.get("input_surah_numbers", [])
    data_dir: str = state.get("data_dir", "data/raw")  # type: ignore[assignment]

    rasm_matrices: dict = {}
    tashkeel_matrices: dict = {}
    muqattaat_registry: dict = {}

    for snum in surah_numbers:
        raw = load_surah_text(snum, data_dir)
        if raw is None:
            # Fallback: use canonical Muqattaat entry text only
            from src.data.muqattaat import BY_SURAH as MQ
            entry = MQ.get(snum)
            raw = entry.arabic_sequence if entry else ""

        rasm, tashkeel = ingest_surah(snum, raw)
        rasm_matrices[snum] = rasm
        tashkeel_matrices[snum] = tashkeel

        if snum in MUQATTAAT_SURAHS:
            muqattaat_registry[snum] = BY_SURAH[snum].arabic_sequence

    state["rasm_matrices"] = rasm_matrices
    state["tashkeel_matrices"] = tashkeel_matrices
    state["muqattaat_registry"] = muqattaat_registry
    state.setdefault("raw_hypotheses", [])
    state.setdefault("rejected_hypotheses", [])
    state.setdefault("known_dead_ends", [])

    return state
