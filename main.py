"""
main.py
───────
Muqattaat Cryptanalytic Lab — Main Entrypoint

Usage:
    python main.py --surahs 2 3 7 19 20 --focus muqattaat
    python main.py --all-muqattaat
    python main.py --surahs 2 --focus full_surah

This is the lab interface for discovering the meaning of the
Disjointed Letters (الحروف المقطعة / Muqattaat).
"""

from __future__ import annotations
import argparse
import uuid
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.core.graph import compile_graph
from src.core.state import ResearchState
from src.data.muqattaat import MUQATTAAT_SURAHS, summary_stats

console = Console()


def parse_args():
    p = argparse.ArgumentParser(
        description="Muqattaat Cryptanalytic Lab — Find the meaning of the Disjointed Letters"
    )
    p.add_argument(
        "--surahs", nargs="+", type=int,
        help="Surah numbers to analyze (e.g. --surahs 2 3 7)"
    )
    p.add_argument(
        "--all-muqattaat", action="store_true",
        help="Analyze all 29 Muqattaat-bearing Surahs"
    )
    p.add_argument(
        "--focus", choices=["muqattaat", "full_surah", "comparison"],
        default="muqattaat",
        help="Analysis focus mode"
    )
    p.add_argument(
        "--data-dir", default="data/raw",
        help="Path to raw Quran text files"
    )
    p.add_argument(
        "--top", type=int, default=10,
        help="Number of top theories to display"
    )
    return p.parse_args()


def print_header():
    console.print(Panel.fit(
        "[bold cyan]Muqattaat Cryptanalytic Lab[/bold cyan]\n"
        "[dim]الحروف المقطعة — The Disjointed Letters[/dim]\n"
        "[yellow]Primary Goal: Discover the meaning of the isolated letter sequences[/yellow]",
        border_style="cyan"
    ))


def print_muqattaat_overview():
    stats = summary_stats()
    console.print(f"\n[bold]Dataset Overview:[/bold]")
    console.print(f"  • Surahs with Muqattaat: [cyan]{stats['total_muqattaat_surahs']}[/cyan]")
    console.print(f"  • Unique letters used:   [cyan]{stats['unique_letter_count']}[/cyan] of 28")
    console.print(f"  • Unique combinations:   [cyan]{stats['unique_combinations']}[/cyan]")
    console.print(f"  • Letters: [yellow]{', '.join(stats['letters_used'])}[/yellow]\n")


def print_report(report: dict, top: int = 10):
    console.print("\n" + "─" * 60)
    console.print(f"[bold green]Lab Report — Run {report.get('run_id', '')[:8]}[/bold green]")
    console.print(f"Surahs analyzed: {report.get('surahs_analyzed', [])}")
    console.print(
        f"Hypotheses: [white]{report.get('total_hypotheses', 0)}[/white] generated  "
        f"[green]{report.get('survivors', 0)}[/green] survived The Fool  "
        f"[red]{report.get('dead_ends_recorded', 0)}[/red] dead-ends saved"
    )

    theories = report.get("top_theories", [])[:top]
    if not theories:
        console.print("[yellow]No theories passed scoring threshold.[/yellow]")
        return

    table = Table(
        title="Top Theories (ranked by Occam Score)",
        box=box.ROUNDED, show_lines=True
    )
    table.add_column("Rank", style="dim", width=4)
    table.add_column("Score", style="cyan", width=6)
    table.add_column("Scout", style="yellow", width=18)
    table.add_column("Finding", style="white", width=50)
    table.add_column("Goal Link (Muqattaat Relevance)", style="green", width=50)
    table.add_column("Steps", style="dim", width=5)

    for i, t in enumerate(theories, 1):
        table.add_row(
            str(i),
            f"{t['score']:.3f}",
            t["scout"][:18],
            t["description"][:120],
            t["goal_link"][:120],
            str(t["steps"]),
        )

    console.print(table)


def main():
    args = parse_args()
    print_header()
    print_muqattaat_overview()

    # Determine which Surahs to analyze
    if args.all_muqattaat:
        surahs = sorted(MUQATTAAT_SURAHS)
    elif args.surahs:
        surahs = args.surahs
    else:
        # Default: analyze the most commonly studied Muqattaat Surahs
        surahs = [2, 3, 7, 10, 19, 20, 36, 38, 40, 42, 50, 68]

    console.print(f"[bold]Analyzing Surahs:[/bold] {surahs}")

    # Build initial state
    initial_state: ResearchState = {
        "input_surah_numbers": surahs,
        "input_focus": args.focus,
        "data_dir": args.data_dir,  # type: ignore[typeddict-unknown-key]
        "run_id": str(uuid.uuid4()),
        "raw_hypotheses": [],
        "rejected_hypotheses": [],
        "known_dead_ends": [],
    }

    # Compile and run the graph
    console.print("\n[dim]Compiling research graph...[/dim]")
    graph = compile_graph()

    console.print("[dim]Running cognitive research loop...[/dim]\n")
    final_state = graph.invoke(initial_state)

    # Display results
    print_report(final_state.get("lab_report", {}), top=args.top)

    # Save full report
    report_path = "data/processed/last_report.json"
    import os; os.makedirs("data/processed", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(final_state.get("lab_report", {}), f, ensure_ascii=False, indent=2)
    console.print(f"\n[dim]Full report saved to {report_path}[/dim]")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
main.py
───────
Main entry point for the Muqattaat Cryptanalytic Lab.
Runs the full LangGraph pipeline on selected Surahs.
"""

import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.core.graph import compile_graph
from src.core.state import ResearchState
from src.utils.arabic import MUQATTAAT_SURAH_NUMBERS, KNOWN_MUQATTAAT

console = Console()

def create_header_panel() -> Panel:
    """Create the header panel with Arabic text display."""
    header_text = Text()
    header_text.append("🔬 Muqattaat Cryptanalytic Lab\n", style="bold blue")
    header_text.append("الحروف المقطعة - Isolated Letter Sequences\n", style="bold")
    header_text.append("Discovering the meaning of the Quranic opening letters", style="dim")
    
    return Panel(header_text, title="Research Laboratory", border_style="blue")

def display_dataset_overview():
    """Display dataset statistics."""
    console.print("\n📊 Dataset Overview:", style="bold green")
    console.print(f"• Total Muqattaat Surahs: {len(MUQATTAAT_SURAH_NUMBERS)}")
    
    # Count unique letters across all Muqattaat
    unique_letters = set()
    for muqattaat in KNOWN_MUQATTAAT.values():
        unique_letters.update(list(muqattaat))
    
    console.print(f"• Unique Muqattaat letters: {len(unique_letters)}")
    console.print(f"• Letters: {' '.join(sorted(unique_letters))}")

def display_results(state: ResearchState):
    """Display the final results in a formatted table."""
    raw_count = len(state.get("raw_hypotheses", []))
    survivor_count = len(state.get("survivor_hypotheses", []))
    theories = state.get("scored_theories", [])
    
    console.print(f"\n📈 Results Summary:", style="bold green")
    console.print(f"• Hypotheses generated: {raw_count}")
    console.print(f"• Survivors (post-Fool): {survivor_count}")
    console.print(f"• Final theories: {len(theories)}")
    
    if theories:
        console.print("\n🏆 Top Theories (Ranked by Occam Score):", style="bold yellow")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", width=4)
        table.add_column("Scout", width=12)
        table.add_column("Score", width=6)
        table.add_column("Goal Link", width=60)
        table.add_column("Surahs", width=10)
        
        for i, theory in enumerate(theories[:10], 1):
            goal_link = theory.goal_link[:57] + "..." if len(theory.goal_link) > 60 else theory.goal_link
            surah_refs = ", ".join(map(str, theory.surah_refs[:3]))
            if len(theory.surah_refs) > 3:
                surah_refs += "..."
            
            # Check for empty goal link - this is a bug if it happens
            if not goal_link.strip():
                goal_link = "[ERROR: Empty Goal Link]"
                console.print(f"🚨 BUG DETECTED: Theory {i} has empty goal_link!", style="bold red")
            
            table.add_row(
                str(i),
                theory.source_scout,
                f"{theory.score:.3f}",
                goal_link,
                surah_refs
            )
        
        console.print(table)
    
    # Display any errors
    errors = state.get("errors", [])
    if errors:
        console.print("\n⚠️  Errors:", style="bold red")
        for error in errors:
            console.print(f"  • {error}")

def main():
    parser = argparse.ArgumentParser(description="Muqattaat Cryptanalytic Lab")
    parser.add_argument(
        "--surahs", 
        nargs="+", 
        type=int, 
        default=[2, 19, 36, 50, 68],
        help="Surah numbers to analyze (default: 2 19 36 50 68)"
    )
    parser.add_argument(
        "--focus", 
        default="muqattaat",
        help="Research focus mode (default: muqattaat)"
    )
    parser.add_argument(
        "--data-dir",
        default="/Users/bander/QL/data",
        help="Path to data directory"
    )
    
    args = parser.parse_args()
    
    # Display header
    console.print(create_header_panel())
    display_dataset_overview()
    
    # Validate Surah numbers
    invalid_surahs = [s for s in args.surahs if s not in MUQATTAAT_SURAH_NUMBERS]
    if invalid_surahs:
        console.print(f"\n⚠️  Warning: Surahs {invalid_surahs} do not contain Muqattaat", style="yellow")
        args.surahs = [s for s in args.surahs if s in MUQATTAAT_SURAH_NUMBERS]
    
    if not args.surahs:
        console.print("❌ No valid Muqattaat Surahs selected!", style="bold red")
        return
    
    console.print(f"\n🔍 Analyzing Surahs: {args.surahs}")
    console.print("🚀 Starting research pipeline...\n")
    
    # Initialize state
    initial_state: ResearchState = {
        "surah_numbers": args.surahs,
        "focus": args.focus,
        "raw_hypotheses": [],
        "errors": []
    }
    
    # Compile and run the graph
    try:
        graph = compile_graph()
        final_state = graph.invoke(initial_state)
        
        # Display results
        display_results(final_state)
        
    except Exception as e:
        console.print(f"❌ Pipeline failed: {e}", style="bold red")
        raise

if __name__ == "__main__":
    main()
