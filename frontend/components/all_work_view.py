"""
📋 ALL WORK VIEW COMPONENT - Comprehensive Research History
Shows all past research runs, supervisions, findings, and broadcasts
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


# Data paths
HIVE_STATE_PATH = Path("/workspaces/QL/data/processed/hive_state.json")
HIVE_MEMORY_PATH = Path("/workspaces/QL/data/processed/hive_memory.json")
KNOWLEDGE_GRAPH_PATH = Path("/workspaces/QL/data/processed/knowledge_graph.json")
LAST_REPORT_PATH = Path("/workspaces/QL/data/processed/last_report.json")


def load_hive_state() -> Dict[str, Any]:
    """Load hive state from disk"""
    if HIVE_STATE_PATH.exists():
        try:
            with open(HIVE_STATE_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_hive_memory() -> Dict[str, Any]:
    """Load hive memory from disk"""
    if HIVE_MEMORY_PATH.exists():
        try:
            with open(HIVE_MEMORY_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_knowledge_graph() -> Dict[str, Any]:
    """Load knowledge graph from disk"""
    if KNOWLEDGE_GRAPH_PATH.exists():
        try:
            with open(KNOWLEDGE_GRAPH_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_last_report() -> Dict[str, Any]:
    """Load last research report"""
    if LAST_REPORT_PATH.exists():
        try:
            with open(LAST_REPORT_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def render_all_work_header():
    """Render header for All Work view"""
    st.header("📋 All Work - Complete Research History")
    st.write("View all research runs, supervision reports, findings, and broadcasts")


def render_research_runs():
    """Render all research runs section"""
    st.subheader("🔬 Research Runs")
    
    last_report = load_last_report()
    
    if last_report:
        # Display summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            theories = last_report.get("ranked_theories", [])
            st.metric("Total Theories", len(theories))
        
        with col2:
            st.metric("Timestamp", last_report.get("timestamp", "N/A")[:10])
        
        with col3:
            st.metric("Surahs Analyzed", len(last_report.get("surah_numbers", [])))
        
        with col4:
            st.metric("Focus", last_report.get("focus", "N/A"))
        
        # Show top theories
        with st.expander("View Top Theories"):
            for i, theory in enumerate(theories[:20], 1):
                st.write(f"{i}. **{theory.get('source_scout', 'Unknown')}** - Score: {theory.get('score', 0):.3f}")
                st.caption(f"Goal: {theory.get('goal_link', 'N/A')[:80]}...")
    else:
        st.info("No research runs recorded yet")


def render_supervision_reports():
    """Render all supervision reports section"""
    st.divider()
    st.subheader("📋 Supervision Reports")
    
    hive_state = load_hive_state()
    reports = hive_state.get("supervision_reports", [])
    
    if reports:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        approved = len([r for r in reports if r.get("status") == "APPROVED"])
        revised = len([r for r in reports if r.get("status") == "REVISED"])
        rejected = len([r for r in reports if r.get("status") == "REJECTED"])
        
        with col1:
            st.metric("Total Reports", len(reports))
        with col2:
            st.metric("Approved", approved)
        with col3:
            st.metric("Revised", revised)
        with col4:
            st.metric("Rejected", rejected)
        
        # Filter by status
        status_filter = st.multiselect(
            "Filter by Status",
            ["APPROVED", "REVISED", "REJECTED"],
            default=["APPROVED", "REVISED", "REJECTED"]
        )
        
        filtered_reports = [r for r in reports if r.get("status") in status_filter]
        
        # Display reports
        for report in filtered_reports[-50:]:  # Last 50
            status = report.get("status", "UNKNOWN")
            
            if status == "APPROVED":
                color = "green"
                icon = "✅"
            elif status == "REVISED":
                color = "yellow"
                icon = "📝"
            else:
                color = "red"
                icon = "❌"
            
            st.markdown(f"""
            <div style="
                padding: 10px; 
                border-radius: 5px; 
                background-color: #161b22;
                border-left: 4px solid {color};
                margin: 5px 0;
            ">
                <strong>{icon} {status}</strong> | Score: {report.get('final_score', 0):.3f}<br>
                Worker: {report.get('worker_agent', 'N/A')} → Expert: {report.get('expert_agent', 'N/A')}<br>
                <small>{report.get('expert_feedback', 'No feedback')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No supervision reports yet")


def render_agent_thoughts():
    """Render all agent thoughts section"""
    st.divider()
    st.subheader("🧠 Agent Thoughts")
    
    hive_state = load_hive_state()
    thoughts = hive_state.get("thoughts_log", [])
    
    if thoughts:
        st.metric("Total Thoughts", len(thoughts))
        
        # Filter by agent
        agents = list(set([t.get("agent_role", "Unknown") for t in thoughts]))
        agent_filter = st.multiselect("Filter by Agent", agents, default=agents)
        
        filtered_thoughts = [t for t in thoughts if t.get("agent_role") in agent_filter]
        
        # Display thoughts
        for thought in filtered_thoughts[-30:]:  # Last 30
            st.markdown(f"""
            <div style="
                padding: 10px; 
                border-radius: 5px; 
                background-color: #1e1e1e;
                margin: 5px 0;
            ">
                <strong>{thought.get('agent_role', 'Unknown')}</strong> @ {thought.get('timestamp', 'N/A')[:19]}<br>
                <em>{thought.get('thought', 'N/A')[:150]}...</em><br>
                💡 Decision: {thought.get('decision', 'N/A')} | Confidence: {thought.get('confidence', 0):.2f}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No agent thoughts logged yet")


def render_knowledge_graph():
    """Render knowledge graph findings section"""
    st.divider()
    st.subheader("🌐 Knowledge Graph Findings")
    
    kg = load_knowledge_graph()
    
    if kg:
        nodes = kg.get("nodes", [])
        edges = kg.get("edges", [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Nodes", len(nodes))
        with col2:
            st.metric("Total Edges", len(edges))
        
        # Display nodes
        with st.expander(f"View {len(nodes)} Nodes"):
            for node in nodes[:50]:  # First 50
                st.write(f"• {node.get('id', 'N/A')} - Type: {node.get('type', 'Unknown')}")
        
        # Display edges
        with st.expander(f"View {len(edges)} Edges"):
            for edge in edges[:50]:  # First 50
                st.write(f"• {edge.get('source', 'N/A')} → {edge.get('target', 'N/A')}")
    else:
        st.info("No knowledge graph data yet")


def render_broadcast_history():
    """Render broadcast history section"""
    st.divider()
    st.subheader("📡 Knowledge Broadcasts")
    
    hive_memory = load_hive_memory()
    broadcasts = hive_memory.get("broadcast_history", [])
    
    if broadcasts:
        st.metric("Total Broadcasts", len(broadcasts))
        
        # Filter by priority
        priorities = list(set([b.get("priority", "normal") for b in broadcasts]))
        priority_filter = st.multiselect("Filter by Priority", priorities, default=priorities)
        
        filtered_broadcasts = [b for b in broadcasts if b.get("priority") in priority_filter]
        
        for broadcast in filtered_broadcasts[-30:]:  # Last 30
            priority = broadcast.get("priority", "normal")
            
            if priority == "high":
                color = "red"
                icon = "🔴"
            elif priority == "normal":
                color = "blue"
                icon = "🔵"
            else:
                color = "gray"
                icon = "⚪"
            
            st.markdown(f"""
            <div style="
                padding: 10px; 
                border-radius: 5px; 
                background-color: #1e1e1e;
                border-left: 4px solid {color};
                margin: 5px 0;
            ">
                <strong>{icon} {broadcast.get('type', 'Message')}</strong> | Priority: {priority}<br>
                {broadcast.get('content', 'N/A')[:100]}...<br>
                <small>From: {broadcast.get('sender', 'Unknown')} @ {broadcast.get('timestamp', 'N/A')[:19]}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No broadcasts yet")


def render_shared_memory():
    """Render shared memory section"""
    st.divider()
    st.subheader("💾 Shared Memory")
    
    hive_memory = load_hive_memory()
    
    if hive_memory:
        # Verified Patterns
        patterns = hive_memory.get("verified_patterns", [])
        with st.expander(f"✅ Verified Patterns ({len(patterns)})"):
            if patterns:
                for pattern in patterns:
                    st.success(f"✓ {pattern}")
            else:
                st.info("No verified patterns")
        
        # Known Errors
        errors = hive_memory.get("known_errors", [])
        with st.expander(f"❌ Known Errors ({len(errors)})"):
            if errors:
                for error in errors:
                    st.error(f"✗ {error}")
            else:
                st.info("No known errors")
        
        # Optimization Tips
        tips = hive_memory.get("optimization_tips", [])
        with st.expander(f"⚡ Optimization Tips ({len(tips)})"):
            if tips:
                for tip in tips:
                    st.info(f"💡 {tip}")
            else:
                st.info("No optimization tips")
        
        # Pending Broadcasts
        pending = hive_memory.get("pending_broadcasts", [])
        with st.expander(f"📨 Pending Broadcasts ({len(pending)})"):
            if pending:
                for p in pending:
                    st.write(f"• {p.get('content', 'N/A')[:80]}...")
            else:
                st.info("No pending broadcasts")
    else:
        st.info("No shared memory data")


def render_hive_status():
    """Render hive status section"""
    st.divider()
    st.subheader("🏛️ Hive Status")
    
    hive_state = load_hive_state()
    status = hive_state.get("hive_status", {})
    
    if status:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ollama Enabled", "✓" if status.get("ollama_enabled") else "✗")
        with col2:
            st.metric("Database", "✓" if status.get("database_connected") else "✗")
        with col3:
            st.metric("Thoughts Logged", status.get("total_thoughts_logged", 0))
        with col4:
            st.metric("Supervisions", status.get("total_supervisions", 0))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Memory Size", f"{status.get('shared_memory_size', 0)} bytes")
        with col2:
            st.metric("Timestamp", status.get("timestamp", "N/A")[:19])
    else:
        st.info("No hive status available")


def create_all_work_tab():
    """Create the complete All Work tab"""
    render_all_work_header()
    
    # Research Runs
    render_research_runs()
    
    # Supervision Reports
    render_supervision_reports()
    
    # Agent Thoughts
    render_agent_thoughts()
    
    # Knowledge Graph
    render_knowledge_graph()
    
    # Broadcasts
    render_broadcast_history()
    
    # Shared Memory
    render_shared_memory()
    
    # Hive Status
    render_hive_status()


# For standalone testing
if __name__ == "__main__":
    import streamlit as st
    
    st.set_page_config(page_title="All Work View Test", layout="wide")
    st.title("All Work View Component Test")
    
    create_all_work_tab()

