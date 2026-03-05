"""
src/core/graph.py
─────────────────
LangGraph state machine.
Wires all agents into the cognitive research loop.

Flow:
  ingest → [scouts in parallel] → fool → synthesizer → scorer → linker → report
"""

from __future__ import annotations
from langgraph.graph import StateGraph, END
from src.core.state import ResearchState
from src.data.ingestion import run_ingestion
from src.agents.micro_scout import MicroScout
from src.agents.static_scout import StaticScout
from src.agents.linguistic_scout import LinguisticScout
from src.agents.symbolic_scout import SymbolicScout
from src.agents.math_scout import MathScout
from src.agents.freq_scout import FreqScout
from src.agents.deep_scout import DeepScout
from src.agents.the_fool import TheFool
from src.agents.synthesizer import Synthesizer
from src.core.scorer import rank_theories
from src.data.knowledge_graph import KnowledgeGraphLinker


# ── Instantiate agents ────────────────────────────────────────────────────────
_micro = MicroScout()
_static = StaticScout()
_linguistic = LinguisticScout()
_symbolic = SymbolicScout()
_math = MathScout()
_freq = FreqScout()
_deep = DeepScout()
_fool = TheFool()
_synth = Synthesizer()
_linker = KnowledgeGraphLinker()


# ── Node wrappers ─────────────────────────────────────────────────────────────

def node_ingest(state: ResearchState) -> ResearchState:
    return run_ingestion(state)


def node_micro(state: ResearchState) -> ResearchState:
    return _micro.run(state)


def node_static(state: ResearchState) -> ResearchState:
    return _static.run(state)


def node_linguistic(state: ResearchState) -> ResearchState:
    return _linguistic.run(state)


def node_symbolic(state: ResearchState) -> ResearchState:
    return _symbolic.run(state)


def node_math(state: ResearchState) -> ResearchState:
    return _math.run(state)


def node_freq(state: ResearchState) -> ResearchState:
    return _freq.run(state)


def node_deep(state: ResearchState) -> ResearchState:
    return _deep.run(state)


def node_fool(state: ResearchState) -> ResearchState:
    return _fool.run(state)


def node_synthesizer(state: ResearchState) -> ResearchState:
    return _synth.run(state)


def node_scorer(state: ResearchState) -> ResearchState:
    state["scored_theories"] = rank_theories(
        state.get("synthesized_theories", [])
    )
    return state


def node_linker(state: ResearchState) -> ResearchState:
    return _linker.run(state)


def node_report(state: ResearchState) -> ResearchState:
    """Compile the final lab report."""
    scored = state.get("scored_theories", [])
    rejected = state.get("rejected_hypotheses", [])
    state["lab_report"] = {
        "run_id": state.get("run_id", ""),
        "surahs_analyzed": state.get("input_surah_numbers", []),
        "top_theories": [
            {
                "score": h.score,
                "scout": h.source_scout,
                "description": h.description,
                "goal_link": h.goal_link,
                "steps": h.transformation_steps,
                "surahs": h.surah_refs,
            }
            for h in scored[:10]
        ],
        "total_hypotheses": len(state.get("raw_hypotheses", [])),
        "survivors": len(state.get("survivor_hypotheses", [])),
        "dead_ends_recorded": len(rejected),
    }
    return state


# ── Build the graph ───────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Construct the LangGraph pipeline.

    Scout nodes run sequentially after ingestion (LangGraph parallel fan-out
    can be enabled if the runtime supports it — see README for async option).
    """
    g = StateGraph(ResearchState)

    # Nodes
    g.add_node("ingest", node_ingest)
    g.add_node("micro_scout", node_micro)
    g.add_node("static_scout", node_static)
    g.add_node("linguistic_scout", node_linguistic)
    g.add_node("symbolic_scout", node_symbolic)
    g.add_node("math_scout", node_math)
    g.add_node("freq_scout", node_freq)
    g.add_node("deep_scout", node_deep)
    g.add_node("the_fool", node_fool)
    g.add_node("synthesizer", node_synthesizer)
    g.add_node("scorer", node_scorer)
    g.add_node("linker", node_linker)
    g.add_node("report", node_report)

    # Edges: ingest → all scouts (fan-out pattern)
    g.set_entry_point("ingest")
    for scout in [
        "micro_scout", "static_scout", "linguistic_scout",
        "symbolic_scout", "math_scout", "freq_scout", "deep_scout"
    ]:
        g.add_edge("ingest", scout)
        g.add_edge(scout, "the_fool")

    # Fan-in: all scouts complete → fool → synthesizer → scorer → linker → report
    g.add_edge("the_fool", "synthesizer")
    g.add_edge("synthesizer", "scorer")
    g.add_edge("scorer", "linker")
    g.add_edge("linker", "report")
    g.add_edge("report", END)

    return g


def compile_graph():
    return build_graph().compile()
