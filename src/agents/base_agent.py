"""
src/agents/base_agent.py
────────────────────────
Abstract base class for all Scout agents and The Fool.

All agents MUST:
  1. Implement `run(state) -> state`
  2. Only append to `state["raw_hypotheses"]` (never other agents' keys)
  3. Set `goal_link` on every Hypothesis explaining Muqattaat relevance
  4. Check `state["known_dead_ends"]` before attempting a known-dead approach
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from src.core.state import ResearchState, Hypothesis, RasmMatrix, TashkeelMatrix
from src.data.muqattaat import MUQATTAAT_SURAHS, BY_SURAH


class BaseScout(ABC):
    """Abstract base for all Scout agents."""

    name: str = "BaseScout"

    # Which layer this scout consumes (enforced at runtime)
    consumes_rasm: bool = True
    consumes_tashkeel: bool = False

    def run(self, state: ResearchState) -> ResearchState:
        """
        Main entry point called by LangGraph.
        Validates layer access, checks dead-ends, then calls analyze().
        """
        # Enforce layer purity
        if self.consumes_tashkeel and not self.consumes_rasm:
            # This scout must NOT access rasm_matrices
            pass
        if self.consumes_rasm and not self.consumes_tashkeel:
            # This scout must NOT access tashkeel_matrices
            pass

        new_hypotheses = self.analyze(state)

        # Filter known dead-ends
        dead_ends = state.get("known_dead_ends", [])
        filtered = []
        for h in new_hypotheses:
            fingerprint = self._fingerprint(h)
            if fingerprint in dead_ends:
                continue  # Skip known dead path
            filtered.append(h)

        state.setdefault("raw_hypotheses", [])
        state["raw_hypotheses"].extend(filtered)
        return state

    @abstractmethod
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Core analysis logic. Return a list of Hypothesis objects.
        Each MUST have a non-empty goal_link.
        """
        ...

    def make_hypothesis(
        self,
        description: str,
        goal_link: str,
        transformation_steps: int,
        evidence_snippets: list[str] | None = None,
        surah_refs: list[int] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Hypothesis:
        """Convenience factory ensuring all required fields are set."""
        return Hypothesis(
            source_scout=self.name,
            description=description,
            goal_link=goal_link,
            transformation_steps=transformation_steps,
            evidence_snippets=evidence_snippets or [],
            surah_refs=surah_refs or [],
            metadata=metadata or {},
        )

    def get_rasm_matrices(self, state: ResearchState) -> dict[int, RasmMatrix]:
        """Safe accessor — raises if called from a Tashkeel-only scout."""
        if not self.consumes_rasm:
            raise RuntimeError(f"{self.name} is not allowed to access Rasm matrices (layer purity).")
        return state.get("rasm_matrices", {})

    def get_tashkeel_matrices(self, state: ResearchState) -> dict[int, TashkeelMatrix]:
        """Safe accessor — raises if called from a Rasm-only scout."""
        if not self.consumes_tashkeel:
            raise RuntimeError(f"{self.name} is not allowed to access Tashkeel matrices (layer purity).")
        return state.get("tashkeel_matrices", {})

    def get_muqattaat_surahs(self, state: ResearchState) -> dict[int, RasmMatrix]:
        """Return only the Rasm matrices for Muqattaat Surahs — priority targets."""
        return {
            snum: mat
            for snum, mat in self.get_rasm_matrices(state).items()
            if snum in MUQATTAAT_SURAHS
        }

    @staticmethod
    def _fingerprint(h: Hypothesis) -> str:
        """Create a short fingerprint for dead-end detection."""
        return f"{h.source_scout}::{h.description[:60]}"
