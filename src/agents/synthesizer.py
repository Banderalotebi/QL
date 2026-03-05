"""
src/agents/synthesizer.py
──────────────────────────
Synthesizer — Cross-Scout Theory Merger

Takes all survivor hypotheses (post-Fool) and looks for overlapping
anomalies across different paradigms. Merges corroborated findings
into single, stronger synthesized theories.

Rule: 2+ scouts independently pointing at the same phenomenon =
      synthesized theory with combined evidence and elevated credibility.

PRIMARY GOAL FOCUS:
  Synthesized theories receive a `goal_link` that explicitly names
  the strongest candidate theory of Muqattaat meaning implied by
  the cross-scout convergence.
"""

from __future__ import annotations
from collections import defaultdict
from src.agents.base_agent import BaseScout
from src.core.state import ResearchState, Hypothesis


# Keyword clusters for grouping related hypotheses
THEME_KEYWORDS: dict[str, list[str]] = {
    "frequency_signature":   ["dominance", "frequency", "ratio", "dominant"],
    "geometric_symbol":      ["geometric", "connection", "isolated", "undotted", "topology"],
    "numerical_encoding":    ["abjad", "numerical", "weight", "inverse", "correlation"],
    "organizational_marker": ["consecutive", "block", "positional", "boundary", "section"],
    "phonetic_key":          ["phonetic", "consonant", "rhythm", "syllable", "tashkeel"],
    "transition_grammar":    ["transition", "pathway", "grammar", "rigid", "successor"],
}


def classify_theme(h: Hypothesis) -> str:
    """Assign a theme cluster to a hypothesis based on its description."""
    combined = (h.description + h.goal_link).lower()
    scores: dict[str, int] = {}
    for theme, keywords in THEME_KEYWORDS.items():
        scores[theme] = sum(1 for kw in keywords if kw in combined)
    return max(scores, key=lambda t: scores[t]) if any(scores.values()) else "general"


class Synthesizer:
    """Merges survivor hypotheses into cross-scout synthesized theories."""

    name = "Synthesizer"

    def run(self, state: ResearchState) -> ResearchState:
        survivors: list[Hypothesis] = state.get("survivor_hypotheses", [])

        # Group by theme
        by_theme: dict[str, list[Hypothesis]] = defaultdict(list)
        for h in survivors:
            theme = classify_theme(h)
            by_theme[theme].append(h)

        synthesized: list[Hypothesis] = []

        for theme, group in by_theme.items():
            if len(group) == 1:
                # Single hypothesis — pass through unchanged
                synthesized.append(group[0])
                continue

            # Multiple scouts agree on this theme — merge
            all_scouts = list({h.source_scout for h in group})
            all_evidence = []
            for h in group:
                all_evidence.extend(h.evidence_snippets)
            all_surahs = list({s for h in group for s in h.surah_refs})
            max_steps = max(h.transformation_steps for h in group)

            # Compose a merged goal_link from the strongest constituent
            best = max(group, key=lambda h: len(h.goal_link))

            merged = Hypothesis(
                source_scout=f"Synthesizer[{'+'.join(all_scouts)}]",
                description=(
                    f"[SYNTHESIZED — {len(group)} scouts converge on '{theme}'] "
                    f"{group[0].description[:120]}... "
                    f"(+ {len(group)-1} corroborating observations)"
                ),
                goal_link=(
                    f"Multi-scout convergence on '{theme}' strengthens the theory that: "
                    f"{best.goal_link}"
                ),
                transformation_steps=max_steps,
                evidence_snippets=list(dict.fromkeys(all_evidence))[:10],  # deduplicated
                surah_refs=sorted(set(all_surahs)),
                metadata={
                    "synthesized_from": all_scouts,
                    "theme": theme,
                    "scout_count": len(group),
                    "dual_layer_corroborated": len(all_scouts) >= 2,
                    "complexity_justified": any(
                        h.metadata.get("complexity_justified") for h in group
                    ),
                },
            )
            synthesized.append(merged)

        state["synthesized_theories"] = synthesized
        return state
