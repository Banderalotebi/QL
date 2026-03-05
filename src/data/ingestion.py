# src/data/ingestion.py
# Ingestion module for the Muqattaat Cryptanalytic Lab

from __future__ import annotations
import os

from src.core.state import ResearchState

def get_project_root() -> str:
    """Safely resolve the absolute path to the QL project root."""
    # This file is at QL/src/data/ingestion.py
    # So we go up 3 levels to hit QL/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def load_surah_text(surah_number: int, script_type: str = "quran-uthmani-min") -> str:
    """
    Load the text of a Surah from the Quran directory.

    Args:
        surah_number: The number of the Surah to load.
        script_type: The subfolder to pull from (e.g., 'quran-uthmani-min', 'quran-simple-clean')

    Returns:
        The text of the Surah as a string.
    """
    base_dir = os.path.join(get_project_root(), "data", "Quran_Extracted_Texts")
    file_path = os.path.join(base_dir, script_type, f"Surah_{surah_number}.txt")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Surah text not found at: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def run_ingestion(state: ResearchState) -> ResearchState:
    """
    Validates that the required data for the requested Surahs is available
    before releasing the Scout agents.
    """
    # Handle both potential state keys depending on how main.py initialized it
    surahs = state.get("surah_numbers", state.get("input_surah_numbers", []))
    errors = state.get("errors", [])
    
    for surah in surahs:
        try:
            # Test loading both the Uthmani script (for Rasm scouts)
            # and the Simple script (for Tashkeel scouts)
            load_surah_text(surah, "quran-uthmani-min")
            load_surah_text(surah, "quran-simple-clean")
        except Exception as e:
            errors.append(str(e))
            
    # Update state with any missing file errors
    state["errors"] = errors
    
    # Initialize lists if they don't exist yet so scouts don't crash
    if "raw_hypotheses" not in state:
        state["raw_hypotheses"] = []
    
    return state
