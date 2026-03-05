# src/core/state_definitions.py
from __future__ import annotations
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
from src.core.leaders import AlchemistLeader

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
_alchemist_leader = AlchemistLeader()

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

def _run_alchemist(state: ResearchState) -> ResearchState:
    return _alchemist_leader.run(state)
