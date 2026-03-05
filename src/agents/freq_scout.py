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
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class FreqScout(BaseScout):
    """
    Advanced frequency analysis with statistical patterns.
    """
    
    name = "FreqScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Perform advanced frequency analysis on Muqattaat letters.
        """
        hypotheses = []
        
        rasm_matrices = state.get("rasm_matrices", {})
        muqattaat_map = state.get("muqattaat_map", {})
        
        for surah_num in rasm_matrices:
            if surah_num not in muqattaat_map:
                continue
                
            muqattaat = muqattaat_map[surah_num]
            rasm_letters = rasm_matrices[surah_num]
            
            if not rasm_letters:
                continue
            
            # Advanced frequency analysis with distribution patterns
            muqattaat_letters = set(muqattaat)
            total_letters = len(rasm_letters)
            
            # Calculate frequency distribution
            letter_freq = {}
            for letter in rasm_letters:
                letter_freq[letter] = letter_freq.get(letter, 0) + 1
            
            # Focus on Muqattaat letter frequencies
            muqattaat_freq = {letter: letter_freq.get(letter, 0) for letter in muqattaat_letters}
            total_muqattaat = sum(muqattaat_freq.values())
            
            if total_muqattaat > 0:
                # Calculate statistical measures
                frequencies = list(muqattaat_freq.values())
                max_freq = max(frequencies)
                min_freq = min(frequencies)
                freq_range = max_freq - min_freq
                
                # Calculate dominance ratio
                dominance_ratio = total_muqattaat / total_letters
                
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat letters {muqattaat} exhibit a frequency distribution with range {freq_range} and dominance ratio {dominance_ratio:.3f} in Surah {surah_num}, revealing the statistical signature that identifies the chapter's consonantal DNA.",
                    description=f"Statistical analysis: dominance {dominance_ratio:.3f}, frequency range {freq_range}",
                    transformation_steps=2,
                    evidence_snippets=[
                        f"Total Muqattaat occurrences: {total_muqattaat}",
                        f"Dominance ratio: {dominance_ratio:.4f}",
                        f"Frequency range: {freq_range}",
                        f"Max frequency: {max_freq}",
                        f"Min frequency: {min_freq}",
                        f"Individual frequencies: {muqattaat_freq}"
                    ],
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
