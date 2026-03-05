from src.core.state import ResearchState, Hypothesis, RejectedHypothesis

class TheFool:
    """
    The Fool - Quality control agent that interrogates hypotheses for logical rigor.
    Rejects hypotheses with generic goal_link, circular reasoning, or insufficient evidence.
    """
    
    def run(self, state: ResearchState) -> ResearchState:
        """
        Interrogate all raw hypotheses and separate survivors from rejects.
        """
        raw_hypotheses = state.get("raw_hypotheses", [])
        survivors = []
        rejected = []
        
        for h in raw_hypotheses:
            verdict, reason, details = self._interrogate(h)
            
            if verdict == "PASS":
                survivors.append(h)
            else:
                rejected.append(RejectedHypothesis(
                    hypothesis=h,
                    reason=reason,
                    auditor="TheFool"
                ))
        
        state["survivor_hypotheses"] = survivors
        state["rejected_hypotheses"] = rejected
        
        return state
    
    def _interrogate(self, h: Hypothesis) -> tuple[str, str, str]:
        """
        Interrogate a single hypothesis.
        
        Returns:
            Tuple of (verdict, reason, details) where verdict is "PASS" or "REJECT"
        """
        
        # Test 1: Generic goal_link detection
        generic_phrases = [
            "this is interesting",
            "may be relevant",
            "could be significant",
            "worth investigating",
            "appears to be",
            "seems to",
            "might indicate",
            "could suggest",
            "potentially",
            "possibly"
        ]
        
        goal_lower = h.goal_link.lower()
        if any(phrase in goal_lower for phrase in generic_phrases):
            return (
                "REJECT",
                "Generic goal_link detected",
                f"Goal link contains generic language: '{h.goal_link}'"
            )
        
        # Test 2: Empty or too short goal_link
        if len(h.goal_link.strip()) < 20:
            return (
                "REJECT",
                "Goal link too short or empty",
                f"Goal link must be at least 20 characters, got {len(h.goal_link.strip())}"
            )
        
        # Test 3: Circular reasoning detection
        if h.description.strip() == h.goal_link.strip():
            return (
                "REJECT",
                "Circular reasoning detected",
                "Description and goal_link are identical — circular logic detected."
            )
        
        # Test 4: Must mention Muqattaat specifically
        muqattaat_keywords = [
            "muqattaat", "isolated letter", "disjointed letter", "الحروف المقطعة",
            "alif lam mim", "alm", "alr", "alms", "ha mim", "ya sin", "ta ha",
            "phonetic key", "consonantal", "letter sequence", "opening letter"
        ]
        
        if not any(kw in goal_lower for kw in muqattaat_keywords):
            return (
                "REJECT",
                "Goal link does not mention Muqattaat",
                "Every hypothesis must explicitly connect to the Muqattaat mystery"
            )
        
        # Test 5: Evidence sufficiency
        if len(h.evidence_snippets) < 1:
            return (
                "REJECT",
                "Insufficient evidence",
                "At least one evidence snippet required"
            )
        
        # Test 6: Surah reference validation
        if not h.surah_refs:
            return (
                "REJECT",
                "No Surah references",
                "Must reference at least one Surah"
            )
        
        # Test 7: Layer purity check
        if h.layer not in ("rasm", "tashkeel"):
            return (
                "REJECT",
                "Invalid layer specification",
                f"Layer must be 'rasm' or 'tashkeel', got '{h.layer}'"
            )
        
        return ("PASS", "Hypothesis accepted", "All tests passed")
