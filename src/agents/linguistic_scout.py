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
