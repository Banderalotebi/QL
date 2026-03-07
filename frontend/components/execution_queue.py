"""
Execution Queue Component - Streamlit UI
Manages pattern execution queue visualization and control
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExecutionQueue:
    """Manages the execution queue for pattern processing"""
    
    def __init__(self):
        self.queue: List[Dict] = []
        self.execution_history: List[Dict] = []
    
    def enqueue(self, pattern_id: str, priority: str = "normal") -> bool:
        """Add pattern to queue"""
        item = {
            "pattern_id": pattern_id,
            "priority": priority,
            "enqueued_at": datetime.now().isoformat(),
            "status": "pending"
        }
        self.queue.append(item)
        logger.info(f"Enqueued pattern {pattern_id}")
        return True
    
    def dequeue(self) -> Optional[Dict]:
        """Remove and return next pattern from queue"""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def get_status(self) -> Dict:
        """Get queue status"""
        return {
            "queue_size": len(self.queue),
            "patterns": self.queue.copy(),
            "estimated_time_seconds": len(self.queue) * 5
        }
    
    def clear(self) -> None:
        """Clear queue"""
        self.queue.clear()
    
    def reorder(self, new_order: List[str]) -> None:
        """Reorder queue based on pattern IDs"""
        new_queue = []
        pattern_map = {item['pattern_id']: item for item in self.queue}
        
        for pattern_id in new_order:
            if pattern_id in pattern_map:
                new_queue.append(pattern_map[pattern_id])
        
        self.queue = new_queue


class ExecutionQueueWidget:
    """Streamlit UI widget for execution queue management"""
    
    @staticmethod
    def render_queue_overview(queue_status: Dict) -> None:
        """Render overview of current queue"""
        st.subheader("📥 Execution Queue")
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Queue Size", queue_status.get("queue_size", 0))
        col2.metric("Patterns Pending", queue_status.get("queue_size", 0))
        col3.metric("Est. Time", f"{queue_status.get('estimated_time_seconds', 0)}s")
        col4.metric("Avg. Duration", "~5s per pattern")
    
    @staticmethod
    def render_queue_items(patterns: List[Dict]) -> None:
        """Render queue items as draggable list"""
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
            if st.button("🚀 Execute Queue"):
                st.success(f"Executing {len(patterns)} patterns...")
        
        with col2:
            if st.button("⏸️ Pause Queue"):
                st.info("Queue paused")
        
        with col3:
            if st.button("🗑️ Clear Queue"):
                st.warning("Queue cleared")
    
    @staticmethod
    def render_pattern_selector(available_patterns: List[Dict]) -> Optional[str]:
        """Render pattern selector to add to queue"""
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
                ["Low", "Normal", "High"],
                index=1,
                key="pattern_priority"
            )
        
        with col3:
            st.write("")
            st.write("")
            if st.button("➕ Add", use_container_width=True):
                return selected
        
        return None
    
    @staticmethod
    def render_execution_history(history: List[Dict], limit: int = 20) -> None:
        """Render execution history"""
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
                "Timestamp": item.get("timestamp", "").split("T")[1][:5] if "T" in item.get("timestamp", "") else ""
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
        """Allow adjusting pattern priorities in queue"""
        st.subheader("⚖️ Priority Management")
        
        if not patterns:
            st.info("No patterns to adjust")
            return
        
        for item in patterns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"Pattern {item.get('pattern_id')}")
            
            with col2:
                new_priority = st.selectbox(
                    "Priority",
                    ["Low", "Normal", "High"],
                    index=["low", "normal", "high"].index(item.get("priority", "normal")),
                    key=f"priority_{item.get('pattern_id')}"
                )
    
    @staticmethod
    def render_batch_operations(patterns: List[Dict]) -> None:
        """Allow batch operations on queue"""
        st.subheader("📦 Batch Operations")
        
        col1, col2, col3 = st.columns(3)
        
        max_batch = len(patterns) if patterns else 1
        default_batch = min(5, max_batch)  # Ensure default doesn't exceed max
        
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
                value=300,
                key="batch_interval"
            )
        
        with col3:
            st.write("")
            st.write("")
            if st.button("⚙️ Configure Batching", use_container_width=True):
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
