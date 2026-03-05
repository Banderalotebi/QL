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
from src.core.state import ResearchState, Hypothesis, RejectedHypothesis

class TheFool:
    """
    The Fool - Quality control agent that interrogates hypotheses for logical rigor.
    Rejects hypotheses with generic goal_link, circular reasoning, or insufficient evidence.
    """
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Interrogate all raw hypotheses and separate survivors from rejects.
        """
        raw_hypotheses = state.get("raw_hypotheses", [])
        survivors = []
        rejected = []
        
        for h in raw_hypotheses:
            verdict, reason, details = self._interrogate(h)
            
            if verdict == "PASS":
                survivors.append(h)
            else:
                rejected.append(RejectedHypothesis(
                    hypothesis=h,
                    reason=reason,
                    auditor="TheFool"
                ))
        
        state["survivor_hypotheses"] = survivors
        state["rejected_hypotheses"] = rejected
        
        return state
    
    def _interrogate(self, h: Hypothesis) -> tuple[str, str, str]:
        """
        Interrogate a single hypothesis.
        
        Returns:
            Tuple of (verdict, reason, details) where verdict is "PASS" or "REJECT"
        """
        
        # Test 1: Generic goal_link detection
        generic_phrases = [
            "this is interesting",
            "may be relevant",
            "could be significant",
            "worth investigating",
            "appears to be",
            "seems to",
            "might indicate",
            "could suggest",
            "potentially",
            "possibly"
        ]
        
        goal_lower = h.goal_link.lower()
        if any(phrase in goal_lower for phrase in generic_phrases):
            return (
                "REJECT",
                "Generic goal_link detected",
                f"Goal link contains generic language: '{h.goal_link}'"
            )
        
        # Test 2: Empty or too short goal_link
        if len(h.goal_link.strip()) < 20:
            return (
                "REJECT",
                "Goal link too short or empty",
                f"Goal link must be at least 20 characters, got {len(h.goal_link.strip())}"
            )
        
        # Test 3: Circular reasoning detection
        if h.description.strip() == h.goal_link.strip():
            return (
                "REJECT",
                "Circular reasoning detected",
                "Description and goal_link are identical — circular logic detected."
            )
        
        # Test 4: Must mention Muqattaat specifically
        muqattaat_keywords = [
            "muqattaat", "isolated letter", "disjointed letter", "الحروف المقطعة",
            "alif lam mim", "alm", "alr", "alms", "ha mim", "ya sin", "ta ha",
            "phonetic key", "consonantal", "letter sequence", "opening letter"
        ]
        
        if not any(kw in goal_lower for kw in muqattaat_keywords):
            return (
                "REJECT",
                "Goal link does not mention Muqattaat",
                "Every hypothesis must explicitly connect to the Muqattaat mystery"
            )
        
        # Test 5: Evidence sufficiency
        if len(h.evidence_snippets) < 1:
            return (
                "REJECT",
                "Insufficient evidence",
                "At least one evidence snippet required"
            )
        
        # Test 6: Surah reference validation
        if not h.surah_refs:
            return (
                "REJECT",
                "No Surah references",
                "Must reference at least one Surah"
            )
        
        # Test 7: Layer purity check
        if h.layer not in ("rasm", "tashkeel"):
            return (
                "REJECT",
                "Invalid layer specification",
                f"Layer must be 'rasm' or 'tashkeel', got '{h.layer}'"
            )
        
        return ("PASS", "Hypothesis accepted", "All tests passed")
