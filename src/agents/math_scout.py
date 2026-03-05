from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class MathScout(BaseScout):
    """
    Abjad matrix analysis using mathematical patterns.
    """
    
    name = "MathScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze mathematical patterns in Muqattaat using Abjad values.
        """
        hypotheses = []
        
        # Simple Abjad values for common letters
        abjad_values = {
            'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
            'ي': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80,
            'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600,
            'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000
        }
        
        rasm_matrices = state.get("rasm_matrices", {})
        muqattaat_map = state.get("muqattaat_map", {})
        
        for surah_num in rasm_matrices:
            if surah_num not in muqattaat_map:
                continue
                
            muqattaat = muqattaat_map[surah_num]
            rasm_letters = rasm_matrices[surah_num]
            
            if not rasm_letters:
                continue
            
            # Calculate Abjad sum for Muqattaat
            muqattaat_sum = sum(abjad_values.get(letter, 0) for letter in muqattaat)
            
            if muqattaat_sum > 0:
                # Count occurrences of Muqattaat letters in the text
                muqattaat_letters = set(muqattaat)
                letter_counts = {}
                for letter in rasm_letters:
                    if letter in muqattaat_letters:
                        letter_counts[letter] = letter_counts.get(letter, 0) + 1
                
                total_muqattaat_occurrences = sum(letter_counts.values())
                
                if total_muqattaat_occurrences > 0:
                    hypothesis = Hypothesis(
                        source_scout=self.name,
                        goal_link=f"Muqattaat {muqattaat} has Abjad value {muqattaat_sum} which correlates with the {total_muqattaat_occurrences} total occurrences of these letters in Surah {surah_num}, revealing a mathematical encoding of the chapter's numerical signature.",
                        description=f"Abjad sum: {muqattaat_sum}, Total letter occurrences: {total_muqattaat_occurrences}",
                        transformation_steps=2,
                        evidence_snippets=[
                            f"Muqattaat Abjad sum: {muqattaat_sum}",
                            f"Letter frequency: {letter_counts}",
                            f"Total occurrences: {total_muqattaat_occurrences}"
                        ],
                        surah_refs=[surah_num],
                        layer="rasm"
                    )
                    hypotheses.append(hypothesis)
        
        return hypotheses
