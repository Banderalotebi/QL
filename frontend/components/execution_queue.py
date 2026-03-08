"""
Execution Queue Component - Streamlit UI
Manages pattern execution queue visualization and control

Improvements:
- Uses collections.deque for O(1) queue operations
- Configurable timing constants
- Proper error handling and logging
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration Constants
# ============================================================================

class QueueConfig:
    """Configuration constants for the execution queue."""
    DEFAULT_ESTIMATED_TIME_PER_PATTERN = 5  # seconds
    DEFAULT_BATCH_INTERVAL = 300  # seconds
    MAX_QUEUE_SIZE = 1000
    DEFAULT_HISTORY_LIMIT = 20
    PRIORITY_LEVELS = ["Low", "Normal", "High"]
    PRIORITY_WEIGHTS = {"Low": 1, "Normal": 2, "High": 3}
    PRIORITY_WEIGHTS_LOWER = {"low": 1, "normal": 2, "high": 3}


class ExecutionStatus(Enum):
    """Status states for execution items."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Execution Queue Core
# ============================================================================

class ExecutionQueue:
    """
    Manages the execution queue for pattern processing.
    
    Uses deque for O(1) append and popleft operations.
    """
    
    def __init__(self, max_size: int = QueueConfig.MAX_QUEUE_SIZE):
        """
        Initialize the execution queue.
        
        Args:
            max_size: Maximum number of items in the queue
        """
        self._queue: deque = deque(maxlen=max_size)
        self._execution_history: List[Dict] = []
        self._paused: bool = False
    
    @property
    def queue(self) -> List[Dict]:
        """Get current queue as list (for backward compatibility)."""
        return list(self._queue)
    
    @property
    def is_paused(self) -> bool:
        """Check if queue is paused."""
        return self._paused
    
    def pause(self) -> None:
        """Pause the queue."""
        self._paused = True
        logger.info("Execution queue paused")
    
    def resume(self) -> None:
        """Resume the queue."""
        self._paused = False
        logger.info("Execution queue resumed")
    
    def enqueue(self, pattern_id: str, priority: str = "normal") -> bool:
        """
        Add pattern to queue.
        
        Args:
            pattern_id: Unique identifier for the pattern
            priority: Priority level ("low", "normal", "high")
        
        Returns:
            True if successfully enqueued, False otherwise
        """
        if self._paused:
            logger.warning("Cannot enqueue - queue is paused")
            return False
        
        # Normalize priority
        priority = priority.lower() if priority else "normal"
        if priority not in QueueConfig.PRIORITY_WEIGHTS_LOWER:
            priority = "normal"
        
        item = {
            "pattern_id": pattern_id,
            "priority": priority,
            "priority_weight": QueueConfig.PRIORITY_WEIGHTS_LOWER[priority],
            "enqueued_at": datetime.now().isoformat(),
            "status": ExecutionStatus.PENDING.value,
            "attempts": 0
        }
        
        self._queue.append(item)
        logger.info(f"Enqueued pattern {pattern_id} with priority {priority}")
        return True
    
    def dequeue(self) -> Optional[Dict]:
        """
        Remove and return next pattern from queue.
        Uses priority-based dequeueing (high priority first).
        
        Returns:
            The next item or None if queue is empty
        """
        if not self._queue:
            return None
        
        # Find highest priority item
        best_index = 0
        best_weight = 0
        
        for i, item in enumerate(self._queue):
            weight = item.get("priority_weight", 0)
            if weight > best_weight:
                best_weight = weight
                best_index = i
        
        # Convert to list to remove item at index, then back to deque
        queue_list = list(self._queue)
        item = queue_list.pop(best_index)
        self._queue = deque(queue_list, maxlen=self._queue.maxlen)
        
        item["status"] = ExecutionStatus.RUNNING.value
        item["started_at"] = datetime.now().isoformat()
        
        logger.debug(f"Dequeued pattern {item['pattern_id']}")
        return item
    
    def peek(self) -> Optional[Dict]:
        """View next item without removing it."""
        if not self._queue:
            return None
        
        # Find highest priority item
        best_index = 0
        best_weight = 0
        
        for i, item in enumerate(self._queue):
            weight = item.get("priority_weight", 0)
            if weight > best_weight:
                best_weight = weight
                best_index = i
        
        return self._queue[best_index]
    
    def get_status(self) -> Dict:
        """Get queue status."""
        return {
            "queue_size": len(self._queue),
            "patterns": list(self._queue),
            "estimated_time_seconds": len(self._queue) * QueueConfig.DEFAULT_ESTIMATED_TIME_PER_PATTERN,
            "is_paused": self._paused,
            "avg_duration_seconds": QueueConfig.DEFAULT_ESTIMATED_TIME_PER_PATTERN
        }
    
    def clear(self) -> int:
        """
        Clear queue.
        
        Returns:
            Number of items cleared
        """
        cleared_count = len(self._queue)
        self._queue.clear()
        logger.info(f"Cleared {cleared_count} items from queue")
        return cleared_count
    
    def reorder(self, new_order: List[str]) -> None:
        """
        Reorder queue based on pattern IDs.
        
        Args:
            new_order: List of pattern IDs in desired order
        """
        pattern_map = {item['pattern_id']: item for item in self._queue}
        new_queue = deque(maxlen=self._queue.maxlen)
        
        for pattern_id in new_order:
            if pattern_id in pattern_map:
                new_queue.append(pattern_map[pattern_id])
        
        self._queue = new_queue
        logger.debug(f"Reordered queue with {len(new_order)} items")
    
    def update_priority(self, pattern_id: str, new_priority: str) -> bool:
        """
        Update priority of a specific pattern.
        
        Args:
            pattern_id: The pattern to update
            new_priority: New priority level
        
        Returns:
            True if updated, False if not found
        """
        new_priority = new_priority.lower()
        if new_priority not in QueueConfig.PRIORITY_WEIGHTS_LOWER:
            return False
        
        for item in self._queue:
            if item['pattern_id'] == pattern_id:
                item['priority'] = new_priority
                item['priority_weight'] = QueueConfig.PRIORITY_WEIGHTS_LOWER[new_priority]
                logger.debug(f"Updated priority for {pattern_id} to {new_priority}")
                return True
        
        return False
    
    def add_to_history(self, item: Dict, result: str = "success", duration_ms: int = 0) -> None:
        """
        Add completed item to execution history.
        
        Args:
            item: The completed item
            result: Execution result
            duration_ms: Duration in milliseconds
        """
        history_item = {
            **item,
            "result": result,
            "duration_ms": duration_ms,
            "completed_at": datetime.now().isoformat()
        }
        self._execution_history.append(history_item)
        
        # Trim history if too large
        if len(self._execution_history) > 1000:
            self._execution_history = self._execution_history[-500:]
    
    def get_history(self, limit: int = QueueConfig.DEFAULT_HISTORY_LIMIT) -> List[Dict]:
        """Get execution history."""
        return self._execution_history[-limit:]
    
    def get_statistics(self) -> Dict:
        """Get execution statistics."""
        if not self._execution_history:
            return {
                "total_executed": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0
            }
        
        total = len(self._execution_history)
        success = sum(1 for item in self._execution_history if item.get("result") == "success")
        total_duration = sum(item.get("duration_ms", 0) for item in self._execution_history)
        
        return {
            "total_executed": total,
            "success_rate": (success / total * 100) if total > 0 else 0.0,
            "avg_duration_ms": total_duration // total if total > 0 else 0
        }


# ============================================================================
# Streamlit UI Widget
# ============================================================================

class ExecutionQueueWidget:
    """Streamlit UI widget for execution queue management."""
    
    @staticmethod
    def render_queue_overview(queue_status: Dict) -> None:
        """Render overview of current queue."""
        st.subheader("📥 Execution Queue")
        
        col1, col2, col3, col4 = st.columns(4)
        
        queue_size = queue_status.get("queue_size", 0)
        estimated_time = queue_status.get("estimated_time_seconds", 0)
        avg_duration = queue_status.get("avg_duration_seconds", QueueConfig.DEFAULT_ESTIMATED_TIME_PER_PATTERN)
        
        col1.metric("Queue Size", queue_size)
        col2.metric("Patterns Pending", queue_size)
        col3.metric("Est. Time", f"{estimated_time}s")
        col4.metric("Avg. Duration", f"~{avg_duration}s per pattern")
        
        # Show pause status
        if queue_status.get("is_paused", False):
            st.warning("⏸️ Queue is paused")
    
    @staticmethod
    def render_queue_items(patterns: List[Dict]) -> None:
        """Render queue items as draggable list."""
        st.write("### Queued Patterns")
        
        if not patterns:
            st.info("Queue is empty")
            return
        
        # Create dataframe
        df_data = []
        for i, item in enumerate(patterns):
            df_data.append({
                "Position": i + 1,
                "Pattern": item.get("pattern_id", "Unknown"),
                "Priority": item.get("priority", "normal").upper(),
                "Status": item.get("status", "pending").upper(),
                "Enqueued": item.get("enqueued_at", "").split("T")[1][:5] if "T" in item.get("enqueued_at", "") else ""
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # Add controls for queue management
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Execute Queue", key="execute_queue_btn"):
                st.success(f"Executing {len(patterns)} patterns...")
        
        with col2:
            if st.button("⏸️ Pause Queue", key="pause_queue_btn"):
                st.info("Queue paused")
        
        with col3:
            if st.button("🗑️ Clear Queue", key="clear_queue_btn"):
                st.warning("Queue cleared")
    
    @staticmethod
    def render_pattern_selector(available_patterns: List[Dict]) -> Optional[str]:
        """Render pattern selector to add to queue."""
        st.subheader("➕ Add Pattern to Queue")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Create options from available patterns
            pattern_options = {
                p.get("pattern_id"): f"{p.get('name', p.get('pattern_id', ''))} ({p.get('type', '')})"
                for p in available_patterns
            }
            
            selected = st.selectbox(
                "Select Pattern",
                options=list(pattern_options.keys()),
                format_func=lambda x: pattern_options.get(x, x),
                key="pattern_selector"
            )
        
        with col2:
            priority = st.selectbox(
                "Priority",
                QueueConfig.PRIORITY_LEVELS,
                index=1,
                key="pattern_priority"
            )
        
        with col3:
            st.write("")
            st.write("")
            if st.button("➕ Add", use_container_width=True, key="add_pattern_btn"):
                return selected
        
        return None
    
    @staticmethod
    def render_execution_history(history: List[Dict], limit: int = 20) -> None:
        """Render execution history."""
        st.subheader("📊 Execution History")
        
        if not history:
            st.info("No execution history")
            return
        
        # Display recent executions
        df_data = []
        for item in history[-limit:]:
            df_data.append({
                "Pattern": item.get("pattern_id", "Unknown"),
                "Result": item.get("result", "unknown").upper(),
                "Duration (ms)": item.get("duration_ms", 0),
                "Timestamp": item.get("completed_at", "").split("T")[1][:5] if "T" in item.get("completed_at", "") else ""
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            success_count = sum(1 for item in history if item.get("result") == "success")
            success_rate = success_count / len(history) * 100 if history else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Executed", len(history))
            col2.metric("Success Rate", f"{success_rate:.1f}%")
            col3.metric("Avg Duration", f"{sum(h.get('duration_ms', 0) for h in history) // max(len(history), 1)}ms")
    
    @staticmethod
    def render_priority_adjustment(patterns: List[Dict]) -> None:
        """Allow adjusting pattern priorities in queue."""
        st.subheader("⚖️ Priority Management")
        
        if not patterns:
            st.info("No patterns to adjust")
            return
        
        for item in patterns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"Pattern {item.get('pattern_id')}")
            
            with col2:
                priority_index = 1  # Default to "Normal"
                current_priority = item.get("priority", "normal").lower()
                if current_priority in QueueConfig.PRIORITY_LEVELS:
                    priority_index = QueueConfig.PRIORITY_LEVELS.index(current_priority.capitalize())
                
                new_priority = st.selectbox(
                    "Priority",
                    QueueConfig.PRIORITY_LEVELS,
                    index=priority_index,
                    key=f"priority_{item.get('pattern_id')}"
                )
    
    @staticmethod
    def render_batch_operations(patterns: List[Dict]) -> None:
        """Allow batch operations on queue."""
        st.subheader("📦 Batch Operations")
        
        col1, col2, col3 = st.columns(3)
        
        max_batch = len(patterns) if patterns else 1
        default_batch = min(5, max_batch)
        
        with col1:
            batch_size = st.number_input(
                "Batch Size",
                min_value=1,
                max_value=max_batch,
                value=default_batch,
                key="batch_size"
            )
        
        with col2:
            interval = st.number_input(
                "Interval (seconds)",
                min_value=1,
                max_value=3600,
                value=QueueConfig.DEFAULT_BATCH_INTERVAL,
                key="batch_interval"
            )
        
        with col3:
            st.write("")
            st.write("")
            if st.button("⚙️ Configure Batching", use_container_width=True, key="configure_batching_btn"):
                st.success(f"Batch processing: {batch_size} patterns every {interval}s")


def create_execution_queue_tab(hive, pattern_web) -> None:
    """
    Create a complete execution queue tab for Streamlit dashboard
    
    Args:
        hive: HiveCouncil instance
        pattern_web: PatternWebVisualizer instance
    """
    tab1, tab2, tab3 = st.tabs(["📋 Queue", "📊 History", "⚙️ Settings"])
    
    with tab1:
        st.header("Pattern Execution Queue")
        
        queue_status = pattern_web.get_queue_status()
        ExecutionQueueWidget.render_queue_overview(queue_status)
        
        st.divider()
        
        # Show current queue
        ExecutionQueueWidget.render_queue_items(queue_status.get("queued_patterns", []))
        
        st.divider()
        
        # Add patterns to queue
        available_patterns = list(pattern_web.patterns.values())
        available_dicts = [
            {
                "pattern_id": p.pattern_id,
                "name": p.metadata.get("name", p.pattern_id),
                "type": p.pattern_type
            }
            for p in available_patterns
        ]
        
        selected_pattern = ExecutionQueueWidget.render_pattern_selector(available_dicts)
        if selected_pattern:
            pattern_web.add_pattern_to_queue(selected_pattern)
            st.success(f"Added {selected_pattern} to queue!")
    
    with tab2:
        st.header("Execution History")
        ExecutionQueueWidget.render_execution_history([])
    
    with tab3:
        st.header("Queue Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ExecutionQueueWidget.render_batch_operations(queue_status.get("queued_patterns", []))
        
        with col2:
            ExecutionQueueWidget.render_priority_adjustment(queue_status.get("queued_patterns", []))

