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
