from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class DeepScout(BaseScout):
    """
    Deep pattern analysis combining multiple layers and cross-references.
    """
    
    name = "DeepScout"
    consumes_rasm = True
    consumes_tashkeel = True
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Perform deep cross-layer analysis of Muqattaat patterns.
        """
        hypotheses = []
        
        rasm_matrices = state.get("rasm_matrices", {})
        tashkeel_matrices = state.get("tashkeel_matrices", {})
        muqattaat_map = state.get("muqattaat_map", {})
        
        # Cross-reference analysis across multiple Surahs
        muqattaat_surahs = list(muqattaat_map.keys())
        
        if len(muqattaat_surahs) >= 2:
            # Compare patterns across Surahs
            pattern_similarities = {}
            
            for i, surah1 in enumerate(muqattaat_surahs):
                for surah2 in muqattaat_surahs[i+1:]:
                    muq1 = muqattaat_map[surah1]
                    muq2 = muqattaat_map[surah2]
                    
                    # Find common letters
                    common_letters = set(muq1) & set(muq2)
                    if common_letters:
                        similarity_key = f"{surah1}-{surah2}"
                        pattern_similarities[similarity_key] = {
                            'common': common_letters,
                            'muq1': muq1,
                            'muq2': muq2
                        }
            
            if pattern_similarities:
                # Create hypothesis about cross-Surah patterns
                total_comparisons = len(pattern_similarities)
                common_patterns = sum(1 for p in pattern_similarities.values() if len(p['common']) > 0)
                
                evidence = []
                surah_refs = []
                for key, data in list(pattern_similarities.items())[:3]:  # Limit to first 3
                    evidence.append(f"{key}: common letters {data['common']}")
                    surah_nums = [int(x) for x in key.split('-')]
                    surah_refs.extend(surah_nums)
                
                surah_refs = list(set(surah_refs))  # Remove duplicates
                
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Cross-Surah analysis reveals {common_patterns}/{total_comparisons} Muqattaat pairs share common letters, indicating a systematic phonetic architecture where specific consonants serve as universal keys across multiple chapters of the Quran.",
                    description=f"Deep pattern analysis found {common_patterns} common patterns across {total_comparisons} Surah pairs",
                    transformation_steps=4,
                    evidence_snippets=evidence + [f"Pattern ratio: {common_patterns}/{total_comparisons}"],
                    surah_refs=surah_refs,
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis

class DeepScout(BaseScout):
    """
    Deep pattern analysis scout.
    Performs complex multi-layer analysis.
    """
    
    name = "DeepScout"
    consumes_rasm = True
    consumes_tashkeel = True
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Perform deep analysis combining multiple layers.
        """
        hypotheses = []
        
        rasm_matrices = state.get("rasm_matrices", {})
        tashkeel_matrices = state.get("tashkeel_matrices", {})
        muqattaat_map = state.get("muqattaat_map", {})
        
        for surah_num in rasm_matrices:
            if surah_num not in muqattaat_map:
                continue
                
            muqattaat = muqattaat_map[surah_num]
            rasm_letters = rasm_matrices[surah_num]
            
            if not rasm_letters:
                continue
            
            # Deep analysis: multi-dimensional pattern detection
            # This is a placeholder for more sophisticated analysis
            
            # Calculate complexity metrics
            unique_letters = len(set(rasm_letters))
            total_letters = len(rasm_letters)
            complexity_ratio = unique_letters / total_letters if total_letters > 0 else 0
            
            muqattaat_complexity = len(set(muqattaat)) / len(muqattaat) if muqattaat else 0
            
            if abs(complexity_ratio - muqattaat_complexity) < 0.1:  # Similar complexity
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat sequence {muqattaat} exhibits complexity ratio {muqattaat_complexity:.3f} that closely matches the overall letter complexity {complexity_ratio:.3f} of Surah {surah_num}, indicating these isolated letters encode a compressed representation of the chapter's linguistic complexity signature.",
                    description=f"Complexity correlation: Muqattaat {muqattaat_complexity:.3f} vs Chapter {complexity_ratio:.3f}",
                    transformation_steps=3,
                    evidence_snippets=[f"Muqattaat complexity: {muqattaat_complexity:.3f}", f"Chapter complexity: {complexity_ratio:.3f}"],
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
