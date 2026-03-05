# src/core/graph.py
# LangGraph state machine definition for the Muqattaat Cryptanalytic Lab

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from src.core.state import ResearchState

# ── Node imports ──────────────────────────────────────────────────────────────
# Each import is guarded so that missing agent stubs produce a clear error.

from src.data.ingestion import ingest_surah  # noqa: F401 — used via wrapper

from src.agents.micro_scout import MicroScout
from src.agents.static_scout import StaticScout
from src.agents.linguistic_scout import LinguisticScout
from src.agents.symbolic_scout import SymbolicScout
from src.agents.math_scout import MathScout
from src.agents.freq_scout import FreqScout
from src.agents.deep_scout import DeepScout
from src.agents.the_fool import TheFool
from src.agents.synthesizer import Synthesizer
from src.core.scorer import score_all
from src.data.knowledge_graph import KnowledgeGraphLinker


# ── Node wrappers ─────────────────────────────────────────────────────────────
# LangGraph nodes must be plain callables: (state) -> state.
# We instantiate agents once at module load to avoid repeated init overhead.

_micro_scout = MicroScout()
_static_scout = StaticScout()
_linguistic_scout = LinguisticScout()
_symbolic_scout = SymbolicScout()
_math_scout = MathScout()
_freq_scout = FreqScout()
_deep_scout = DeepScout()
_the_fool = TheFool()
_synthesizer = Synthesizer()
_kg_linker = KnowledgeGraphLinker()


def _run_ingestion(state: ResearchState) -> ResearchState:
    """
    Ingestion node: load raw text, split Rasm/Tashkeel matrices,
    tag Muqattaat sequences, and pre-populate known_dead_ends from
    the Knowledge Graph.
    """
    from src.data.ingestion import run_ingestion_pipeline
    return run_ingestion_pipeline(state)


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