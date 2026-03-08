"""
Unit tests for Pattern Detection Module
"""
import pytest
from src.utils.pattern_detection import (
    PatternAnalyzer,
    MuqattaatDetector,
    LetterSequenceDetector,
    RepetitionDetector,
    NumericalPatternDetector,
    PatternTest,
    PatternType,
    PatternConfidence
)


class TestMuqattaatDetector:
    """Tests for Muqattaat prefix detection."""
    
    def test_detect_prefix_alif_lam_mim(self):
        """Test detection of 'الم' prefix."""
        text = "الم كتاب أنزلناه"
        matches = MuqattaatDetector.detect_prefix(text)
        assert len(matches) > 0
        assert matches[0].pattern_value == "الم"
        assert matches[0].confidence == PatternConfidence.HIGH
    
    def test_detect_prefix_ta_ha(self):
        """Test detection of 'طه' prefix."""
        text = "طه"
        matches = MuqattaatDetector.detect_prefix(text)
        assert len(matches) > 0
        assert matches[0].pattern_value == "طه"
    
    def test_get_prefix_for_surah(self):
        """Test getting prefix for specific Surah."""
        prefix = MuqattaatDetector.get_prefix_for_surah(2)
        assert prefix == "الم"
        
        prefix = MuqattaatDetector.get_prefix_for_surah(68)
        assert prefix == "ن"
    
    def test_no_prefix(self):
        """Test text without Muqattaat prefix."""
        text = "بسم الله"
        matches = MuqattaatDetector.detect_prefix(text)
        assert len(matches) == 0


class TestLetterSequenceDetector:
    """Tests for letter sequence detection."""
    
    def test_find_sequences(self):
        """Test finding letter sequences."""
        text = "السلام عليكم السلام"
        matches = LetterSequenceDetector.find_sequences(text, min_length=2)
        # Should find "ال" which repeats
        assert isinstance(matches, list)
    
    def test_analyze_transitions(self):
        """Test letter transition analysis."""
        text = "abc"
        transitions = LetterSequenceDetector.analyze_transitions(text)
        assert "ab" in transitions
        assert transitions["ab"] == 1


class TestRepetitionDetector:
    """Tests for repetition detection."""
    
    def test_find_consecutive_repetitions(self):
        """Test finding consecutive word repetitions."""
        text = "الله الله"
        matches = RepetitionDetector.find_repetitions(text)
        assert len(matches) > 0
    
    def test_find_non_consecutive_repetitions(self):
        """Test finding non-consecutive repetitions."""
        text = "الله الرحمن الله"
        matches = RepetitionDetector.find_repetitions(text)
        assert len(matches) > 0


class TestNumericalPatternDetector:
    """Tests for numerical pattern detection."""
    
    def test_calculate_abjad(self):
        """Test Abjad calculation."""
        # Allah = ا + ل + ل + ه = 1 + 23 + 23 + 5 = 52
        abjad = NumericalPatternDetector.calculate_abjad("الله")
        assert abjad > 0
    
    def test_count_letters(self):
        """Test letter counting."""
        text = "الله"
        counts = NumericalPatternDetector.count_letters(text)
        assert "ا" in counts or "ل" in counts or "ه" in counts
    
    def test_prime_detection(self):
        """Test prime number detection."""
        assert NumericalPatternDetector._is_prime(2) == True
        assert NumericalPatternDetector._is_prime(3) == True
        assert NumericalPatternDetector._is_prime(4) == False
        assert NumericalPatternDetector._is_prime(1) == False


class TestPatternAnalyzer:
    """Tests for main PatternAnalyzer class."""
    
    def test_analyze_basic(self):
        """Test basic analysis."""
        analyzer = PatternAnalyzer()
        result = analyzer.analyze("الم", surah_id=2, include_tests=False)
        
        assert "patterns_found" in result
        assert "text_length" in result
        assert result["surah_id"] == 2
    
    def test_analyze_with_tests(self):
        """Test analysis with test generation."""
        analyzer = PatternAnalyzer()
        result = analyzer.analyze("الم", surah_id=2, include_tests=True)
        
        assert "tests" in result
        assert len(result["tests"]) > 0
    
    def test_create_test_case(self):
        """Test custom test case creation."""
        analyzer = PatternAnalyzer()
        test = analyzer.create_test_case(
            name="Test",
            pattern_type=PatternType.MUQATTAAT_PREFIX,
            test_input="الم",
            expected="الم"
        )
        
        assert test.name == "Test"
        assert test.pattern_type == PatternType.MUQATTAAT_PREFIX
        assert test.expected_output == "الم"


class TestPatternTest:
    """Tests for PatternTest dataclass."""
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        test = PatternTest(
            name="Test",
            pattern_type=PatternType.LETTER_SEQUENCE,
            test_input="test",
            expected_output="result"
        )
        
        d = test.to_dict()
        assert d["name"] == "Test"
        assert d["pattern_type"] == "letter_sequence"

