# src/utils/tools.py
"""
Utility functions for the Muqattaat Cryptanalytic Lab.
"""
import tkinter as tk
from tkinter import ttk

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
    
def abjad_calculator(text):
    """Calculate Abjad numerical value of Arabic text."""
    abjad_values = {
        'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6,
        'ز': 7, 'ح': 8, 'ط': 9, 'ي': 10, 'ك': 20, 'ل': 30,
        'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
        'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500,
        'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000
    }
    total = 0
    for char in text:
        total += abjad_values.get(char, 0)
    return total

def librarian_get_knowledge(query):
    """Mock librarian function for knowledge retrieval."""
    # Placeholder implementation
    return f"Knowledge for query: {query}"
