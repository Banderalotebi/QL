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
        
        # Import centralized Abjad values
        from src.utils.abjad import ABJAD as abjad_values
        
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
