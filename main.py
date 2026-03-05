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
