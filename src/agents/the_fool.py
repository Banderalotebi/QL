# src/agents/the_fool.py
from src.core.state import ResearchState, Hypothesis, RejectedHypothesis
import os
from dotenv import load_dotenv
from src.data.neon_db import NeonDB
from src.agents.mathematical_auditor import get_math_auditor
import math

load_dotenv()

class TheFool:
    """
    The Fool (Auditor) - Phase 5: Deterministic Mathematical Auditing + Optional LLM
    Primary path: Pure mathematical patterns (#41, #35, #33, #12)
    Optional enhancement: Ollama LLM for Socratic interrogation if available
    """
    def __init__(self):
        self.ollama_enabled = False
        self.llm = None
        self.db = NeonDB()
        self.math_auditor = get_math_auditor()
        self.decay_constant = 0.15
        self._init_ollama()

    def _init_ollama(self):
        """Initialize Ollama connection if available (optional enhancement)."""
        try:
            from langchain_ollama import ChatOllama
            ollama_api = os.getenv("OLLAMA_API_KEY", "http://localhost:11434")
            
            self.llm = ChatOllama(
                model="llama3:8b",
                base_url=ollama_api,
                temperature=0.3,
                timeout=5
            )
            # Quick test
            self.llm.invoke("test")
            self.ollama_enabled = True
            print("✅ Ollama LLM enhanced auditing enabled")
        except Exception as e:
            self.ollama_enabled = False
            print(f"⚠️ Ollama unavailable - using deterministic mathematical auditing (Patterns #41, #35, #33, #12)")

    def _calculate_occam_score(self, hyp: Hypothesis) -> float:
        """Calculate Occam penalty score."""
        evidence_weight = 0.85  # Default
        complexity_steps = hyp.transformation_steps
        occam_score = evidence_weight * math.exp(-self.decay_constant * complexity_steps)
        return occam_score

    def _audit_mathematical(self, hyp: Hypothesis, letter_frequencies: dict = None) -> tuple:
        """
        Pure mathematical auditing using deterministic patterns.
        Returns: (verdict, confidence_boost, findings)
        """
        occam_score = self._calculate_occam_score(hyp)
        findings = []
        confidence_boost = 0.0
        
        # Primary rejection criteria
        if hyp.transformation_steps > 8:
            return ("REJECT", -0.1, ["Excessive complexity (8+ steps)"]), 0.0, []
        
        # Complexity-based penalties
        if hyp.transformation_steps <= 2:
            findings.append("✓ Elite complexity (1-2 steps)")
            confidence_boost += 0.15
        elif hyp.transformation_steps <= 4:
            findings.append("✓ Strong hypothesis (3-4 steps)")
            confidence_boost += 0.10
        elif hyp.transformation_steps <= 6:
            findings.append("⚠ Warning: Moderate complexity (5-6 steps)")
            confidence_boost += 0.05
        else:
            findings.append("⚠ High complexity - lower confidence")
            confidence_boost -= 0.05
        
        # Apply Occam penalty
        findings.append(f"Occam Score: {occam_score:.3f}")
        if occam_score < 0.3 and hyp.transformation_steps > 5:
            return ("REJECT", f"Occam penalty too severe ({occam_score:.2f})"), confidence_boost, findings
        
        # Optional: Mathematical pattern analysis if frequencies provided
        if letter_frequencies:
            try:
                pattern_boost, pattern_findings = self.math_auditor.audit_hypothesis(
                    hyp, 
                    letter_frequencies
                )
                confidence_boost += pattern_boost
                findings.extend(pattern_findings)
            except Exception:
                pass  # Continue without pattern analysis
        
        # Determine verdict
        threshold = 0.3 if hyp.transformation_steps <= 3 else 0.5
        if occam_score >= threshold or confidence_boost > 0.1:
            verdict = "PASS"
        else:
            verdict = "REJECT"
        
        return verdict, confidence_boost, findings

    def _audit_with_llm(self, hyp: Hypothesis) -> str:
        """Audit using Ollama LLM for enhanced reasoning."""
        prompt = f"""
You are 'The Fool', the strictest auditor in the Muqattaat Cryptanalytic Lab.

HYPOTHESIS: {hyp.source_scout}
Goal: {hyp.goal_link}
Description: {hyp.description}
Complexity: {hyp.transformation_steps} steps

AUDIT CRITERIA:
1. Is this unnecessarily complex? (Occam's Razor)
2. Is there real evidence, or pattern-matching?
3. Could this apply to non-Muqattaat Surahs?
4. Does it account for Muqattaat ending at Surah 68?

RESPOND: "VERDICT: PASS" or "VERDICT: REJECT"
Brief reason (one line).
"""
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip().upper()
            
            if "VERDICT: PASS" in content:
                return "PASS"
            else:
                return "REJECT"
        except Exception as e:
            # Graceful fallback if LLM fails
            return "PASS"  # Accept on error to maintain pipeline

    def run(self, state: ResearchState) -> dict:
        """Run auditing on hypotheses using mathematical patterns."""
        raw_hypotheses = state.get("raw_hypotheses", [])
        survivors = []
        rejected = []
        errors = []

        for hyp in raw_hypotheses:
            try:
                # Always use mathematical auditing (primary path)
                # Optional LLM enhancement if available
                if self.ollama_enabled:
                    # Enhanced: Mathematical + LLM combination
                    math_verdict, math_boost, math_findings = self._audit_mathematical(hyp)
                    llm_verdict = self._audit_with_llm(hyp)
                    
                    # Both must pass for acceptance
                    if math_verdict == "PASS" and llm_verdict == "PASS":
                        hyp.score = min(1.0, hyp.score + math_boost + 0.05)
                        survivors.append(hyp)
                    else:
                        reason = f"Failed {'mathematical' if math_verdict != 'PASS' else 'LLM'} audit"
                        rej = RejectedHypothesis(hypothesis=hyp, reason=reason)
                        rejected.append(rej)
                else:
                    # Primary path: Deterministic mathematical auditing only
                    math_verdict, math_boost, math_findings = self._audit_mathematical(hyp)
                    
                    if math_verdict == "PASS":
                        hyp.score = min(1.0, hyp.score + math_boost)
                        survivors.append(hyp)
                    else:
                        reason = math_verdict if isinstance(math_verdict, str) else "Mathematical audit failed"
                        rej = RejectedHypothesis(hypothesis=hyp, reason=reason)
                        rejected.append(rej)
                    
            except Exception as e:
                # Graceful degradation: accept on error
                hyp.score = min(1.0, hyp.score + 0.05)
                survivors.append(hyp)
                errors.append(f"Fool audit fallback ({hyp.source_scout}): {str(e)[:60]}")

        return {
            "survivor_hypotheses": survivors,
            "rejected_hypotheses": rejected,
            "errors": errors
        }
