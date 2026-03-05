"""
src/agents/the_fool.py
──────────────────────
The Fool — Primary Auditor & Negative Feedback Driver

The Fool does NOT analyze the text. It interrogates the other Scouts.
Before any hypothesis reaches the Synthesizer, it must survive The Fool.

The Fool asks fundamental questions to expose:
  - Unjustified complexity (modern framework forced onto ancient text)
  - Missing goal link (hypothesis not connected to Muqattaat meaning)
  - Circular reasoning
  - Statistical noise mistaken for pattern

Hypotheses that fail are saved as NEGATIVE NODES (dead ends) in the
knowledge graph — preventing the system from re-walking dead paths.

CRITICAL RULE: The Fool ALWAYS rejects any hypothesis where goal_link
is empty, generic, or fails to address Muqattaat meaning specifically.
"""

from __future__ import annotations
from src.core.state import ResearchState, Hypothesis, RejectedHypothesis

# ── Rejection criteria ────────────────────────────────────────────────────────

# These signals in goal_link indicate it is too generic
GENERIC_GOAL_SIGNALS = [
    "pattern found", "statistical anomaly", "interesting observation",
    "further study needed", "may be relevant", "could indicate",
    "unclear", "unknown", "to be determined",
]

# Minimum evidence snippets for a hypothesis to pass
MIN_EVIDENCE = 1

# Maximum transformation steps before The Fool demands justification
COMPLEXITY_THRESHOLD = 5


class TheFool:
    """
    The Fool interrogates every hypothesis before it reaches the Synthesizer.
    Survivors go to state["survivor_hypotheses"].
    Failures go to state["rejected_hypotheses"] as Negative Nodes.
    """

    name = "TheFool"

    def run(self, state: ResearchState) -> ResearchState:
        raw: list[Hypothesis] = state.get("raw_hypotheses", [])
        survivors: list[Hypothesis] = []
        rejected: list[RejectedHypothesis] = []

        for h in raw:
            verdict, question, reason = self._interrogate(h)
            if verdict == "PASS":
                survivors.append(h)
            else:
                rejected.append(RejectedHypothesis(
                    original=h,
                    rejection_reason=reason,
                    fool_question=question,
                ))

        state["survivor_hypotheses"] = survivors
        state["rejected_hypotheses"] = state.get("rejected_hypotheses", []) + rejected
        return state

    def _interrogate(self, h: Hypothesis) -> tuple[str, str, str]:
        """
        Returns (verdict, question_asked, reason_for_verdict).
        verdict: "PASS" or "REJECT"
        """

        # ── Test 1: Goal link check ────────────────────────────────────────
        if not h.goal_link or len(h.goal_link.strip()) < 15:
            return (
                "REJECT",
                "How does this finding help us understand what the Muqattaat mean?",
                "Goal link is missing or too vague to establish connection to Muqattaat meaning.",
            )

        if any(sig in h.goal_link.lower() for sig in GENERIC_GOAL_SIGNALS):
            return (
                "REJECT",
                "This goal link is generic. What SPECIFICALLY does this tell us about the Muqattaat?",
                f"Goal link contains generic signal: '{h.goal_link[:80]}'",
            )

        # ── Test 2: Evidence check ─────────────────────────────────────────
        if len(h.evidence_snippets) < MIN_EVIDENCE:
            return (
                "REJECT",
                "Show me the evidence. What in the text actually supports this?",
                "No evidence snippets provided. Hypothesis is unanchored.",
            )

        # ── Test 3: Complexity justification ──────────────────────────────
        if h.transformation_steps > COMPLEXITY_THRESHOLD:
            # Demand justification — check if metadata carries it
            justified = h.metadata.get("complexity_justified", False)
            if not justified:
                return (
                    "REJECT",
                    (
                        f"You used {h.transformation_steps} transformation steps. "
                        "Why is this complexity necessary? "
                        "Are you forcing a modern mathematical framework onto an ancient structure? "
                        "Prove the complexity is essential."
                    ),
                    f"Unjustified complexity: {h.transformation_steps} steps without justification in metadata.",
                )

        # ── Test 4: Surah anchoring ────────────────────────────────────────
        if not h.surah_refs:
            return (
                "REJECT",
                "Which Surah(s) is this actually about? Ground this in a specific text location.",
                "Hypothesis has no Surah references — cannot be verified against the text.",
            )

        # ── Test 5: Circular reasoning detector ───────────────────────────
        if h.description.lower() in h.goal_link.lower():
            return (
                "REJECT",
                "You are using the finding to justify itself. That is circular reasoning.",
                "Description and goal_link are suspiciously similar — possible circular logic.",
            )

        # ── PASS ───────────────────────────────────────────────────────────
        return ("PASS", "", "")
