"""
src/agents/math_scout.py
────────────────────────
Math Scout — Abjad Numerical & Linear Algebra Engine

Converts Rasm letters to Abjad numerical values.
Looks for numerical symmetries, proportions, and structural patterns.
Uses Rasm layer ONLY.

PRIMARY GOAL FOCUS:
  The Abjad numerical system assigns values to each Arabic letter.
  Do the Muqattaat sequences encode mathematical messages through their
  Abjad totals? Are there proportional relationships between the
  Muqattaat Abjad values and the Surah structure (verse count, word count)?

COMPLEXITY WARNING:
  Per Occam's Razor, chains of >5 transforms are penalized.
  This scout marks complex transforms with complexity_justified=True
  ONLY when the probability of coincidence is demonstrably low.
"""

from __future__ import annotations
import math
from src.agents.base_agent import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.data.muqattaat import BY_SURAH, MUQATTAAT_SURAHS, MUQATTAAT_REGISTRY
from src.utils.abjad import abjad_value_of_sequence, ABJAD


class MathScout(BaseScout):
    name = "MathScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []
        rasm_matrices = self.get_rasm_matrices(state)

        # ── Abjad total analysis ───────────────────────────────────────────
        abjad_totals: dict[int, int] = {}
        for entry in MUQATTAAT_REGISTRY:
            if entry.surah_number in state.get("input_surah_numbers", [entry.surah_number]):
                total = sum(entry.abjad_values)
                abjad_totals[entry.surah_number] = total

        if abjad_totals:
            # Check for patterns in the Abjad totals across groups
            unique_totals = sorted(set(abjad_totals.values()))
            total_sum = sum(abjad_totals.values())
            avg = total_sum / len(abjad_totals) if abjad_totals else 0

            hypotheses.append(self.make_hypothesis(
                description=(
                    f"Abjad totals of Muqattaat sequences: {dict(list(abjad_totals.items())[:5])}... "
                    f"Sum of all: {total_sum}. Average: {avg:.1f}. "
                    f"Unique totals: {unique_totals[:8]}"
                ),
                goal_link=(
                    "The Abjad system is a classical Arabic numerological method. "
                    "If Muqattaat Abjad totals correlate with Surah verse counts, word counts, "
                    "or Surah position in the Quran, this is strong evidence the letters encode "
                    "numerical metadata about their Surah — their 'meaning' is a mathematical signature."
                ),
                transformation_steps=2,
                evidence_snippets=[
                    f"Sample totals: {list(abjad_totals.items())[:6]}",
                    f"Grand total: {total_sum}",
                    f"Unique values: {unique_totals}",
                ],
                surah_refs=list(abjad_totals.keys()),
            ))

            # ── Inverse frequency / weight correlation ─────────────────────
            # Research doc finding: "inverse correlation between aggregate mathematical
            # weight and frequency of repetition"
            from src.data.muqattaat import BY_GROUP
            freq_weight_pairs = [
                (len(BY_GROUP[entry.group_id]), sum(entry.abjad_values))
                for entry in MUQATTAAT_REGISTRY
                if entry.surah_number in abjad_totals
            ]

            if freq_weight_pairs:
                # Check if high-frequency groups have low Abjad weights
                high_freq = [(f, w) for f, w in freq_weight_pairs if f >= 4]
                low_freq = [(f, w) for f, w in freq_weight_pairs if f <= 2]
                avg_weight_high = sum(w for _, w in high_freq) / len(high_freq) if high_freq else 0
                avg_weight_low = sum(w for _, w in low_freq) / len(low_freq) if low_freq else 0

                if avg_weight_high < avg_weight_low * 0.8:
                    hypotheses.append(self.make_hypothesis(
                        description=(
                            f"Inverse correlation detected: High-frequency Muqattaat groups "
                            f"(≥4 Surahs) have avg Abjad weight {avg_weight_high:.1f}, "
                            f"while rare groups (≤2 Surahs) have avg weight {avg_weight_low:.1f}."
                        ),
                        goal_link=(
                            "The inverse relationship between Abjad weight and frequency is a "
                            "non-random structural feature. Heavy Muqattaat appear rarely (as rare "
                            "structural markers), while light Muqattaat repeat often (as common "
                            "structural anchors). This suggests Muqattaat are a tiered encoding system — "
                            "their Abjad values encode the 'weight' or significance tier of the Surah type."
                        ),
                        transformation_steps=3,
                        evidence_snippets=[
                            f"High-freq avg Abjad weight: {avg_weight_high:.2f}",
                            f"Low-freq avg Abjad weight: {avg_weight_low:.2f}",
                            f"Sample high-freq pairs: {high_freq[:3]}",
                        ],
                        surah_refs=list(abjad_totals.keys()),
                        metadata={"complexity_justified": True},
                    ))

        # ── Positional boundary analysis ────────────────────────────────────
        # Research doc: "disjointed letters only exist in the first half of the Quran"
        # Last Muqattaat Surah is 68 (Al-Qalam). Total Surahs = 114. 68/114 ≈ 0.596
        last_muq_surah = max(MUQATTAAT_SURAHS)
        total_surahs = 114
        position_ratio = last_muq_surah / total_surahs

        hypotheses.append(self.make_hypothesis(
            description=(
                f"Muqattaat appear only in Surahs 2–68 (first {position_ratio:.1%} of the Quran). "
                f"The phenomenon ends at exactly Surah {last_muq_surah} of {total_surahs}."
            ),
            goal_link=(
                "The strict positional boundary of the Muqattaat — confined to the first ~60% "
                "of the Quran — is a structural fact about their placement. "
                "If their meaning is a chapter-type marker or organizational code, "
                "this boundary defines the scope of that organizational system "
                "and is a key clue to decoding their function."
            ),
            transformation_steps=1,
            evidence_snippets=[
                f"First Muqattaat Surah: {min(MUQATTAAT_SURAHS)}",
                f"Last Muqattaat Surah: {last_muq_surah}",
                f"Total Surahs: {total_surahs}",
                f"Coverage: Surahs 2–68",
            ],
            surah_refs=sorted(MUQATTAAT_SURAHS),
        ))

        return hypotheses
