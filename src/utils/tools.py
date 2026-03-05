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
    
    console.print(table)
    console.print(f"... and {len(MUQATTAAT_SURAH_NUMBERS) - 10} more Surahs" if len(MUQATTAAT_SURAH_NUMBERS) > 10 else "")
    return None
