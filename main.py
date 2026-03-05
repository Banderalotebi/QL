#!/usr/bin/env python3
"""
Muqattaat Cryptanalytic Lab
Main entry point for Quranic pattern analysis research.
"""
import argparse
import sys
from rich.console import Console
from rich.table import Table

from src.core.graph_utils import compile_graph
from src.core.state import ResearchState
from src.utils.tools import create_header_panel, display_dataset_overview, MUQATTAAT_SURAH_NUMBERS

console = Console()

def display_results(state: ResearchState):
    """Display research results in a formatted table."""
    console.print("\n" + "="*80)
    console.print("📊 RESEARCH RESULTS", style="bold cyan")
    console.print("="*80 + "\n")
    
    # Get ranked theories
    theories = state.get("ranked_theories", [])
    
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
