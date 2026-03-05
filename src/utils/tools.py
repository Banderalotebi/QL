import sqlite3
from src.utils.abjad import ABJAD

def abjad_calculator(arabic_string: str) -> int:
    """Calculates the exact Gematria value of a word/verse without 'guessing'."""
    abjad_value = 0
    for char in arabic_string:
        if char in ABJAD:
            abjad_value += ABJAD[char]
    return abjad_value

def librarian_get_knowledge(surah_id: int, scout_type: str) -> dict:
    """Searches the Neon `hypotheses` and `rejected_hypotheses` tables for a 'Briefing'."""
    conn = sqlite3.connect("neon.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM hypotheses
        WHERE surah_id = ? AND scout_type = ?
    """, (surah_id, scout_type))
    hypotheses = cursor.fetchall()
    cursor.execute("""
        SELECT * FROM rejected_hypotheses
        WHERE surah_id = ? AND scout_type = ?
    """, (surah_id, scout_type))
    rejected_hypotheses = cursor.fetchall()
    conn.close()
    return {"hypotheses": hypotheses, "rejected_hypotheses": rejected_hypotheses}
