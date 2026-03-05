"""
src/agents/freq_scout.py
────────────────────────
Frequency Scout — Artificial Dominance Detector

Tracks if letters that appear in the Muqattaat of a Surah artificially
dominate the frequency distribution of that ENTIRE Surah.
Uses Rasm layer only.

PRIMARY GOAL FOCUS:
  If a Surah opens with "ALM" and the letters Alif, Lam, Mim then appear
  at unusually high frequency throughout the chapter body, the Muqattaat
  are functioning as a thematic frequency key — their 'meaning' is
  "this Surah is built on these phonetic pillars."
"""

from __future__ import annotations
from collections import Counter
from src.agents.base_agent import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.data.muqattaat import BY_SURAH, MUQATTAAT_SURAHS

# Approximate Arabic Unicode for the 14 Muqattaat letters
MUQATTAAT_ARABIC_CHARS = {
    "Alif": "ا", "Lam": "ل", "Mim": "م", "Ra": "ر",
    "Sad": "ص", "Ta": "ط", "Sin": "س", "Ha": "ح",
    "Kaf": "ك", "Ya": "ي", "Ain": "ع", "Nun": "ن",
    "Qaf": "ق", "Ha2": "ه",
}


class FreqScout(BaseScout):
    name = "FreqScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []
        rasm_matrices = self.get_rasm_matrices(state)

        for snum, matrix in rasm_matrices.items():
            if not matrix.is_muqattaat_surah:
                continue
            entry = BY_SURAH[snum]
            letters = matrix.letter_sequence
            if not letters:
                continue

            freq = Counter(letters)
            total = len(letters)

            # Get Arabic chars for this Surah's Muqattaat letters
            muq_chars = [
                MUQATTAAT_ARABIC_CHARS.get(name)
                for name in entry.letter_names
                if MUQATTAAT_ARABIC_CHARS.get(name)
            ]

            # Calculate expected vs actual frequency
            expected_per_letter = total / 28.0  # 28 Arabic letters baseline
            muq_dominance_scores = []
            for ch in muq_chars:
                actual = freq.get(ch, 0)
                dominance = actual / expected_per_letter if expected_per_letter > 0 else 0
                muq_dominance_scores.append((ch, actual, round(dominance, 3)))

            dominant = [(ch, a, d) for ch, a, d in muq_dominance_scores if d > 1.2]

            if dominant:
                hypotheses.append(self.make_hypothesis(
                    description=(
                        f"Surah {snum} ({entry.surah_name}): Muqattaat letters show "
                        f"above-baseline dominance: {dominant}. "
                        f"These letters occur >{1.2:.0%} of expected frequency."
                    ),
                    goal_link=(
                        f"When the specific letters of the Muqattaat (here: {entry.transliteration}) "
                        f"are artificially dominant throughout the Surah body, it confirms they are not "
                        f"decorative. Their meaning appears to be a FREQUENCY SIGNATURE — "
                        f"the Muqattaat declare: 'this chapter is phonetically governed by these letters.'"
                    ),
                    transformation_steps=2,
                    evidence_snippets=[
                        f"Muqattaat: {entry.transliteration}",
                        f"Dominant letters: {dominant}",
                        f"Total letters in Surah: {total}",
                    ],
                    surah_refs=[snum],
                ))

        return hypotheses
