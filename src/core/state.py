"""
src/core/state.py
─────────────────
Central shared memory object (ResearchState) passed through the entire
LangGraph pipeline. Every agent reads from and writes to this structure.

PRIMARY GOAL: Discover the meaning of the Muqattaat (Disjointed Letters).
All hypotheses MUST link back to this goal via `goal_link`.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, TypedDict
import unicodedata


# ──────────────────────────────────────────────────────────────────────────────
# Hypothesis — the atomic unit of discovery
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Hypothesis:
    """
    An observation produced by a Scout agent.

    Every hypothesis MUST have a non-empty `goal_link` that explains
    how this finding contributes to understanding the Muqattaat.
    The Fool will reject any hypothesis with a missing or generic goal_link.
    """
    source_scout: str                      # Which scout generated this
    goal_link: str                         # How does this help decode Muqattaat?
    description: str                       # Human-readable finding
    transformation_steps: int             # How many logical steps to reach this
    evidence_snippets: list[str] = field(default_factory=list)  # Raw evidence
    surah_refs: list[int] = field(default_factory=list)          # Surah numbers
    score: float = 0.0                     # Filled by Occam Scorer
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.goal_link.strip():
            raise ValueError(
                f"Hypothesis from {self.source_scout} is missing goal_link. "
                "Every hypothesis MUST explain its connection to the Muqattaat."
            )


@dataclass
class RejectedHypothesis:
    """Record of a hypothesis The Fool destroyed — saved as a Negative Node."""
    original: Hypothesis
    rejection_reason: str
    fool_question: str  # The basic question that killed it


# ──────────────────────────────────────────────────────────────────────────────
# Dual-Layer Text Matrices
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RasmMatrix:
    """
    Layer A — The Foundational Skeleton.
    Pure skeletal Arabic letters, all diacritics stripped.
    Fed ONLY to: MathScout, SymbolicScout, MicroScout, StaticScout, FreqScout.
    """
    surah_number: int
    raw_rasm: str                          # Cleaned skeletal text
    letter_sequence: list[str]            # Individual letter tokens
    is_surah_start: bool = False
    isolated_sequences: list[str] = field(default_factory=list)  # Muqattaat
    is_muqattaat_surah: bool = False


@dataclass
class TashkeelMatrix:
    """
    Layer B — The Phonetic Overlay.
    Diacritics (Fatha, Kasra, Damma, Sukun, Shadda) mapped by position.
    Fed ONLY to: LinguisticScout, DeepScout.
    """
    surah_number: int
    diacritic_map: dict[int, str]         # position → diacritic char
    syllable_structure: list[str]         # Derived syllable tokens
    phonetic_rhythm: str                  # Compact rhythm string (C/V pattern)


# ──────────────────────────────────────────────────────────────────────────────
# ResearchState — the pipeline's shared memory
# ──────────────────────────────────────────────────────────────────────────────

class ResearchState(TypedDict, total=False):
    """
    The single object passed between all nodes in the LangGraph pipeline.

    KEY SECTIONS:
    ─────────────
    input_*          Raw inputs
    rasm_matrices    Layer A data (skeletal)
    tashkeel_matrices Layer B data (phonetic)
    raw_hypotheses   All Scout outputs (pre-Fool)
    survivor_hypotheses Hypotheses that passed The Fool
    rejected_hypotheses Dead-ends saved as Negative Nodes
    synthesized_theories Cross-scout merged findings
    scored_theories  Final ranked theories
    graph_nodes      What was written to the knowledge graph this run
    lab_report       Final human-readable output
    """

    # ── Input ──────────────────────────────────────────────────────────────
    input_surah_numbers: list[int]         # Which Surahs to analyze
    input_focus: str                       # "muqattaat" | "full_surah" | "comparison"

    # ── Processed layers ───────────────────────────────────────────────────
    rasm_matrices: dict[int, RasmMatrix]        # surah_num → RasmMatrix
    tashkeel_matrices: dict[int, TashkeelMatrix]  # surah_num → TashkeelMatrix
    muqattaat_registry: dict[int, str]           # surah_num → Muqattaat string

    # ── Scout working memory (each scout appends here) ─────────────────────
    raw_hypotheses: list[Hypothesis]

    # ── The Fool output ────────────────────────────────────────────────────
    survivor_hypotheses: list[Hypothesis]
    rejected_hypotheses: list[RejectedHypothesis]

    # ── Synthesizer output ─────────────────────────────────────────────────
    synthesized_theories: list[Hypothesis]

    # ── Occam Scorer output ────────────────────────────────────────────────
    scored_theories: list[Hypothesis]

    # ── Knowledge Graph tracking ───────────────────────────────────────────
    graph_nodes: list[dict[str, Any]]      # Nodes written this run
    known_dead_ends: list[str]             # Dead-end fingerprints from graph DB

    # ── Final output ───────────────────────────────────────────────────────
    lab_report: dict[str, Any]
    run_id: str                            # UUID for this analysis run
