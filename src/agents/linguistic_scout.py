"""
src/agents/linguistic_scout.py
────────────────────────────────
Linguistic Scout — Word DNA analyzer

Consumes ONLY Tashkeel layer.
Analyzes morphology, 3-letter root derivation, syllable structures,
and rhythmic patterns independent of semantic meaning.

PRIMARY GOAL FOCUS:
  Are the Muqattaat letters phonetically significant — do they represent
  the dominant consonantal roots of the Surah's vocabulary?
  If a Surah's key root letters match its Muqattaat, the letters may be
  a phonetic summary or signature of the chapter's linguistic identity.
"""

from __future__ import annotations
from collections import Counter
from src.agents.base_agent import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.data.muqattaat import BY_SURAH, MUQATTAAT_SURAHS


class LinguisticScout(BaseScout):
    name = "LinguisticScout"
    consumes_rasm = False
    consumes_tashkeel = True

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []
        tashkeel_matrices = self.get_tashkeel_matrices(state)

        for snum, matrix in tashkeel_matrices.items():
            if snum not in MUQATTAAT_SURAHS:
                continue

            entry = BY_SURAH[snum]
            rhythm = matrix.phonetic_rhythm

            if not rhythm:
                continue

            # ── Rhythm pattern analysis ────────────────────────────────────
            # Count CV vs CC clusters
            cv_count = rhythm.count("V")
            cc_count = rhythm.count("C") - cv_count
            ratio = cv_count / len(rhythm) if rhythm else 0

            # Muqattaat letters are all consonants — do they shape a CC-heavy opening?
            opening_rhythm = rhythm[:20] if len(rhythm) > 20 else rhythm
            opening_cc = opening_rhythm.count("C")
            opening_cv = opening_rhythm.count("V")

            if opening_cc > opening_cv * 1.5:
                hypotheses.append(self.make_hypothesis(
                    description=(
                        f"Surah {snum}: Opening rhythm is consonant-heavy "
                        f"(CC:{opening_cc} vs CV:{opening_cv}), "
                        f"consistent with the consonantal-only Muqattaat opening pattern."
                    ),
                    goal_link=(
                        "The Muqattaat are read as isolated consonant names (e.g. Alif, Lam, Mim). "
                        "A consonant-heavy opening rhythm in the Surah text reinforces the phonetic "
                        "theory: the Muqattaat letters define the consonantal skeleton (Rasm) that "
                        "gives the chapter its sonic identity — their 'meaning' is this phonetic signature."
                    ),
                    transformation_steps=2,
                    evidence_snippets=[
                        f"Opening rhythm: {opening_rhythm}",
                        f"CC count: {opening_cc}",
                        f"CV count: {opening_cv}",
                        f"Muqattaat: {entry.transliteration}",
                    ],
                    surah_refs=[snum],
                ))

            # ── Diacritic density hypothesis ───────────────────────────────
            diacritic_count = len(matrix.diacritic_map)
            syllable_count = len(matrix.syllable_structure)
            density = diacritic_count / syllable_count if syllable_count > 0 else 0

            hypotheses.append(self.make_hypothesis(
                description=(
                    f"Surah {snum}: Tashkeel density = {density:.3f} diacritics/syllable. "
                    f"Total diacritics: {diacritic_count}, syllables: {syllable_count}."
                ),
                goal_link=(
                    "Baseline phonetic density of Muqattaat Surahs — required for cross-Surah "
                    "comparison to determine if the presence of Muqattaat correlates with "
                    "measurably distinct phonetic complexity, revealing their structural role."
                ),
                transformation_steps=1,
                evidence_snippets=[
                    f"Diacritics: {diacritic_count}",
                    f"Syllables: {syllable_count}",
                    f"Density: {density:.4f}",
                ],
                surah_refs=[snum],
            ))

        return hypotheses
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class LinguisticScout(BaseScout):
    """
    Linguistic pattern analysis focusing on phonetic and morphological structures.
    """
    
    name = "LinguisticScout"
    consumes_rasm = False
    consumes_tashkeel = True
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze linguistic patterns in the tashkeel layer.
        """
        hypotheses = []
        
        tashkeel_matrices = state.get("tashkeel_matrices", {})
        muqattaat_map = state.get("muqattaat_map", {})
        
        for surah_num in tashkeel_matrices:
            if surah_num not in muqattaat_map:
                continue
                
            muqattaat = muqattaat_map[surah_num]
            tashkeel_data = tashkeel_matrices[surah_num]
            
            if not tashkeel_data:
                continue
            
            # Analyze phonetic rhythm patterns
            rhythm_pattern = tashkeel_data[0] if tashkeel_data else ""
            
            if rhythm_pattern:
                consonant_count = rhythm_pattern.count('C')
                vowel_count = rhythm_pattern.count('V')
                total_phonemes = consonant_count + vowel_count
                
                if total_phonemes > 0:
                    cv_ratio = consonant_count / total_phonemes
                    
                    hypothesis = Hypothesis(
                        source_scout=self.name,
                        goal_link=f"Muqattaat {muqattaat} establishes a consonant-vowel ratio of {cv_ratio:.2f} in Surah {surah_num}, revealing the phonetic template that governs the chapter's rhythmic recitation pattern.",
                        description=f"Phonetic analysis: {consonant_count}C/{vowel_count}V ratio = {cv_ratio:.2f}",
                        transformation_steps=2,
                        evidence_snippets=[
                            f"Consonants: {consonant_count}",
                            f"Vowels: {vowel_count}",
                            f"C/V ratio: {cv_ratio:.3f}",
                            f"Rhythm pattern sample: {rhythm_pattern[:50]}..."
                        ],
                        surah_refs=[surah_num],
                        layer="tashkeel"
                    )
                    hypotheses.append(hypothesis)
        
        return hypotheses
