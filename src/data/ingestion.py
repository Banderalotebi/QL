# src/data/ingestion.py
# Ingestion module for the Muqattaat Cryptanalytic Lab

from __future__ import annotations

import os
import requests

from src.core.state import ResearchState

# ── Constants ───────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
QURAN_DIR = os.path.join(DATA_DIR, "Quran_Extracted_Texts")

# ── Functions ───────────────────────────────────────────────────────────────

def load_surah_text(surah_number: int) -> str:
    """
    Load the text of a Surah from the Quran directory.

    Args:
        surah_number: The number of the Surah to load.

    Returns:
        The text of the Surah as a string.
    """
    surah_dir = os.path.join(QURAN_DIR, f"quran-{surah_number}-min")
    text_file = os.path.join(surah_dir, f"{surah_number}.txt")
    if not os.path.exists(text_file):
        raise FileNotFoundError(f"Text file for Surah {surah_number} not found.")
    with open(text_file, "r") as f:
        return f.read()

def run_ingestion(state: ResearchState) -> ResearchState:
    # Send request to ChatOllama API
    response = requests.post(
        CHAT_OLLAMA_API_URL,
        json={"prompt": state.prompt, "max_tokens": state.max_tokens}
    )

    # Parse response
    response_json = response.json()

    # Update state
    state.hypotheses = response_json["output"]

    return state
