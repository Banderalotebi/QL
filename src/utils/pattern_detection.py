"""
Linguistic Pattern Detection Utilities

Provides utilities for detecting and testing linguistic patterns in Arabic text,
particularly for Muqattaat (lettered Surahs) analysis.

This module integrates with the linguesticpstterntestcreator skill to enable
AI agents to discover and test patterns in Quranic text.
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Pattern Types
# ============================================================================

class PatternType(Enum):
    """Types of linguistic patterns to detect."""
    MUQATTAAT_PREFIX = "muqattaat_prefix"
    LETTER_SEQUENCE = "letter_sequence"
    REPETITION = "repetition"
    PALINDROME = "palindrome"
    NUMERICAL = "numerical"
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"


class PatternConfidence(Enum):
    """Confidence levels for pattern matches."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SPECULATIVE = "speculative"


# ============================================================================
# Pattern Models
# ============================================================================

@dataclass
class PatternMatch:
    """Represents a detected pattern match."""
    pattern_type: PatternType
    pattern_value: str
    position: Tuple[int, int]
    confidence: PatternConfidence
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_type": self.pattern_type.value,
            "pattern_value": self.pattern_value,
            "position": self.position,
            "confidence": self.confidence.value,
            "metadata": self.metadata
        }


@dataclass
class PatternTest:
    """Represents a test case for a linguistic pattern."""
    name: str
    pattern_type: PatternType
    test_input: str
    expected_output: Optional[str] = None
    is_positive: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "pattern_type": self.pattern_type.value,
            "test_input": self.test_input,
            "expected_output": self.expected_output,
            "is_positive": self.is_positive,
            "metadata": self.metadata
        }


# ============================================================================
# Core Pattern Detectors
# ============================================================================

class MuqattaatDetector:
    """Detects Muqattaat (lettered prefix) patterns in Quranic text."""
    
    # Known Muqattaat prefixes
    KNOWN_PREFIXES = {
        2: "الم",
        3: "المص",
        7: "الر",
        10: "الر",
        11: "الر",
        12: "الر",
        13: "المر",
        14: "الر",
        15: "الر",
        19: "كهيعص",
        20: "طه",
        26: "طسم",
        27: "طس",
        28: "طسم",
        29: "الم",
        30: "الم",
        31: "الم",
        32: "الم",
        36: "يس",
        38: "ص",
        40: "حم",
        41: "حم",
        42: "حم عسق",
        43: "حم",
        44: "حم",
        45: "حم",
        46: "حم",
        50: "ق",
        68: "ن"
    }
    
    @classmethod
    def detect_prefix(cls, text: str) -> List[PatternMatch]:
        """
        Detect Muqattaat prefix in text.
        
        Args:
            text: Arabic text to analyze
            
        Returns:
            List of pattern matches
        """
        matches = []
        
        for surah_id, prefix in cls.KNOWN_PREFIXES.items():
            if text.startswith(prefix):
                matches.append(PatternMatch(
                    pattern_type=PatternType.MUQATTAAT_PREFIX,
                    pattern_value=prefix,
                    position=(0, len(prefix)),
                    confidence=PatternConfidence.HIGH,
                    metadata={"surah_id": surah_id, "prefix_length": len(prefix)}
                ))
        
        return matches
    
    @classmethod
    def get_prefix_for_surah(cls, surah_id: int) -> Optional[str]:
        """Get the Muqattaat prefix for a specific Surah."""
        return cls.KNOWN_PREFIXES.get(surah_id)


class LetterSequenceDetector:
    """Detects letter sequence patterns."""
    
    ARABIC_LETTERS = list("ابتثجحخدذرزسشصضطظعغفقكلمنهويؤئةآأؤإ")
    
    @classmethod
    def find_sequences(cls, text: str, min_length: int = 2) -> List[PatternMatch]:
        """
        Find repeating letter sequences.
        
        Args:
            text: Text to analyze
            min_length: Minimum sequence length
            
        Returns:
            List of pattern matches
        """
        matches = []
        
        # Find all repeated sequences
        for length in range(min_length, min(10, len(text) // 2)):
            for i in range(len(text) - length):
                seq = text[i:i + length]
                
                # Check if this sequence repeats
                count = text.count(seq)
                if count > 1:
                    # Check if it's a meaningful pattern (not just random)
                    if cls._is_meaningful_sequence(seq):
                        matches.append(PatternMatch(
                            pattern_type=PatternType.LETTER_SEQUENCE,
                            pattern_value=seq,
                            position=(i, i + length),
                            confidence=PatternConfidence.MEDIUM,
                            metadata={"occurrences": count, "length": length}
                        ))
        
        return matches
    
    @classmethod
    def _is_meaningful_sequence(cls, sequence: str) -> bool:
        """Check if a sequence is meaningful (not just random letters)."""
        # A sequence is meaningful if it contains at least 2 unique letters
        unique_letters = set(sequence)
        return len(unique_letters) >= 2
    
    @classmethod
    def analyze_transitions(cls, text: str) -> Dict[str, int]:
        """
        Analyze letter transition patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of letter transitions and their counts
        """
        transitions = {}
        
        for i in range(len(text) - 1):
            pair = text[i:i + 2]
            transitions[pair] = transitions.get(pair, 0) + 1
        
        return transitions


class RepetitionDetector:
    """Detects repetition patterns in text."""
    
    @classmethod
    def find_repetitions(cls, text: str) -> List[PatternMatch]:
        """
        Find word/repetition patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of pattern matches
        """
        matches = []
        words = text.split()
        
        # Find consecutive repetitions
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                matches.append(PatternMatch(
                    pattern_type=PatternType.REPETITION,
                    pattern_value=words[i],
                    position=(i, i + 2),
                    confidence=PatternConfidence.HIGH,
                    metadata={"type": "consecutive", "count": 2}
                ))
        
        # Find non-consecutive repetitions
        word_counts = {}
        for i, word in enumerate(words):
            if word in word_counts:
                word_counts[word].append(i)
            else:
                word_counts[word] = [i]
        
        for word, positions in word_counts.items():
            if len(positions) > 1:
                matches.append(PatternMatch(
                    pattern_type=PatternType.REPETITION,
                    pattern_value=word,
                    position=(positions[0], positions[-1]),
                    confidence=PatternConfidence.MEDIUM,
                    metadata={"type": "non_consecutive", "count": len(positions)}
                ))
        
        return matches


class NumericalPatternDetector:
    """Detects numerical patterns in text."""
    
    @classmethod
    def count_letters(cls, text: str) -> Dict[str, int]:
        """Count occurrences of each letter."""
        counts = {}
        for char in text:
            if char.isalpha():
                counts[char] = counts.get(char, 0) + 1
        return counts
    
    @classmethod
    def calculate_abjad(cls, text: str) -> int:
        """
        Calculate Abjad numerical value of Arabic text.
        
        Args:
            text: Arabic text
            
        Returns:
            Abjad value
        """
        # Abjad letter values
        abjad_values = {
            'ا': 1, 'ب': 2, 'ت': 3, 'ث': 4, 'ج': 5, 'ح': 6, 'خ': 7, 'د': 8,
            'ذ': 9, 'ر': 10, 'ز': 11, 'س': 12, 'ش': 13, 'ص': 14, 'ض': 15,
            'ط': 16, 'ظ': 17, 'ع': 18, 'غ': 19, 'ف': 20, 'ق': 21, 'ك': 22,
            'ل': 23, 'م': 24, 'ن': 25, 'ه': 26, 'و': 27, 'ي': 28
        }
        
        total = 0
        for char in text:
            total += abjad_values.get(char, 0)
        
        return total
    
    @classmethod
    def find_numerical_patterns(cls, text: str) -> List[PatternMatch]:
        """
        Find numerical patterns in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of pattern matches
        """
        matches = []
        
        # Calculate abjad value
        abjad = cls.calculate_abjad(text)
        if abjad > 0:
            matches.append(PatternMatch(
                pattern_type=PatternType.NUMERICAL,
                pattern_value=str(abjad),
                position=(0, len(text)),
                confidence=PatternConfidence.HIGH,
                metadata={"type": "abjad", "value": abjad}
            ))
        
        # Check for prime numbers
        if cls._is_prime(abjad):
            matches.append(PatternMatch(
                pattern_type=PatternType.NUMERICAL,
                pattern_value=f"prime:{abjad}",
                position=(0, len(text)),
                confidence=PatternConfidence.MEDIUM,
                metadata={"type": "prime", "value": abjad}
            ))
        
        return matches
    
    @classmethod
    def _is_prime(cls, n: int) -> bool:
        """Check if a number is prime."""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True


# ============================================================================
# Pattern Test Generator
# ============================================================================

class PatternTestGenerator:
    """Generates test cases for linguistic patterns."""
    
    def __init__(self):
        self.muqattaat_detector = MuqattaatDetector()
        self.letter_detector = LetterSequenceDetector()
        self.repetition_detector = RepetitionDetector()
        self.numerical_detector = NumericalPatternDetector()
    
    def generate_tests(
        self,
        text: str,
        surah_id: Optional[int] = None
    ) -> List[PatternTest]:
        """
        Generate test cases for the given text.
        
        Args:
            text: Arabic text to generate tests for
            surah_id: Optional Surah ID for context
            
        Returns:
            List of pattern tests
        """
        tests = []
        
        # Test for Muqattaat prefix
        prefix_tests = self._generate_muqattaat_tests(text, surah_id)
        tests.extend(prefix_tests)
        
        # Test for letter sequences
        sequence_tests = self._generate_sequence_tests(text)
        tests.extend(sequence_tests)
        
        # Test for repetitions
        repetition_tests = self._generate_repetition_tests(text)
        tests.extend(repetition_tests)
        
        # Test for numerical patterns
        numerical_tests = self._generate_numerical_tests(text)
        tests.extend(numerical_tests)
        
        return tests
    
    def _generate_muqattaat_tests(
        self,
        text: str,
        surah_id: Optional[int]
    ) -> List[PatternTest]:
        """Generate Muqattaat prefix tests."""
        tests = []
        
        if surah_id:
            expected_prefix = self.muqattaat_detector.get_prefix_for_surah(surah_id)
            if expected_prefix:
                tests.append(PatternTest(
                    name=f"Muqattaat prefix for Surah {surah_id}",
                    pattern_type=PatternType.MUQATTAAT_PREFIX,
                    test_input=text[:20],
                    expected_output=expected_prefix,
                    is_positive=True,
                    metadata={"surah_id": surah_id}
                ))
        
        return tests
    
    def _generate_sequence_tests(self, text: str) -> List[PatternTest]:
        """Generate letter sequence tests."""
        tests = []
        sequences = self.letter_detector.find_sequences(text)
        
        for seq in sequences[:5]:  # Limit to top 5
            tests.append(PatternTest(
                name=f"Letter sequence: {seq.pattern_value}",
                pattern_type=PatternType.LETTER_SEQUENCE,
                test_input=text,
                expected_output=seq.pattern_value,
                is_positive=True,
                metadata=seq.metadata
            ))
        
        return tests
    
    def _generate_repetition_tests(self, text: str) -> List[PatternTest]:
        """Generate repetition tests."""
        tests = []
        repetitions = self.repetition_detector.find_repetitions(text)
        
        for rep in repetitions[:5]:  # Limit to top 5
            tests.append(PatternTest(
                name=f"Repetition: {rep.pattern_value}",
                pattern_type=PatternType.REPETITION,
                test_input=text,
                expected_output=rep.pattern_value,
                is_positive=True,
                metadata=rep.metadata
            ))
        
        return tests
    
    def _generate_numerical_tests(self, text: str) -> List[PatternTest]:
        """Generate numerical pattern tests."""
        tests = []
        patterns = self.numerical_detector.find_numerical_patterns(text)
        
        for pattern in patterns:
            tests.append(PatternTest(
                name=f"Numerical: {pattern.pattern_value}",
                pattern_type=PatternType.NUMERICAL,
                test_input=text,
                expected_output=pattern.pattern_value,
                is_positive=True,
                metadata=pattern.metadata
            ))
        
        return tests


# ============================================================================
# Pattern Analysis API
# ============================================================================

class PatternAnalyzer:
    """
    Main API for analyzing linguistic patterns.
    This is the primary interface for AI agents to interact with.
    """
    
    def __init__(self):
        self.test_generator = PatternTestGenerator()
    
    def analyze(
        self,
        text: str,
        surah_id: Optional[int] = None,
        include_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive pattern analysis.
        
        Args:
            text: Arabic text to analyze
            surah_id: Optional Surah ID for context
            include_tests: Whether to generate test cases
            
        Returns:
            Dictionary containing analysis results
        """
        results = {
            "text_length": len(text),
            "surah_id": surah_id,
            "patterns_found": [],
            "tests": []
        }
        
        # Run all detectors
        detectors = [
            MuqattaatDetector(),
            LetterSequenceDetector(),
            RepetitionDetector(),
            NumericalPatternDetector()
        ]
        
        for detector in detectors:
            method_name = f"find_{detector.__class__.__name__.replace('Detector', '').lower()}s"
            if hasattr(detector, method_name):
                try:
                    matches = getattr(detector, method_name)(text)
                    results["patterns_found"].extend([
                        m.to_dict() for m in matches
                    ])
                except Exception as e:
                    logger.error(f"Error in {method_name}: {e}")
        
        # Generate tests if requested
        if include_tests:
            tests = self.test_generator.generate_tests(text, surah_id)
            results["tests"] = [t.to_dict() for t in tests]
        
        return results
    
    def create_test_case(
        self,
        name: str,
        pattern_type: PatternType,
        test_input: str,
        expected: Optional[str] = None
    ) -> PatternTest:
        """
        Create a custom test case.
        
        Args:
            name: Test name
            pattern_type: Type of pattern
            test_input: Input text
            expected: Expected output
            
        Returns:
            PatternTest object
        """
        return PatternTest(
            name=name,
            pattern_type=pattern_type,
            test_input=test_input,
            expected_output=expected
        )


# ============================================================================
# Integration with AI Agents
# ============================================================================

def get_pattern_analyzer() -> PatternAnalyzer:
    """Get a PatternAnalyzer instance (for use with AI agents)."""
    return PatternAnalyzer()


def analyze_for_research(
    text: str,
    surah_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function for quick pattern analysis.
    
    Args:
        text: Text to analyze
        surah_id: Optional Surah ID
        
    Returns:
        Analysis results dictionary
    """
    analyzer = PatternAnalyzer()
    return analyzer.analyze(text, surah_id)

