# src/core/state.py
# ResearchState TypedDict and Hypothesis dataclass for the Muqattaat Cryptanalytic Lab

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


@dataclass
class Hypothesis:
    """
    A single research hypothesis produced by a Scout agent.

    All fields are required. `goal_link` must be a non-empty, specific sentence
    explaining how this finding contributes to discovering the meaning of the Muqattaat.
    The Fool will reject any Hypothesis where goal_link is empty or generic.
    """

    source_scout: str
    """Name of the Scout agent that produced this hypothesis."""

    goal_link: str
    """
    Plain-English sentence explaining how this finding contributes to discovering
    the meaning of the Muqattaat. Must be specific — not generic boilerplate.
    """

    description: str
    """Human-readable summary of what was found."""

    transformation_steps: int
    """
    Number of logical operations / transformations applied to reach this hypothesis.
    Feeds directly into the Occam penalty: score *= exp(-0.15 * transformation_steps).
    """

    evidence_snippets: list[str]
    """Raw data excerpts, counts, or quotes that support this hypothesis."""

    surah_refs: list[int]
    """Surah numbers (1-indexed) that this hypothesis references."""

    score: float = 0.0
    """Occam-penalised score assigned by the Scorer node. Default 0 until scored."""

    fingerprint: str = ""
    """
    Short hash/slug used by the Knowledge Graph to detect duplicate or similar findings.
    Set by the KnowledgeGraphLinker node.
    """

    layer: str = "rasm"
    """
    Which text layer this hypothesis operates on: 'rasm' or 'tashkeel'.
    Enforces Dual-Matrix Purity — checked by The Fool.
    """

    def __post_init__(self) -> None:
        # Validate required string fields are non-empty
        if not self.source_scout.strip():
            raise ValueError("Hypothesis.source_scout must not be empty.")
        if not self.goal_link.strip():
            raise ValueError(
                "Hypothesis.goal_link must not be empty. "
                "Every hypothesis must explain how it contributes to discovering "
                "the meaning of the Muqattaat."
            )
        if not self.description.strip():
            raise ValueError("Hypothesis.description must not be empty.")
        if self.transformation_steps < 0:
            raise ValueError("Hypothesis.transformation_steps must be >= 0.")
        if not self.evidence_snippets:
            raise ValueError(
                "Hypothesis.evidence_snippets must contain at least one entry."
            )
        if not self.surah_refs:
            raise ValueError(
                "Hypothesis.surah_refs must reference at least one Surah."
            )
        if self.layer not in ("rasm", "tashkeel"):
            raise ValueError(
                f"Hypothesis.layer must be 'rasm' or 'tashkeel', got '{self.layer}'."
            )


@dataclass
class RejectedHypothesis:
    """A hypothesis that The Fool has rejected, stored with the reason."""

    hypothesis: Hypothesis
    reason: str
    auditor: str = "TheFool"


class ResearchState(TypedDict, total=False):
    """
    Shared memory dict passed between all nodes in the LangGraph state machine.

    Keys are written by specific nodes only — no agent modifies another agent's key.
    """

    # ── Ingestion outputs ────────────────────────────────────────────────────
    surah_numbers: list[int]
    """Surah numbers selected for this run."""

    rasm_matrices: dict[int, list[str]]
    """
    Layer A — skeletal (Rasm) letter sequences, keyed by Surah number.
    Rasm scouts ONLY read from this key.
    """

    tashkeel_matrices: dict[int, list[str]]
    """
    Layer B — diacritic (Tashkeel) overlays, keyed by Surah number.
    Tashkeel scouts ONLY read from this key.
    """

    muqattaat_map: dict[int, str]
    """
    Maps Surah number → its Muqattaat sequence string (e.g. {2: 'الم'}).
    Only populated for Surahs that open with Muqattaat.
    """

    known_dead_ends: list[str]
    """
    Fingerprints of paths already proven dead, loaded from the Knowledge Graph
    before scouts run. Scouts should skip any path whose fingerprint appears here.
    """

    raw_text: dict[int, str]
    """Original Uthmani text per Surah, before any processing."""

    # ── Scout outputs ────────────────────────────────────────────────────────
    raw_hypotheses: list[Hypothesis]
    """
    All hypotheses produced by Scout agents. Each Scout APPENDS to this list.
    No scout may modify another scout's entries.
    """

    # ── Auditor outputs ──────────────────────────────────────────────────────
    survivor_hypotheses: list[Hypothesis]
    """Hypotheses that passed The Fool's interrogation."""

    rejected_hypotheses: list[RejectedHypothesis]
    """Hypotheses rejected by The Fool, with reasons. Written by TheFool only."""

    # ── Synthesizer outputs ──────────────────────────────────────────────────
    synthesized_theories: list[Hypothesis]
    """
    Merged / cross-scout theories produced by the Synthesizer.
    Each entry may combine evidence from multiple survivor hypotheses.
    """

    # ── Scorer outputs ───────────────────────────────────────────────────────
    scored_theories: list[Hypothesis]
    """Synthesized theories with `.score` populated by the Occam Scorer."""

    # ── Knowledge Graph outputs ──────────────────────────────────────────────
    graph_save_status: str
    """'OK' or error message from the KnowledgeGraphLinker node."""

    # ── Run metadata ─────────────────────────────────────────────────────────
    focus: str
    """Run focus mode, e.g. 'muqattaat'."""

    errors: list[str]
    """Non-fatal errors accumulated during the run."""
