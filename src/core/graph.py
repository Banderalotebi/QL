# src/core/graph.py
import uuid
from langgraph.graph import END, StateGraph
from src.core.state import ResearchState
from src.core.state_definitions import (
    _run_ingestion, _run_micro_scout, _run_static_scout,
    _run_linguistic_scout, _run_symbolic_scout, _run_math_scout,
    _run_freq_scout, _run_deep_scout, _run_the_fool, _run_synthesizer
)

def _build_report(state: ResearchState) -> dict:
    """Compiles the final metrics into the lab_report dict for main.py UI"""
    run_id = state.get("run_id", str(uuid.uuid4()))
    surahs = state.get("surah_numbers", state.get("input_surah_numbers", []))
    raw_hyps = state.get("raw_hypotheses", [])
    
    # Sort generated theories by score descending
    # Fallback to raw_hypotheses if Occam Scorer isn't fully implemented yet
    theories_to_rank = state.get("scored_theories", raw_hyps)
    top_theories = sorted(
        [h.__dict__ for h in theories_to_rank], 
        key=lambda x: x.get("score", 0), 
        reverse=True
    )

    lab_report = {
        "run_id": run_id,
        "surahs_analyzed": surahs,
        "total_hypotheses": len(raw_hyps),
        "survivors": len(state.get("survivor_hypotheses", [])),
        "dead_ends_recorded": len(state.get("known_dead_ends", [])),
        "top_theories": top_theories
    }
    
    return {"lab_report": lab_report}

def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

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
    graph.add_node("report_builder", _build_report)

    graph.set_entry_point("ingestion")
    graph.add_edge("ingestion", "micro_scout")
    graph.add_edge("micro_scout", "static_scout")
    graph.add_edge("static_scout", "linguistic_scout")
    graph.add_edge("linguistic_scout", "symbolic_scout")
    graph.add_edge("symbolic_scout", "math_scout")
    graph.add_edge("math_scout", "freq_scout")
    graph.add_edge("freq_scout", "deep_scout")
    graph.add_edge("deep_scout", "the_fool")
    graph.add_edge("the_fool", "synthesizer")
    graph.add_edge("synthesizer", "report_builder")
    graph.add_edge("report_builder", END)

    return graph

def compile_graph():
    return build_graph().compile()
