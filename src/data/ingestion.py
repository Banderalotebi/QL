
"""
Data ingestion module for the Muqattaat Cryptanalytic Lab.
"""
from src.data.db import get_db_connection, NeonLabAPI

# Import the necessary modules to avoid Name Shadowing
from operator import add


def extract_rasm_strips_diacritics(text: str) -> str:
    """Extract Rasm strips and diacritics from a given text."""
    import re
    # Arabic letters pattern (without diacritics)
    rasm_pattern = re.compile(r'[\u0621-\u063A\u0641-\u064A\u0671-\u06D3\u06FA-\u06FF]')
    letters = rasm_pattern.findall(text)
    return ''.join(letters)


def isolate_muqattaat(surah_number: int) -> str:
    """Isolate the Muqattaat letters from a given Surah."""
    from src.utils.arabic import KNOWN_MUQATTAAT
    return KNOWN_MUQATTAAT.get(surah_number, "")


def ingest_surah(surah_number: int) -> dict:
    """Ingest a Surah from the file system."""
    import os
    from pathlib import Path
    
    # Path to Quran files
    quran_path = Path("/workspaces/QL/data/Quran_Extracted_Texts/quran-simple")
    surah_file = quran_path / f"Surah_{surah_number}.txt"
    
    if surah_file.exists():
        with open(surah_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        return {
            "surah_id": surah_number,
            "content": content,
            "muqattaat": isolate_muqattaat(surah_number)
        }
    else:
        return {
            "surah_id": surah_number,
            "content": "",
            "muqattaat": isolate_muqattaat(surah_number)
        }
    
    return None


def load_surah_text(surah_number: int) -> str:
    """Load the text of a Surah from the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT text_clean
            FROM verse_data
            WHERE surah_id = %s
            ORDER BY verse_number
            LIMIT 1
        """, (surah_number,))
        
        result = cur.fetchone()
        
        if result:
            return result[0]
    finally:
        cur.close()
        conn.close()
    
    return None


def run_ingestion(state: dict) -> dict:
    """
    LangGraph node to ingest requested surahs and update the state.
    """
    # Get the list of surahs to process from the state
    surahs = state.get("surah_numbers", [])
    if not surahs and "input_surah_numbers" in state:
        surahs = state["input_surah_numbers"]

    rasm_matrices = {}
    tashkeel_matrices = {}
    muqattaat_map = {}

    for surah_number in surahs:
        # 1. Load the surah data
        surah_data = ingest_surah(surah_number)
        raw_text = surah_data["content"]
        muqattaat = surah_data["muqattaat"]
        
        if raw_text:
            # 2. Extract rasm (skeletal letters)
            rasm = extract_rasm_strips_diacritics(raw_text)
            
            # 3. For now, tashkeel is same as rasm (simplified)
            tashkeel = rasm
            
            # 4. Store the results
            rasm_matrices[surah_number] = list(rasm)  # Convert to list of letters
            tashkeel_matrices[surah_number] = list(tashkeel)
            if muqattaat:
                muqattaat_map[surah_number] = muqattaat

    # Return the dictionary of state updates to LangGraph
    return {
        "rasm_matrices": rasm_matrices,
        "tashkeel_matrices": tashkeel_matrices,
        "muqattaat_map": muqattaat_map
    }
