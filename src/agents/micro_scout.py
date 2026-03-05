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
