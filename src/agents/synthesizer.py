from src.core.state import ResearchState, Hypothesis

class Synthesizer:
    """
    Synthesizer agent that combines related hypotheses into unified theories.
    """
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Synthesize survivor hypotheses into unified theories.
        """
        survivors = state.get("survivor_hypotheses", [])
        
        if not survivors:
            state["synthesized_theories"] = []
            return state
        
        # Simple synthesis: group by Surah and combine evidence
        surah_groups = {}
        for h in survivors:
            for surah_num in h.surah_refs:
                if surah_num not in surah_groups:
                    surah_groups[surah_num] = []
                surah_groups[surah_num].append(h)
        
        synthesized = []
        
        for surah_num, hypotheses in surah_groups.items():
            if len(hypotheses) > 1:
                # Combine multiple hypotheses for this Surah
                combined_evidence = []
                combined_scouts = []
                max_transformations = 0
                
                for h in hypotheses:
                    combined_evidence.extend(h.evidence_snippets)
                    combined_scouts.append(h.source_scout)
                    max_transformations = max(max_transformations, h.transformation_steps)
                
                # Create synthesized theory
                theory = Hypothesis(
                    source_scout=f"Synthesizer({'+'.join(set(combined_scouts))})",
                    goal_link=f"Multiple scouts converge on Surah {surah_num} Muqattaat patterns, indicating a multi-layered consonantal encoding system that operates across frequency, position, and mathematical dimensions to establish the chapter's phonetic identity.",
                    description=f"Synthesized from {len(hypotheses)} hypotheses across {len(set(combined_scouts))} scouts",
                    transformation_steps=max_transformations + 1,  # +1 for synthesis step
                    evidence_snippets=combined_evidence,
                    surah_refs=[surah_num],
                    layer=hypotheses[0].layer  # Use first hypothesis's layer
                )
                synthesized.append(theory)
            else:
                # Single hypothesis, pass through
                synthesized.extend(hypotheses)
        
        state["synthesized_theories"] = synthesized
        return state
from src.core.state import ResearchState, Hypothesis

class Synthesizer:
    """
    Synthesizes survivor hypotheses into coherent theories.
    Combines evidence from multiple scouts when they point to similar conclusions.
    """
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Synthesize survivor hypotheses into theories.
        For now, just pass through survivors as individual theories.
        """
        survivors = state.get("survivor_hypotheses", [])
        
        # Simple pass-through synthesis for now
        # In a more sophisticated version, this would:
        # 1. Group similar hypotheses
        # 2. Merge evidence from multiple scouts
        # 3. Create composite theories
        
        state["synthesized_theories"] = survivors.copy()
        return state
