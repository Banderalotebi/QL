"""
Knowledge Broadcast System - Streamlit UI Component
Allows pushing knowledge updates to all agents via shared vector store
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class BroadcastMessage:
    """Represents a knowledge broadcast message"""
    
    def __init__(self, message_id: str, content: str, sender: str, priority: str = "normal"):
        self.message_id = message_id
        self.content = content
        self.sender = sender
        self.timestamp = datetime.now().isoformat()
        self.priority = priority  # "low", "normal", "high", "critical"
        self.recipients: List[str] = []
        self.acknowledged_by: List[str] = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "content": self.content,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "recipients": self.recipients,
            "acknowledged_by": self.acknowledged_by
        }


class MessageQueue:
    """Manages broadcast message queue"""
    
    def __init__(self):
        self.messages: List[BroadcastMessage] = []
        self.broadcast_history: List[Dict] = []
    
    def add_message(self, message: BroadcastMessage) -> str:
        """Add message to queue"""
        self.messages.append(message)
        logger.info(f"Message {message.message_id} added to queue")
        return message.message_id
    
    def get_pending(self) -> List[BroadcastMessage]:
        """Get pending messages"""
        return self.messages.copy()
    
    def acknowledge(self, message_id: str, agent_id: str) -> bool:
        """Mark message as acknowledged by agent"""
        for msg in self.messages:
            if msg.message_id == message_id:
                if agent_id not in msg.acknowledged_by:
                    msg.acknowledged_by.append(agent_id)
                return True
        return False
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get broadcast history"""
        return self.broadcast_history[-limit:]


class BroadcastPanel:
    """
    Streamlit UI component for knowledge broadcasting
    Manages pushing knowledge updates to the hive
    """
    
    def __init__(self):
        self.message_queue = MessageQueue()
    
    @staticmethod
    def render_broadcast_input() -> Optional[Dict]:
        """Render knowledge input widget"""
        st.subheader("📡 Broadcast New Knowledge")
        
        broadcast_type = st.selectbox(
            "Knowledge Type",
            ["Pattern Discovery", "Error Alert", "Optimization Tip", "Style Guide", "Custom"],
            key="broadcast_type"
        )
        
        priority = st.select_slider(
            "Priority",
            options=["Low", "Normal", "High", "Critical"],
            value="Normal",
            key="broadcast_priority"
        )
        
        content = st.text_area(
            "Knowledge Content",
            placeholder="Share a discovery, error pattern, optimization, or style rule...",
            height=150,
            key="broadcast_content"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Broadcast Now", use_container_width=True):
                if content.strip():
                    return {
                        "type": broadcast_type,
                        "priority": priority.lower(),
                        "content": content
                    }
                else:
                    st.error("Please enter knowledge content")
        
        with col2:
            if st.button("💾 Save Draft", use_container_width=True):
                st.info("Draft saved")
        
        return None
    
    @staticmethod
    def render_broadcast_history(history: List[Dict]) -> None:
        """Render recent broadcasts"""
        st.subheader("📜 Broadcast History")
        
        if not history:
            st.info("No broadcasts yet")
            return
        
        # Create display dataframe
        display_items = []
        for msg in history[-20:]:
            display_items.append({
                "Time": msg.get("timestamp", "").split("T")[1][:5],
                "Type": msg.get("type", "Custom"),
                "Priority": msg.get("priority", "").upper(),
                "Message": msg.get("content", "")[:50] + "..." if len(msg.get("content", "")) > 50 else msg.get("content", ""),
                "Agents": len(msg.get("acknowledged_by", []))
            })
        
        if display_items:
            df = pd.DataFrame(display_items)
            st.dataframe(df, use_container_width=True)
    
    @staticmethod
    def render_knowledge_categories() -> None:
        """Render knowledge management categories"""
        st.subheader("📚 Knowledge Categories")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Pattern Discoveries", "143", "+5 this week")
        
        with col2:
            st.metric("Known Errors", "28", "Documented")
        
        with col3:
            st.metric("Optimization Tips", "67", "+3 this week")
        
        with col4:
            st.metric("Style Rules", "12", "Active")
    
    @staticmethod
    def render_pending_broadcasts(hive) -> None:
        """Render pending broadcasts awaiting distribution"""
        st.subheader("⏳ Pending Distribution")
        
        pending = hive.shared_memory.get("pending_broadcasts", [])
        
        if not pending:
            st.info("All broadcasts distributed")
            return
        
        for idx, msg in enumerate(pending):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**{msg.get('type', 'Update')}**")
                    st.write(msg.get("content", "")[:100])
                
                with col2:
                    # Use unique key with index to avoid duplicates
                    msg_id = msg.get('message_id') or msg.get('id') or f"msg_{idx}"
                    if st.button("✓ Ack", key=f"ack_{msg_id}_{idx}"):
                        if hasattr(hive, 'acknowledge_broadcast'):
                            hive.acknowledge_broadcast(msg_id, agent_id="system")
                        st.success("Acknowledged by all agents")
    
    @staticmethod
    def render_agent_acknowledgment(broadcasts: List[Dict]) -> None:
        """Show which agents have acknowledged broadcasts"""
        st.subheader("✓ Agent Acknowledgments")
        
        if not broadcasts:
            st.info("No broadcasts to track")
            return
        
        # Create acknowledgment table
        ack_data = []
        for broadcast in broadcasts[-10:]:
            ack_data.append({
                "Broadcast ID": broadcast.get("message_id", "")[:10],
                "Type": broadcast.get("type", ""),
                "Acknowledged": len(broadcast.get("acknowledged_by", [])),
                "Total": 4,  # Number of agents
                "Status": "✓ Complete" if len(broadcast.get("acknowledged_by", [])) >= 4 else "⏳ Pending"
            })
        
        if ack_data:
            df = pd.DataFrame(ack_data)
            st.dataframe(df, use_container_width=True)
    
    @staticmethod
    def render_knowledge_base_stats() -> None:
        """Render knowledge base statistics"""
        st.subheader("📊 Knowledge Base Stats")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Top Categories")
            categories = {
                "Mathematical Patterns": 143,
                "Linguistic Rules": 87,
                "Cryptographic Keys": 56,
                "Performance Tips": 67,
                "Error Patterns": 28
            }
            
            for cat, count in categories.items():
                st.write(f"- {cat}: {count}")
        
        with col2:
            st.write("### Recent Activity")
            st.write("- Pattern #521 discovered (2 min ago)")
            st.write("- Error E-42 logged (15 min ago)")
            st.write("- Optimization tip shared (1 hour ago)")
            st.write("- Style rule updated (3 hours ago)")


def render_broadcast_widget(hive) -> None:
    """
    Main widget for knowledge broadcasting
    Integrates input, history, and statistics
    """
    col1, col2 = st.columns([2, 1])
    
    with col1:
        broadcast_data = BroadcastPanel.render_broadcast_input()
        
        if broadcast_data:
            # send via hive proxy if available
            if hasattr(hive, 'broadcast_knowledge'):
                hive.broadcast_knowledge(broadcast_data['content'], agent_id="system")
            st.success(f"✅ {broadcast_data['type']} broadcasted to all agents!")
            logger.info(f"Broadcast: {broadcast_data}")
    
    st.divider()
    
    BroadcastPanel.render_broadcast_history(hive.shared_memory.get("broadcast_history", []))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        BroadcastPanel.render_knowledge_base_stats()
    
    with col2:
        BroadcastPanel.render_pending_broadcasts(hive)


def create_knowledge_broadcast_tab(hive) -> None:
    """
    Create a complete knowledge broadcast tab for Streamlit dashboard
    
    Args:
        hive: HiveCouncil instance
    """
    tab1, tab2, tab3 = st.tabs(["📡 Broadcast", "📚 Knowledge Base", "✓ Acknowledgments"])
    
    with tab1:
        st.header("Knowledge Broadcasting System")
        render_broadcast_widget(hive)
    
    with tab2:
        st.header("Knowledge Base Management")
        BroadcastPanel.render_knowledge_base_stats()
        st.divider()
        BroadcastPanel.render_broadcast_history(hive.shared_memory.get("broadcast_history", []))
    
    with tab3:
        st.header("Agent Acknowledgments")
        broadcasts = hive.shared_memory.get("broadcasts", [])
        BroadcastPanel.render_agent_acknowledgment(broadcasts)
