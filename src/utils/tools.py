# src/utils/tools.py
"""
Utility functions for the Muqattaat Cryptanalytic Lab.
"""
import sqlite3


def abjad_calculator(arabic_string: str) -> int:
    """Calculates the exact Gematria value of a word/verse without 'guessing'."""
    from src.utils.abjad import ABJAD
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


def create_header_panel():
    """Creates a header panel for the application (CLI version)."""
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    
    header_text = """
╔══════════════════════════════════════════════════════════════╗
║          Muqattaat Cryptanalytic Lab                          ║
║          Quranic Pattern Analysis Research                    ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(header_text.strip(), title="Welcome", border_style="cyan"))
    return None

def display_dataset_overview():
    """Displays a dataset overview (CLI version)."""
    from rich.console import Console
    from rich.table import Table
    console = Console()
    from src.utils.arabic import MUQATTAAT_SURAH_NUMBERS, KNOWN_MUQATTAAT
    
    table = Table(title="Muqattaat Surahs Dataset")
    table.add_column("Surah #", style="cyan")
    table.add_column("Muqattaat", style="magenta")
    table.add_column("Letters", style="green")
    
    for surah in sorted(MUQATTAAT_SURAH_NUMBERS)[:10]:  # Show first 10
        muqattaat = KNOWN_MUQATTAAT.get(surah, "N/A")
        letters = len(muqattaat)
        table.add_row(str(surah), muqattaat, str(letters))
    
    console.print(table)
    console.print(f"... and {len(MUQATTAAT_SURAH_NUMBERS) - 10} more Surahs" if len(MUQATTAAT_SURAH_NUMBERS) > 10 else "")
    return None
