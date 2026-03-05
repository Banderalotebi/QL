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
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis

class StaticScout(BaseScout):
    """
    Static pattern analysis scout.
    Analyzes fixed patterns and structures in the text.
    """
    
    name = "StaticScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze static patterns in the text.
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
            
            # Simple static analysis: count total letters
            total_letters = len(rasm_letters)
            muqattaat_length = len(muqattaat)
            
            if total_letters > 0:
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat sequence {muqattaat} with {muqattaat_length} letters prefixes Surah {surah_num} containing {total_letters} total letters, suggesting a structural relationship between the opening sequence length and chapter content volume.",
                    description=f"Surah {surah_num}: {muqattaat_length} Muqattaat letters, {total_letters} total letters",
                    transformation_steps=1,
                    evidence_snippets=[f"Muqattaat: {muqattaat}", f"Total letters: {total_letters}"],
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
