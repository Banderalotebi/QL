"""
Unit tests for Execution Queue Module
"""
import pytest
from collections import deque
from frontend.components.execution_queue import (
    ExecutionQueue,
    QueueConfig,
    ExecutionStatus,
    ExecutionQueueWidget
)


class TestExecutionQueue:
    """Tests for ExecutionQueue class."""
    
    def test_initialization(self):
        """Test queue initialization."""
        queue = ExecutionQueue()
        assert len(queue.queue) == 0
        assert queue.is_paused == False
    
    def test_enqueue(self):
        """Test adding items to queue."""
        queue = ExecutionQueue()
        result = queue.enqueue("pattern_1", "normal")
        assert result == True
        assert len(queue.queue) == 1
    
    def test_enqueue_with_priority(self):
        """Test enqueue with different priorities."""
        queue = ExecutionQueue()
        
        queue.enqueue("low_priority", "low")
        queue.enqueue("high_priority", "high")
        queue.enqueue("normal_priority", "normal")
        
        assert len(queue.queue) == 3
    
    def test_dequeue(self):
        """Test removing items from queue."""
        queue = ExecutionQueue()
        queue.enqueue("pattern_1", "normal")
        queue.enqueue("pattern_2", "high")
        
        item = queue.dequeue()
        assert item is not None
        assert item["pattern_id"] == "pattern_2"  # High priority first
    
    def test_dequeue_empty(self):
        """Test dequeuing from empty queue."""
        queue = ExecutionQueue()
        item = queue.dequeue()
        assert item is None
    
    def test_pause_resume(self):
        """Test pause and resume functionality."""
        queue = ExecutionQueue()
        
        queue.pause()
        assert queue.is_paused == True
        
        result = queue.enqueue("pattern_1", "normal")
        assert result == False  # Cannot enqueue when paused
        
        queue.resume()
        assert queue.is_paused == False
        assert queue.enqueue("pattern_1", "normal") == True
    
    def test_clear(self):
        """Test clearing the queue."""
        queue = ExecutionQueue()
        queue.enqueue("pattern_1")
        queue.enqueue("pattern_2")
        
        cleared = queue.clear()
        assert cleared == 2
        assert len(queue.queue) == 0
    
    def test_priority_update(self):
        """Test updating priority of queued item."""
        queue = ExecutionQueue()
        queue.enqueue("pattern_1", "normal")
        
        result = queue.update_priority("pattern_1", "high")
        assert result == True
        
        # Check priority was updated
        item = queue.queue[0]
        assert item["priority"] == "high"
        assert item["priority_weight"] == 3
    
    def test_priority_update_not_found(self):
        """Test updating priority for non-existent item."""
        queue = ExecutionQueue()
        result = queue.update_priority("nonexistent", "high")
        assert result == False
    
    def test_reorder(self):
        """Test reordering the queue."""
        queue = ExecutionQueue()
        queue.enqueue("pattern_1", "normal")
        queue.enqueue("pattern_2", "normal")
        queue.enqueue("pattern_3", "normal")
        
        queue.reorder(["pattern_3", "pattern_1", "pattern_2"])
        
        ids = [item["pattern_id"] for item in queue.queue]
        assert ids == ["pattern_3", "pattern_1", "pattern_2"]
    
    def test_get_status(self):
        """Test getting queue status."""
        queue = ExecutionQueue()
        queue.enqueue("pattern_1")
        
        status = queue.get_status()
        
        assert "queue_size" in status
        assert "estimated_time_seconds" in status
        assert status["queue_size"] == 1
    
    def test_add_to_history(self):
        """Test adding to execution history."""
        queue = ExecutionQueue()
        
        item = {"pattern_id": "test", "priority": "normal"}
        queue.add_to_history(item, "success", 1000)
        
        history = queue.get_history()
        assert len(history) == 1
        assert history[0]["result"] == "success"
        assert history[0]["duration_ms"] == 1000
    
    def test_get_statistics(self):
        """Test getting execution statistics."""
        queue = ExecutionQueue()
        
        # Add some history
        queue.add_to_history({"pattern_id": "p1"}, "success", 1000)
        queue.add_to_history({"pattern_id": "p2"}, "success", 2000)
        queue.add_to_history({"pattern_id": "p3"}, "failed", 500)
        
        stats = queue.get_statistics()
        
        assert stats["total_executed"] == 3
        assert stats["success_rate"] == pytest.approx(66.67, rel=0.1)
        assert stats["avg_duration_ms"] == 1166


class TestQueueConfig:
    """Tests for QueueConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        assert QueueConfig.DEFAULT_ESTIMATED_TIME_PER_PATTERN == 5
        assert QueueConfig.DEFAULT_BATCH_INTERVAL == 300
        assert QueueConfig.MAX_QUEUE_SIZE == 1000
        assert QueueConfig.DEFAULT_HISTORY_LIMIT == 20
    
    def test_priority_weights(self):
        """Test priority weight mappings."""
        assert QueueConfig.PRIORITY_WEIGHTS["Low"] == 1
        assert QueueConfig.PRIORITY_WEIGHTS["Normal"] == 2
        assert QueueConfig.PRIORITY_WEIGHTS["High"] == 3


class TestExecutionStatus:
    """Tests for ExecutionStatus enum."""
    
    def test_status_values(self):
        """Test enum values."""
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.CANCELLED.value == "cancelled"

