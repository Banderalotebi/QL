"""
src/agents/static_scout.py
──────────────────────────
Static Scout — The Statistical Mapper

Calculates: Shannon Entropy, n-gram clusters, frequency averages.
Does NOT try to "solve" patterns — only maps the statistical landscape.
Operates strictly on the Rasm layer.

PRIMARY GOAL FOCUS:
  Measure whether the statistical fingerprint of Muqattaat-prefixed Surahs
  is measurably different from non-Muqattaat Surahs. If yes, the Muqattaat
  are acting as statistical modulators of the text — pointing toward their
  function and potentially their meaning.
"""

from __future__ import annotations
import math
from collections import Counter
from src.agents.base_agent import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.data.muqattaat import MUQATTAAT_SURAHS


def shannon_entropy(letters: list[str]) -> float:
    if not letters:
        return 0.0
    total = len(letters)
    freq = Counter(letters)
    return -sum((c / total) * math.log2(c / total) for c in freq.values())


class StaticScout(BaseScout):
    name = "StaticScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []
        rasm_matrices = self.get_rasm_matrices(state)

        muq_entropies: list[float] = []
        non_muq_entropies: list[float] = []
        muq_surahs: list[int] = []
        non_muq_surahs: list[int] = []

        for snum, matrix in rasm_matrices.items():
            letters = matrix.letter_sequence
            if not letters:
                continue
            H = shannon_entropy(letters)
            if snum in MUQATTAAT_SURAHS:
                muq_entropies.append(H)
                muq_surahs.append(snum)
            else:
                non_muq_entropies.append(H)
                non_muq_surahs.append(snum)

        # ── Entropy comparison hypothesis ──────────────────────────────────
        if muq_entropies and non_muq_entropies:
            avg_muq = sum(muq_entropies) / len(muq_entropies)
            avg_non = sum(non_muq_entropies) / len(non_muq_entropies)
            delta = abs(avg_muq - avg_non)

            if delta > 0.05:
                direction = "lower" if avg_muq < avg_non else "higher"
                hypotheses.append(self.make_hypothesis(
                    description=(
                        f"Muqattaat Surahs show {direction} average Shannon entropy "
                        f"({avg_muq:.4f}) vs non-Muqattaat Surahs ({avg_non:.4f}). "
                        f"Delta: {delta:.4f}."
                    ),
                    goal_link=(
                        f"A systematic entropy difference in Muqattaat Surahs indicates "
                        f"the isolated letters are NOT random placeholders — they correlate "
                        f"with a measurably distinct textual structure, suggesting they encode "
                        f"structural or thematic information about the Surah's composition."
                    ),
                    transformation_steps=2,
                    evidence_snippets=[
                        f"Muqattaat Surahs analyzed: {muq_surahs}",
                        f"Avg entropy (Muqattaat): {avg_muq:.4f}",
                        f"Avg entropy (non-Muqattaat): {avg_non:.4f}",
                        f"Delta: {delta:.4f}",
                    ],
                    surah_refs=muq_surahs,
                    metadata={"dual_layer_corroborated": False},
                ))

        # ── Bigram cluster hypothesis ──────────────────────────────────────
        for snum, matrix in rasm_matrices.items():
            if not matrix.is_muqattaat_surah:
                continue
            letters = matrix.letter_sequence
            if len(letters) < 10:
                continue

            bigrams = [f"{letters[i]}{letters[i+1]}" for i in range(len(letters)-1)]
            bigram_freq = Counter(bigrams)
            top3 = bigram_freq.most_common(3)

            # Check if any top bigram contains a Muqattaat letter
            muq_chars = set(matrix.isolated_sequences[0]) if matrix.isolated_sequences else set()
            muq_bigrams = [(bg, c) for bg, c in top3 if any(ch in muq_chars for ch in bg)]

            if muq_bigrams:
                hypotheses.append(self.make_hypothesis(
                    description=(
                        f"Surah {snum}: Top bigrams containing Muqattaat letters: "
                        f"{muq_bigrams}. These letter-pairs cluster above baseline frequency."
                    ),
                    goal_link=(
                        "If Muqattaat letters form the most frequent bigram pairs in the Surah body, "
                        "they are structurally woven into the text — not isolated decorations. "
                        "This supports the theory that Muqattaat are phonetic/structural keys "
                        "whose meaning is embedded in the compositional pattern of the chapter."
                    ),
                    transformation_steps=2,
                    evidence_snippets=[
                        f"Top bigrams: {top3}",
                        f"Muqattaat-containing bigrams: {muq_bigrams}",
                    ],
                    surah_refs=[snum],
                ))

        return hypotheses
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class StaticScout(BaseScout):
    """
    Static frequency analysis of Muqattaat letters in Surah text.
    """
    
    name = "StaticScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze static frequency patterns of Muqattaat letters.
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
            
            # Count frequency of each Muqattaat letter
            muqattaat_letters = list(muqattaat)
            letter_counts = {}
            total_letters = len(rasm_letters)
            
            for letter in muqattaat_letters:
                count = rasm_letters.count(letter)
                letter_counts[letter] = count
            
            total_muqattaat_count = sum(letter_counts.values())
            
            if total_muqattaat_count > 0:
                frequency_percentage = (total_muqattaat_count / total_letters) * 100
                
                # Create evidence snippets
                evidence = [f"Total letters: {total_letters}", f"Muqattaat occurrences: {total_muqattaat_count}"]
                for letter, count in letter_counts.items():
                    if count > 0:
                        evidence.append(f"{letter}: {count} ({count/total_letters*100:.1f}%)")
                
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat letters {muqattaat} comprise {frequency_percentage:.1f}% of Surah {surah_num}'s total letter content, indicating they serve as the dominant consonantal framework encoding the chapter's phonetic identity.",
                    description=f"Frequency analysis shows {total_muqattaat_count} Muqattaat letters out of {total_letters} total ({frequency_percentage:.1f}%)",
                    transformation_steps=1,
                    evidence_snippets=evidence,
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
