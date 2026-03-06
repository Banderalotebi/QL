"""
🔗 HIVE INTEGRATION - Wire the Council of Experts into the Pipeline
This orchestrates the full system: scouts → hive supervision → synthesizer
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import List

from src.core.graph_utils import compile_graph
from src.core.state import ResearchState, Hypothesis
from src.agents.hive_council import get_hive_council
from src.utils.arabic import MUQATTAAT_SURAH_NUMBERS
from rich.console import Console

console = Console()


def create_integrated_graph():
    """
    Create a research graph that incorporates the hive council
    Flow: Ingestion → Scouts → Hive Supervision → Synthesizer
    """
    from langgraph.graph import StateGraph, END
    from src.core.state_definitions import (
        _run_ingestion, _run_micro_scout, _run_static_scout,
        _run_linguistic_scout, _run_symbolic_scout, _run_math_scout,
        _run_freq_scout, _run_deep_scout, _run_the_fool,
        _run_synthesizer
    )
    
    graph = StateGraph(ResearchState)
    
    # Add existing nodes
    graph.add_node("ingestion", _run_ingestion)
    graph.add_node("micro_scout", _run_micro_scout)
    graph.add_node("static_scout", _run_static_scout)
    graph.add_node("linguistic_scout", _run_linguistic_scout)
    graph.add_node("symbolic_scout", _run_symbolic_scout)
    graph.add_node("math_scout", _run_math_scout)
    graph.add_node("freq_scout", _run_freq_scout)
    graph.add_node("deep_scout", _run_deep_scout)
    graph.add_node("the_fool", _run_the_fool)
    graph.add_node("synthesizer", _run_synthesizer)
    
    # Add new hive supervision node
    graph.add_node("hive_supervision", _run_hive_supervision)
    
    # Edges
    graph.add_edge("ingestion", "micro_scout")
    
    # Parallel scouts
    graph.add_edge("ingestion", "static_scout")
    graph.add_edge("ingestion", "linguistic_scout")
    graph.add_edge("ingestion", "symbolic_scout")
    graph.add_edge("ingestion", "math_scout")
    graph.add_edge("ingestion", "freq_scout")
    graph.add_edge("ingestion", "deep_scout")
    
    # All scouts → fool
    for scout in ["micro_scout", "static_scout", "linguistic_scout", 
                  "symbolic_scout", "math_scout", "freq_scout", "deep_scout"]:
        graph.add_edge(scout, "the_fool")
    
    # Fool → Hive Supervision
    graph.add_edge("the_fool", "hive_supervision")
    
    # Hive → Synthesizer
    graph.add_edge("hive_supervision", "synthesizer")
    
    # Set entry and exit
    graph.set_entry_point("ingestion")
    graph.add_edge("synthesizer", END)
    
    return graph.compile()


def _run_hive_supervision(state: ResearchState) -> ResearchState:
    """
    Expert supervision node
    Each survivor hypothesis is audited by the Council of Experts
    """
    hive = get_hive_council()
    surah_nums = state.get("surah_numbers", [])
    survivors = state.get("survivor_hypotheses", [])
    
    if not survivors:
        console.print("⚠️  No survivor hypotheses to supervise")
        return state
    
    supervised_theories = []
    
    for hyp in survivors:
        surah_num = hyp.surah_refs[0] if hyp.surah_refs else surah_nums[0]
        
        # Run expert supervision
        report = hive.supervise_hypothesis(hyp, surah_num)
        
        # Create supervised version
        supervised_hyp = Hypothesis(
            source_scout=f"{hyp.source_scout} (Supervised)",
            goal_link=hyp.goal_link,
            transformation_steps=hyp.transformation_steps,
            evidence_snippets=hyp.evidence_snippets,
            description=hyp.description,
            score=report.final_score,
            surah_refs=hyp.surah_refs
        )
        
        supervised_theories.append(supervised_hyp)
        
        # Log the supervision
        console.print(
            f"  [cyan]✓[/cyan] {hyp.source_scout} → "
            f"Score: {report.final_score:.3f} [{report.status}]"
        )
    
    state["supervised_theories"] = supervised_theories
    return state


def run_hive_integrated_analysis(surahs: List[int], all_muqattaat: bool = False):
    """
    Execute the integrated analysis pipeline with hive supervision
    """
    console.print("\n" + "="*80)
    console.print("[bold cyan]🏛️  HIERARCHICAL AGENT ARCHITECTURE - COUNCIL OF EXPERTS[/bold cyan]")
    console.print("="*80 + "\n")
    
    # Determine which surahs to analyze
    if all_muqattaat:
        surahs = list(MUQATTAAT_SURAH_NUMBERS)
        console.print(f"[yellow]✨[/yellow] Running analysis on all 29 Muqattaat Surahs!")
    
    # Initialize hive
    hive = get_hive_council()
    console.print(f"\n[cyan]🧠 Initializing Council of Experts[/cyan]")
    console.print(f"  • CrewAI Enabled: {hive.crewai_initialized}")
    console.print(f"  • Mathematical Auditor: Active")
    console.print(f"  • Database Connected: {hive.db.is_connected}")
    console.print(f"  • Shared Memory Loaded: {len(hive.shared_memory)} entries")
    
    # Create integrated graph
    console.print(f"\n[cyan]📊 Compiling integrated research graph[/cyan]")
    graph = create_integrated_graph()
    
    # Initialize state
    initial_state: ResearchState = {
        "surah_numbers": surahs,
        "focus": "muqattaat",
        "raw_hypotheses": [],
        "errors": []
    }
    
    # Run pipeline
    console.print(f"\n[cyan]🚀 Starting integrated research pipeline[/cyan]")
    console.print(f"   Analyzing {len(surahs)} Surah(s): {surahs}\n")
    
    final_state = graph.invoke(initial_state)
    
    # Display results
    console.print("\n" + "="*80)
    console.print("[bold cyan]📊 EXPERT SUPERVISION RESULTS[/bold cyan]")
    console.print("="*80 + "\n")
    
    supervised = final_state.get("supervised_theories", [])
    ranked = final_state.get("ranked_theories", [])
    
    if supervised:
        console.print(f"[bold green]✅ Supervised Theories: {len(supervised)}[/bold green]")
        for i, theory in enumerate(supervised[:5], 1):
            console.print(
                f"\n  {i}. {theory.source_scout}")
            console.print(f"     Score: {theory.score:.4f}")
            console.print(f"     Goal: {theory.goal_link[:60]}...")
    
    if ranked:
        console.print(f"\n[bold green]✅ Final Ranked Theories: {len(ranked)}[/bold green]")
        for i, theory in enumerate(ranked[:5], 1):
            console.print(
                f"\n  {i}. {theory.source_scout}")
            console.print(f"     Score: {theory.score:.4f}")
            console.print(f"     Surahs: {theory.surah_refs}")
    
    # Print hive statistics
    console.print("\n" + "="*80)
    console.print("[bold cyan]🏛️  HIVE COUNCIL STATISTICS[/bold cyan]")
    console.print("="*80)
    
    hive_status = hive.get_hive_status()
    console.print(f"\n  Total Thoughts Logged: {hive_status.get('total_thoughts_logged', 0)}")
    console.print(f"  Total Supervisions: {hive_status.get('total_supervisions', 0)}")
    console.print(f"  Shared Memory Size: {hive_status.get('shared_memory_size', 0)} bytes")
    
    # Save hive state
    console.print(f"\n[cyan]💾 Saving hive state to persistent storage...[/cyan]")
    hive.save_hive_state()
    console.print(f"   ✅ State saved to: /workspaces/QL/data/processed/hive_state.json")
    
    console.print("\n" + "="*80)
    console.print("[bold green]✅ RESEARCH COMPLETE[/bold green]")
    console.print("="*80 + "\n")
    
    return final_state


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Muqattaat Hive Analysis")
    parser.add_argument("--all-muqattaat", action="store_true",
                       help="Analyze all 29 Muqattaat Surahs")
    parser.add_argument("--surahs", nargs="+", type=int, default=[2],
                       help="Surah numbers to analyze")
    
    args = parser.parse_args()
    
    try:
        final_state = run_hive_integrated_analysis(
            surahs=args.surahs,
            all_muqattaat=args.all_muqattaat
        )
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()
