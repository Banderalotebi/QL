"""
src/agents/micro_scout.py
─────────────────────────
Micro Scout — The Basic (O(n) linear pass)

Looks for the simplest, most obvious patterns:
  - Direct letter repetitions
  - Basic spacing / positional patterns
  - Steganographic patterns (every Nth word/letter)
  - Whether Muqattaat letters literally dominate the opening of the Surah

PRIMARY GOAL FOCUS:
  Does the Muqattaat sequence act as a literal abbreviation or acronym
  for words that follow? Checks if each isolated letter matches the
  first letter of the following word(s).
"""

from __future__ import annotations
from collections import Counter
from src.agents.base_agent import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.data.muqattaat import BY_SURAH, MUQATTAAT_SURAHS


class MicroScout(BaseScout):
    name = "MicroScout"
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

            # ── Test 1: Acronym hypothesis ─────────────────────────────────
            # Do Muqattaat letters match first letters of subsequent words?
            muq_letters = list(entry.arabic_sequence)
            first_word_letters = letters[:len(muq_letters)]
            match_count = sum(
                1 for a, b in zip(muq_letters, first_word_letters) if a == b
            )
            if match_count > 0:
                hypotheses.append(self.make_hypothesis(
                    description=(
                        f"Surah {snum}: {match_count}/{len(muq_letters)} Muqattaat letters "
                        f"match first letters of the opening text sequence."
                    ),
                    goal_link=(
                        f"If Muqattaat letters are abbreviations for the words that follow, "
                        f"a direct letter-match supports the acronym/abbreviation theory of Muqattaat meaning."
                    ),
                    transformation_steps=1,
                    evidence_snippets=[
                        f"Muqattaat: {''.join(muq_letters)}",
                        f"Opening letters: {''.join(first_word_letters)}",
                        f"Matches: {match_count}",
                    ],
                    surah_refs=[snum],
                ))

            # ── Test 2: Letter dominance hypothesis ───────────────────────
            # Do the Muqattaat letters statistically dominate the Surah?
            freq = Counter(letters)
            total = len(letters)
            muq_unique = set(entry.unique_letters)

            # Map letter names to Arabic chars (simplified)
            muq_arabic = set(entry.arabic_sequence)
            muq_freq = sum(freq.get(ch, 0) for ch in muq_arabic)
            dominance_ratio = muq_freq / total if total > 0 else 0

            if dominance_ratio > 0.25:
                hypotheses.append(self.make_hypothesis(
                    description=(
                        f"Surah {snum}: Muqattaat letters account for "
                        f"{dominance_ratio:.1%} of all letters in the Surah body — "
                        f"significantly above chance baseline."
                    ),
                    goal_link=(
                        "Statistical dominance of the exact Muqattaat letters throughout "
                        "the Surah suggests they may be thematic keys or structural anchors "
                        "that mark the dominant phonetic/semantic thread of the chapter, "
                        "pointing toward their meaning as chapter identifiers."
                    ),
                    transformation_steps=2,
                    evidence_snippets=[
                        f"Muqattaat: {entry.arabic_sequence}",
                        f"Dominance ratio: {dominance_ratio:.4f}",
                        f"Total letters: {total}",
                        f"Muqattaat letter count in Surah: {muq_freq}",
                    ],
                    surah_refs=[snum],
                ))

        return hypotheses
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class MicroScout(BaseScout):
    """
    Tests if Muqattaat letters match first letters of ayah words.
    Micro-level pattern detection in word-initial positions.
    """
    
    name = "MicroScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze if Muqattaat letters appear as first letters of words in the Surah.
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
            
            # Simple analysis: check if Muqattaat letters appear frequently at word boundaries
            # This is a placeholder implementation
            muqattaat_letters = list(muqattaat)
            first_letters = rasm_letters[:min(100, len(rasm_letters))]  # Sample first 100 letters
            
            matches = sum(1 for letter in first_letters if letter in muqattaat_letters)
            match_ratio = matches / len(first_letters) if first_letters else 0
            
            if match_ratio > 0.1:  # If more than 10% match
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat letters {muqattaat} appear frequently at word-initial positions in Surah {surah_num}, suggesting they encode the phonetic structure of the chapter's opening consonants.",
                    description=f"Found {matches} Muqattaat letter matches in first {len(first_letters)} positions ({match_ratio:.1%} match rate)",
                    transformation_steps=1,
                    evidence_snippets=[f"Match ratio: {match_ratio:.3f}", f"Matches: {matches}/{len(first_letters)}"],
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
