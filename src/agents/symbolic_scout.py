from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class SymbolicScout(BaseScout):
    """
    Symbolic and geometric pattern analysis of Muqattaat sequences.
    """
    
    name = "SymbolicScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze symbolic patterns and geometric relationships in Muqattaat.
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
            
            # Analyze sequence length and letter uniqueness
            muqattaat_length = len(muqattaat)
            unique_letters = len(set(muqattaat))
            
            # Look for geometric patterns in letter positions
            muqattaat_letters = set(muqattaat)
            positions = []
            for i, letter in enumerate(rasm_letters[:1000]):  # Sample first 1000 letters
                if letter in muqattaat_letters:
                    positions.append(i)
            
            if len(positions) >= 3:
                # Calculate intervals between positions
                intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
                
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat {muqattaat} forms a {muqattaat_length}-letter symbolic sequence with {unique_letters} unique elements, creating geometric intervals averaging {avg_interval:.1f} positions in Surah {surah_num}, suggesting a spatial encoding of divine mathematical harmony.",
                    description=f"Symbolic analysis: {muqattaat_length} letters, {unique_letters} unique, avg interval {avg_interval:.1f}",
                    transformation_steps=3,
                    evidence_snippets=[
                        f"Sequence length: {muqattaat_length}",
                        f"Unique letters: {unique_letters}",
                        f"Position samples: {positions[:10]}",
                        f"Average interval: {avg_interval:.2f}",
                        f"Total positions found: {len(positions)}"
                    ],
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis

class SymbolicScout(BaseScout):
    """
    Symbolic pattern analysis scout.
    Analyzes symbolic and structural relationships.
    """
    
    name = "SymbolicScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze symbolic patterns in the text.
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
            
            # Simple symbolic analysis: position-based patterns
            first_letters = rasm_letters[:len(muqattaat)] if len(rasm_letters) >= len(muqattaat) else rasm_letters
            
            # Check if Muqattaat letters appear in similar positions
            position_matches = sum(1 for i, letter in enumerate(first_letters) if i < len(muqattaat) and letter in muqattaat)
            
            if position_matches > 0:
                match_ratio = position_matches / len(muqattaat)
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat sequence {muqattaat} shows positional correspondence with the opening letters of Surah {surah_num}, with {match_ratio:.1%} positional matches suggesting these isolated letters encode the structural blueprint of the chapter's letter sequence.",
                    description=f"Positional matches: {position_matches}/{len(muqattaat)} ({match_ratio:.1%})",
                    transformation_steps=2,
                    evidence_snippets=[f"Position matches: {position_matches}", f"Match ratio: {match_ratio:.3f}"],
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
