# src/core/graph.py
# LangGraph state machine definition for the Muqattaat Cryptanalytic Lab

from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.core.state import ResearchState
from src.agents.micro_scout import MicroScout
from src.agents.static_scout import StaticScout
from src.agents.linguistic_scout import LinguisticScout
from src.agents.symbolic_scout import SymbolicScout
from src.agents.math_scout import MathScout
from src.agents.freq_scout import FreqScout
from src.agents.deep_scout import DeepScout
from src.agents.the_fool import TheFool
from src.agents.synthesizer import Synthesizer

# ── Agent singletons ──────────────────────────────────────────────────────────
_micro_scout = MicroScout()
_static_scout = StaticScout()
_linguistic_scout = LinguisticScout()
_symbolic_scout = SymbolicScout()
_math_scout = MathScout()
_freq_scout = FreqScout()
_deep_scout = DeepScout()
_the_fool = TheFool()
_synthesizer = Synthesizer()


# ── Node wrappers ─────────────────────────────────────────────────────────────

def _run_ingestion(state: ResearchState) -> ResearchState:
    from src.data.ingestion import run_ingestion
    return run_ingestion(state)

def _run_micro_scout(state: ResearchState) -> ResearchState:
    return _micro_scout.run(state)

def _run_static_scout(state: ResearchState) -> ResearchState:
    return _static_scout.run(state)

def _run_linguistic_scout(state: ResearchState) -> ResearchState:
    return _linguistic_scout.run(state)

def _run_symbolic_scout(state: ResearchState) -> ResearchState:
    return _symbolic_scout.run(state)

def _run_math_scout(state: ResearchState) -> ResearchState:
    return _math_scout.run(state)

def _run_freq_scout(state: ResearchState) -> ResearchState:
    return _freq_scout.run(state)

def _run_deep_scout(state: ResearchState) -> ResearchState:
    return _deep_scout.run(state)

def _run_the_fool(state: ResearchState) -> ResearchState:
    return _the_fool.run(state)

def _run_synthesizer(state: ResearchState) -> ResearchState:
    return _synthesizer.run(state)


# ── Graph builder ─────────────────────────────────────────────────────────────

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
