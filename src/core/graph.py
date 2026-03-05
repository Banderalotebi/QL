# src/core/graph.py
from langgraph.graph import END, StateGraph
from src.core.state import ResearchState
from src.core.state_definitions import (
    _run_ingestion, _run_micro_scout, _run_static_scout,
    _run_linguistic_scout, _run_symbolic_scout, _run_math_scout,
    _run_freq_scout, _run_deep_scout, _run_the_fool, _run_synthesizer
)

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
    graph.add_edge("synthesizer", END)

    return graph


def compile_graph():
    return build_graph().compile()
