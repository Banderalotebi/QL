# src/data/ingestion.py
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
    """Ingest a Surah from the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT m.*, STRING_AGG(v.text_clean, ' ' ORDER BY v.verse_number) as content
            FROM surah_master m
            JOIN verse_data v ON m.surah_id = v.surah_id
            WHERE m.surah_id = %s
            GROUP BY m.surah_id
        """, (surah_number,))
        
        result = cur.fetchone()
        
        if result:
            return {
                "surah_id": result.get("surah_id"),
                "content": result.get("content", ""),
                "muqattaat": isolate_muqattaat(surah_number)
            }
    finally:
        cur.close()
        conn.close()
    
    return None


def run_ingestion(state: dict) -> dict:
    """
    Main ingestion function that loads Surah data into state.
    
    Args:
        state: ResearchState dictionary
        
    Returns:
        Updated state with rasm_matrices and muqattaat_map
    """
    surah_numbers = state.get("surah_numbers", [])
    
    rasm_matrices = {}
    muqattaat_map = {}
    
    for surah_id in surah_numbers:
        surah_data = ingest_surah(surah_id)
        
        if surah_data:
            # Extract rasm from content
            content = surah_data.get("content", "")
            rasm = extract_rasm_strips_diacritics(content)
            rasm_matrices[surah_id] = list(rasm)  # Convert to list of chars
            
            # Get Muqattaat
            muqattaat = surah_data.get("muqattaat", "")
            if muqattaat:
                muqattaat_map[surah_id] = muqattaat
    
    state["rasm_matrices"] = rasm_matrices
    state["muqattaat_map"] = muqattaat_map
    
    return state
