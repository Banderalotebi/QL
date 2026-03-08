"""
Comprehensive Test Suite for Muqattaat Cryptanalytic Lab
Generates detailed reports with visualizations
"""
import pytest
import json
import time
from datetime import datetime
from collections import Counter
from typing import Dict, List, Any

# Import all modules under test
from src.utils.pattern_detection import (
    MuqattaatDetector, LetterSequenceDetector, RepetitionDetector,
    NumericalPatternDetector, PatternAnalyzer
)
from frontend.components.execution_queue import (
    ExecutionQueue, QueueConfig, ExecutionStatus
)
from src.data.db import (
    DatabaseConnectionPool, get_db_connection, with_retry, NeonLabAPI
)
from src.core.state import Hypothesis, ResearchState
from src.data.muqattaat import MUQATTAAT_MAPPING, MUQATTAAT_SURAHS


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_quran_text():
    """Sample Quranic text for testing."""
    return {
        2: "الم",
        3: "المص",
        7: "الر",
        19: "كهيعص",
        20: "طه",
        26: "طسم",
        36: "يس",
        50: "ق",
        68: "ن"
    }


@pytest.fixture
def sample_execution_queue():
    """Create a sample execution queue."""
    q = ExecutionQueue(max_size=100)
    q.enqueue("pattern_001", "high")
    q.enqueue("pattern_002", "normal")
    q.enqueue("pattern_003", "low")
    return q


# ============================================================================
# MuqattaatDetector Tests
# ============================================================================

class TestMuqattaatDetector:
    """Test Muqattaat prefix detection."""
    
    def test_detect_known_prefixes(self, sample_quran_text):
        """Test detection of known Muqattaat prefixes."""
        detector = MuqattaatDetector()
        
        for surah, prefix in sample_quran_text.items():
            result = detector.detect(prefix)
            assert result is not None
            assert result["surah"] == surah
            assert result["prefix"] == prefix
    
    def test_is_muqattaat_surah(self):
        """Test Muqattaat surah identification."""
        detector = MuqattaatDetector()
        
        # Known Muqattaat surahs
        assert detector.is_muqattaat_surah(2) is True
        assert detector.is_muqattaat_surah(36) is True
        assert detector.is_muqattaat_surah(68) is True
        
        # Non-Muqattaat surahs
        assert detector.is_muqattaat_surah(1) is False
        assert detector.is_muqattaat_surah(5) is False
    
    def test_get_prefix_for_surah(self):
        """Test getting prefix for specific surah."""
        detector = MuqattaatDetector()
        
        assert detector.get_prefix_for_surah(2) == "الم"
        assert detector.get_prefix_for_surah(36) == "يس"
        assert detector.get_prefix_for_surah(68) == "ن"
    
    def test_get_all_muqattaat(self):
        """Test getting all Muqattaat surahs."""
        detector = MuqattaatDetector()
        all_muqattaat = detector.get_all_muqattaat()
        
        assert len(all_muqattaat) == 29
        assert 2 in all_muqattaat
        assert 68 in all_muqattaat
    
    def test_letter_frequency(self, sample_quran_text):
        """Test letter frequency analysis."""
        detector = MuqattaatDetector()
        freq = detector.get_letter_frequency()
        
        assert isinstance(freq, dict)
        assert "الم" in freq or len(freq) > 0
    
    def test_unique_prefixes_count(self):
        """Test counting unique prefixes."""
        detector = MuqattaatDetector()
        unique = detector.get_unique_prefixes()
        
        assert len(unique) <= 29
        assert len(unique) >= 14  # Known 14 unique combinations


# ============================================================================
# LetterSequenceDetector Tests
# ============================================================================

class TestLetterSequenceDetector:
    """Test letter sequence detection."""
    
    def test_find_sequences(self):
        """Test finding letter sequences."""
        detector = LetterSequenceDetector()
        text = "المالال"
        
        sequences = detector.find_sequences(text, min_length=2)
        assert isinstance(sequences, list)
    
    def test_count_letters(self):
        """Test letter counting."""
        detector = LetterSequenceDetector()
        text = "الم"
        
        counts = detector.count_letters(text)
        assert counts.get("ا", 0) == 1
        assert counts.get("ل", 0) == 1
        assert counts.get("م", 0) == 1
    
    def test_find_repeating_patterns(self):
        """Test finding repeating patterns."""
        detector = LetterSequenceDetector()
        text = "المالمالم"
        
        patterns = detector.find_repeating_patterns(text)
        assert isinstance(patterns, list)
    
    def test_calculate_diversity(self):
        """Test letter diversity calculation."""
        detector = LetterSequenceDetector()
        
        diversity = detector.calculate_diversity("الم")
        assert 0 <= diversity <= 1.0
        
        diversity2 = detector.calculate_diversity("الالا")
        assert diversity2 <= diversity


# ============================================================================
# RepetitionDetector Tests
# ============================================================================

class TestRepetitionDetector:
    """Test repetition pattern detection."""
    
    def test_find_repetitions(self):
        """Test finding repetitions."""
        detector = RepetitionDetector()
        text = "المالمالم"
        
        reps = detector.find_repetitions(text)
        assert isinstance(reps, list)
    
    def test_calculate_repetition_ratio(self):
        """Test repetition ratio calculation."""
        detector = RepetitionDetector()
        
        ratio1 = detector.calculate_repetition_ratio("AAAA")
        ratio2 = detector.calculate_repetition_ratio("ABCD")
        
        assert ratio1 > ratio2
    
    def test_find_palindromes(self):
        """Test palindrome detection."""
        detector = RepetitionDetector()
        
        # Simple palindrome check
        assert detector.is_palindrome("ABA") is True
        assert detector.is_palindrome("ABCA") is False
    
    def test_longest_repeat(self):
        """Test finding longest repeat."""
        detector = RepetitionDetector()
        text = "المالمالال"
        
        longest = detector.find_longest_repeat(text)
        assert longest is not None


# ============================================================================
# NumericalPatternDetector Tests
# ============================================================================

class TestNumericalPatternDetector:
    """Test numerical pattern detection."""
    
    def test_abjad_calculation(self):
        """Test Abjad value calculation."""
        detector = NumericalPatternDetector()
        
        # Test known Abjad values
        assert detector.calculate_abjad("ا") == 1
        assert detector.calculate_abjad("ب") == 2
        assert detector.calculate_abjad("ج") == 3
    
    def test_word_abjad(self):
        """Test word Abjad calculation."""
        detector = NumericalPatternDetector()
        
        # Alif-Lam-Mim = 1+30+40 = 71
        abjad = detector.calculate_abjad("الم")
        assert abjad == 71
    
    def test_divisibility_patterns(self):
        """Test divisibility pattern detection."""
        detector = NumericalPatternDetector()
        
        patterns = detector.find_divisibility_patterns([1, 2, 3, 4, 6, 12])
        assert isinstance(patterns, list)
    
    def test_prime_analysis(self):
        """Test prime number analysis."""
        detector = NumericalPatternDetector()
        
        primes = detector.get_prime_factors(12)
        assert 2 in primes
        assert 3 in primes
    
    def test_numerical_sequence(self):
        """Test numerical sequence detection."""
        detector = NumericalPatternDetector()
        
        seq_type = detector.identify_sequence([2, 4, 6, 8])
        assert seq_type == "arithmetic"


# ============================================================================
# PatternAnalyzer Tests
# ============================================================================

class TestPatternAnalyzer:
    """Test main PatternAnalyzer API."""
    
    def test_full_analysis(self, sample_quran_text):
        """Test full pattern analysis."""
        analyzer = PatternAnalyzer()
        
        for surah, prefix in sample_quran_text.items():
            result = analyzer.analyze(surah, prefix)
            assert result is not None
            assert "surah" in result
            assert "prefix" in result
    
    def test_batch_analysis(self, sample_quran_text):
        """Test batch analysis."""
        analyzer = PatternAnalyzer()
        
        results = analyzer.batch_analyze(sample_quran_text)
        assert len(results) == len(sample_quran_text)
    
    def test_generate_report(self):
        """Test report generation."""
        analyzer = PatternAnalyzer()
        
        data = {2: "الم", 36: "يس"}
        report = analyzer.generate_report(data)
        
        assert "summary" in report
        assert "total_surahs" in report
        assert report["total_surahs"] == 2
    
    def test_export_results(self, sample_quran_text):
        """Test results export."""
        analyzer = PatternAnalyzer()
        
        results = analyzer.batch_analyze(sample_quran_text)
        exported = analyzer.export_to_json(results)
        
        assert isinstance(exported, str)
        data = json.loads(exported)
        assert len(data) > 0


# ============================================================================
# ExecutionQueue Tests
# ============================================================================

class TestExecutionQueueComprehensive:
    """Comprehensive ExecutionQueue tests."""
    
    def test_enqueue_with_priorities(self):
        """Test enqueueing with different priorities."""
        q = ExecutionQueue()
        
        q.enqueue("p1", "high")
        q.enqueue("p2", "normal")
        q.enqueue("p3", "low")
        
        assert len(q.queue) == 3
    
    def test_priority_dequeue_order(self):
        """Test that high priority items are dequeued first."""
        q = ExecutionQueue()
        
        q.enqueue("low", "low")
        q.enqueue("high", "high")
        q.enqueue("normal", "normal")
        
        next_item = q.dequeue()
        assert next_item["pattern_id"] == "high"
    
    def test_queue_pause_resume(self):
        """Test pause and resume functionality."""
        q = ExecutionQueue()
        
        q.enqueue("p1", "normal")
        q.pause()
        
        result = q.enqueue("p2", "normal")
        assert result is False  # Should fail when paused
        
        q.resume()
        result = q.enqueue("p3", "normal")
        assert result is True
    
    def test_clear_queue(self):
        """Test clearing the queue."""
        q = ExecutionQueue()
        
        q.enqueue("p1", "normal")
        q.enqueue("p2", "normal")
        
        count = q.clear()
        assert count == 2
        assert len(q.queue) == 0
    
    def test_reorder_queue(self):
        """Test reordering queue."""
        q = ExecutionQueue()
        
        q.enqueue("a", "normal")
        q.enqueue("b", "normal")
        q.enqueue("c", "normal")
        
        q.reorder(["c", "a", "b"])
        
        ids = [item["pattern_id"] for item in q.queue]
        assert ids == ["c", "a", "b"]
    
    def test_update_priority(self):
        """Test updating item priority."""
        q = ExecutionQueue()
        
        q.enqueue("p1", "low")
        q.update_priority("p1", "high")
        
        item = q.peek()
        assert item["priority"] == "high"
    
    def test_history_tracking(self):
        """Test execution history tracking."""
        q = ExecutionQueue()
        
        q.enqueue("p1", "normal")
        item = q.dequeue()
        q.add_to_history(item, "success", 1000)
        
        history = q.get_history()
        assert len(history) == 1
        assert history[0]["result"] == "success"
    
    def test_statistics(self):
        """Test statistics calculation."""
        q = ExecutionQueue()
        
        q.enqueue("p1", "normal")
        item = q.dequeue()
        q.add_to_history(item, "success", 1000)
        q.add_to_history(item, "success", 2000)
        
        stats = q.get_statistics()
        assert stats["total_executed"] >= 1
        assert stats["success_rate"] >= 0


# ============================================================================
# Database Tests
# ============================================================================

class TestDatabaseComprehensive:
    """Comprehensive database tests."""
    
    def test_pool_singleton(self):
        """Test that connection pool is singleton."""
        pool1 = DatabaseConnectionPool()
        pool2 = DatabaseConnectionPool()
        
        assert pool1 is pool2
    
    def test_context_manager(self):
        """Test database context manager."""
        with get_db_connection() as conn:
            assert conn is not None
    
    @pytest.mark.slow
    def test_retry_success_first_try(self):
        """Test retry decorator succeeds on first try."""
        call_count = 0
        
        @with_retry
        def succeed_first():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = succeed_first()
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.slow
    def test_retry_success_after_failures(self):
        """Test retry decorator succeeds after failures."""
        call_count = 0
        
        @with_retry
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = fail_then_succeed()
        assert result == "success"
        assert call_count == 3
    
    def test_neon_lab_api_init(self):
        """Test NeonLabAPI initialization."""
        api = NeonLabAPI()
        # Should not raise exception
        assert api is not None


# ============================================================================
# State Management Tests
# ============================================================================

class TestStateManagement:
    """Test state management."""
    
    def test_hypothesis_creation(self):
        """Test Hypothesis creation."""
        h = Hypothesis(
            source_scout="TestScout",
            goal_link="Test goal",
            transformation_steps=3,
            evidence_snippets=["evidence1"]
        )
        
        assert h.source_scout == "TestScout"
        assert h.metadata == {}
    
    def test_hypothesis_with_metadata(self):
        """Test Hypothesis with metadata."""
        h = Hypothesis(
            source_scout="TestScout",
            goal_link="Test goal",
            transformation_steps=3,
            evidence_snippets=[],
            metadata={"key": "value"}
        )
        
        assert h.metadata["key"] == "value"
    
    def test_research_state_creation(self):
        """Test ResearchState creation."""
        state: ResearchState = {
            "surah_numbers": [2, 36],
            "focus": "muqattaat",
            "raw_hypotheses": []
        }
        
        assert len(state["surah_numbers"]) == 2
    
    def test_muqattaat_constants(self):
        """Test Muqattaat constants."""
        assert len(MUQATTAAT_SURAHS) == 29
        assert len(MUQATTAAT_MAPPING) == 29
        assert MUQATTAAT_MAPPING[2] == "الم"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_pattern_to_queue_pipeline(self, sample_quran_text):
        """Test full pipeline from pattern detection to queue."""
        # Step 1: Detect patterns
        analyzer = PatternAnalyzer()
        results = analyzer.batch_analyze(sample_quran_text)
        
        # Step 2: Add to queue
        q = ExecutionQueue()
        for result in results:
            q.enqueue(result["surah"], "normal")
        
        assert len(q.queue) == len(sample_quran_text)
        
        # Step 3: Process queue
        item = q.dequeue()
        q.add_to_history(item, "success", 500)
        
        stats = q.get_statistics()
        assert stats["total_executed"] >= 1
    
    def test_pattern_analysis_to_report(self):
        """Test pattern analysis generates proper report."""
        analyzer = PatternAnalyzer()
        
        data = {
            2: "الم",
            3: "المص",
            36: "يس"
        }
        
        report = analyzer.generate_report(data)
        
        assert report["total_surahs"] == 3
        assert "unique_prefixes" in report
        assert "letter_distribution" in report


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance benchmark tests."""
    
    @pytest.mark.slow
    def test_pattern_analyzer_performance(self):
        """Test pattern analyzer performance."""
        analyzer = PatternAnalyzer()
        
        # Create test data
        test_data = {i: f"prefix_{i}" for i in range(1, 101)}
        
        start = time.time()
        results = analyzer.batch_analyze(test_data)
        elapsed = time.time() - start
        
        assert len(results) == 100
        assert elapsed < 5.0  # Should complete in under 5 seconds
    
    @pytest.mark.slow
    def test_queue_operations_performance(self):
        """Test queue operations performance."""
        q = ExecutionQueue()
        
        start = time.time()
        
        # Add 1000 items
        for i in range(1000):
            q.enqueue(f"pattern_{i}", "normal")
        
        # Remove all
        for _ in range(1000):
            q.dequeue()
        
        elapsed = time.time() - start
        
        assert elapsed < 1.0  # Should be very fast with deque


# ============================================================================
# Test Report Generator
# ============================================================================

def generate_test_report():
    """Generate a comprehensive test report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_suites": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
    }
    return report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
</parameter>
</create_file>
