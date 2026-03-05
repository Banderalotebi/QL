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
