"""
Mathematical Audit Engine - Pattern #41, #35, #33
Deterministic cryptanalytic verification without LLM dependency.
Implements pure-logic analysis of Muqattaat sequences.
"""
import numpy as np
import collections
import math
from typing import Dict, List, Tuple
from src.core.state import Hypothesis


class MathematicalAuditor:
    """
    Rigorous verification using deterministic mathematical patterns.
    No external API calls - pure computational logic.
    """
    
    def __init__(self):
        """Initialize with mathematical constants."""
        self.phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        self.phi_inverse = 1 / self.phi
        
    def calculate_shannon_entropy(self, sequence: str) -> float:
        """
        Pattern #35: Calculate Information Density using Shannon Entropy.
        Higher entropy = higher randomness = lower confidence.
        Lower entropy = more structure = higher confidence.
        """
        if not sequence:
            return 0.0
        
        char_counts = collections.Counter(sequence)
        size = len(sequence)
        entropy = 0.0
        
        for count in char_counts.values():
            p = count / size
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy
    
    def calculate_entropy(self, sequence: str) -> float:
        """Alias for calculate_shannon_entropy for API consistency"""
        return self.calculate_shannon_entropy(sequence)
    
    def audit_modulo_19(self, frequencies: Dict[str, int]) -> Dict:
        """
        Pattern #41: Modulo-19 Verification.
        Checks if frequency totals follow mathematical constraints.
        19 is significant in Islamic numerology (mentions of الرحمن = 57 = 19×3).
        """
        total = sum(frequencies.values())
        remainder = total % 19
        verified = (remainder == 0)
        
        return {
            "total": total,
            "remainder": remainder,
            "verified": verified,
            "divisible_by_19": verified,
            "confidence": 0.9 if verified else 0.3
        }
    
    def calculate_golden_ratio_offset(self, frequencies: Dict[str, int]) -> Dict:
        """
        Pattern #33: Golden Ratio Harmonic Analysis.
        Checks if letter proportions align with φ (golden ratio).
        """
        total = sum(frequencies.values())
        if total == 0:
            return {"phi_offset": float('inf'), "alignment": 0.0}
        
        proportions = {k: v/total for k, v in frequencies.items()}
        
        # For each proportion, find distance to nearest φ-based fraction
        phi_fractions = [
            1/self.phi**2,      # ≈ 0.382
            self.phi_inverse,   # ≈ 0.618
            1/self.phi,         # ≈ 0.618
            self.phi - 1        # ≈ 0.618
        ]
        
        min_offset = min(abs(p - phi) for p in proportions.values() for phi in phi_fractions)
        alignment_score = 1.0 - min(min_offset, 1.0)
        
        return {
            "phi_offset": min_offset,
            "alignment_score": alignment_score,
            "confidence": 0.85 if alignment_score > 0.7 else 0.4
        }
    
    def analyze_abjad_numerology(self, sequence: str) -> Dict:
        """
        Pattern #12: Abjad Numerological Sum.
        Checks numerical significance of letter combinations.
        """
        abjad_table = {
            'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
            'ي': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80,
            'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600,
            'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000
        }
        
        total = sum(abjad_table.get(char, 0) for char in sequence)
        
        # Check for numerologically significant values
        is_multiple_of_19 = (total % 19 == 0)
        is_multiple_of_7 = (total % 7 == 0)
        
        return {
            "abjad_sum": total,
            "is_multiple_of_19": is_multiple_of_19,
            "is_multiple_of_7": is_multiple_of_7,
            "confidence": 0.75 if (is_multiple_of_19 or is_multiple_of_7) else 0.4
        }
    
    def audit_hypothesis(self, hypothesis: Hypothesis, letter_counts: Dict[str, int]) -> Tuple[float, List[str]]:
        """
        Run complete mathematical audit on a hypothesis.
        Returns: (confidence_boost, audit_findings)
        """
        findings = []
        total_confidence = 0.0
        
        # Pattern #41: Modulo-19
        modulo_result = self.audit_modulo_19(letter_counts)
        if modulo_result["verified"]:
            findings.append(f"✓ Modulo-19 Pattern Verified (Pattern #41)")
            total_confidence += 0.25
        else:
            findings.append(f"⊘ Modulo-19 Remainder: {modulo_result['remainder']}")
        
        # Pattern #35: Shannon Entropy
        sequence = "".join([char * count for char, count in letter_counts.items()])
        entropy = self.calculate_shannon_entropy(sequence)
        findings.append(f"📊 Shannon Entropy: {entropy:.3f} bits")
        # Lower entropy tends to indicate structure
        if entropy < 3.0:
            findings.append("✓ Low Entropy Indicates Structured Pattern")
            total_confidence += 0.15
        
        # Pattern #33: Golden Ratio
        phi_result = self.calculate_golden_ratio_offset(letter_counts)
        findings.append(f"φ Alignment: {phi_result['alignment_score']:.3f}")
        if phi_result['alignment_score'] > 0.6:
            findings.append("✓ Golden Ratio Harmony Detected")
            total_confidence += 0.20
        
        # Pattern #12: Abjad Numerology
        sequence_str = hypothesis.goal_link[:10] if hypothesis.goal_link else ""
        if sequence_str:
            abjad_result = self.analyze_abjad_numerology(sequence_str)
            if abjad_result["is_multiple_of_19"] or abjad_result["is_multiple_of_7"]:
                findings.append(f"✓ Abjad Sum: {abjad_result['abjad_sum']} (Numerologically Significant)")
                total_confidence += 0.15
        
        # Normalize confidence
        confidence_boost = min(total_confidence, 0.5)
        
        return confidence_boost, findings
    
    def pattern_41_verified(self, hypothesis: Hypothesis) -> bool:
        """Check if Pattern #41 (Modulo-19) applies to hypothesis"""
        frequencies = collections.Counter(hypothesis.goal_link)
        total = sum(frequencies.values())
        return total % 19 == 0
    
    def pattern_35_entropy_low(self, hypothesis: Hypothesis) -> bool:
        """Check if Pattern #35 (low entropy) applies to hypothesis"""
        entropy = self.calculate_entropy(hypothesis.goal_link)
        return entropy < 2.0
    
    def check_modulo_19(self, sequence: str) -> bool:
        """Check if sequence satisfies Modulo-19 constraint"""
        if not sequence:
            return False
        counts = collections.Counter(sequence)
        total = sum(counts.values())
        return total % 19 == 0
    
    def check_golden_ratio(self, evidence_snippets: List[str]) -> bool:
        """Check if golden ratio pattern appears in evidence"""
        if not evidence_snippets:
            return False
        
        text = "".join(evidence_snippets)
        if len(text) < 2:
            return False
        
        counts = collections.Counter(text)
        values = sorted(counts.values(), reverse=True)
        
        if len(values) >= 2 and values[1] > 0:
            ratio = values[0] / values[1]
            # Check if close to golden ratio (1.618)
            return abs(ratio - self.phi) < 0.2
        
        return False
    
    def check_abjad_significance(self, sequence: str) -> bool:
        """Check if Abjad sum is numerologically significant"""
        abjad_result = self.analyze_abjad_numerology(sequence)
        return abjad_result.get("is_multiple_of_19", False) or abjad_result.get("is_multiple_of_7", False)
    
    def calculate_abjad_sum(self, sequence: str) -> int:
        """Calculate Abjad numerological sum of a sequence"""
        abjad_result = self.analyze_abjad_numerology(sequence)
        return abjad_result.get("abjad_sum", 0)
    
    def generate_audit_report(self, hypotheses: List[Hypothesis], letter_frequencies: Dict[str, Dict[str, int]]) -> str:
        """
        Generate a comprehensive mathematical audit report.
        """
        report = []
        report.append("\n" + "="*80)
        report.append("🔬 MATHEMATICAL AUDIT REPORT (Deterministic Verification)")
        report.append("="*80)
        report.append(f"\nAnalyzing {len(hypotheses)} hypotheses using pure mathematical patterns...")
        report.append(f"Patterns: #41 (Modulo-19), #35 (Shannon Entropy), #33 (Golden Ratio), #12 (Abjad)")
        
        for i, hypothesis in enumerate(hypotheses[:5], 1):
            report.append(f"\n--- Hypothesis {i}: {hypothesis.source_scout} ---")
            report.append(f"Goal Link: {hypothesis.goal_link[:60]}...")
            
            # Get letter frequencies for this surah
            surah_key = str(hypothesis.surah_refs[0]) if hypothesis.surah_refs else "unknown"
            frequencies = letter_frequencies.get(surah_key, {})
            
            if frequencies:
                boost, findings = self.audit_hypothesis(hypothesis, frequencies)
                for finding in findings:
                    report.append(f"  {finding}")
                report.append(f"  Confidence Boost: +{boost:.2f}")
            else:
                report.append(f"  ⊘ No frequency data available")
        
        report.append("\n" + "="*80)
        report.append("✅ Audit Complete - All patterns analyzed deterministically")
        report.append("="*80 + "\n")
        
        return "\n".join(report)


# Singleton instance
_math_auditor = MathematicalAuditor()


def get_math_auditor() -> MathematicalAuditor:
    """Get the mathematical auditor instance."""
    return _math_auditor
