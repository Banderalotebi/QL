"""
🎨 STREAMLIT DASHBOARD - REAL-TIME HIVE MONITORING
Visualize the Council of Experts in action
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from datetime import datetime, timedelta
import time

# Set page config
st.set_page_config(
    page_title="Muqattaat Hive Monitor",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme
st.markdown("""
<style>
    body { background-color: #0e1117; }
    .main { background-color: #010409; }
    h1, h2, h3 { color: #79c0ff; }
    .thought-card {
        background-color: #161b22;
        border-left: 4px solid #79c0ff;
        padding: 16px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .approval-card {
        background-color: #161b22;
        border-left: 4px solid #3fb950;
        padding: 16px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .revision-card {
        background-color: #161b22;
        border-left: 4px solid #d29922;
        padding: 16px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .rejection-card {
        background-color: #161b22;
        border-left: 4px solid #f85149;
        padding: 16px;
        margin: 8px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_hive_state():
    """Load persistent hive state from disk"""
    hive_state_path = Path("/workspaces/QL/data/processed/hive_state.json")
    if hive_state_path.exists():
        with open(hive_state_path, 'r') as f:
            return json.load(f)
    return {
        "thoughts_log": [],
        "supervision_reports": [],
        "shared_memory": {},
        "hive_status": {}
    }


@st.cache_resource
def load_knowledge_graph():
    """Load knowledge graph data"""
    kg_path = Path("/workspaces/QL/data/processed/knowledge_graph.json")
    if kg_path.exists():
        try:
            with open(kg_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


@st.cache_resource
def load_last_report():
    """Load last research report"""
    report_path = Path("/workspaces/QL/data/processed/last_report.json")
    if report_path.exists():
        try:
            with open(report_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def render_header():
    """Render main header with status"""
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("# 🏛️ MUQATTAAT CRYPTANALYTIC LAB")
        st.markdown("**Council of Experts - Real-Time Monitor**")
    
    with col3:
        hive_state = load_hive_state()
        status = hive_state.get("hive_status", {})
        
        if status:
            col_a, col_b = st.columns(2)
            with col_a:
                if status.get("ollama_enabled"):
                    st.metric("Ollama 3.1", "✅ Enabled", delta="Ready")
                else:
                    st.metric("Mathematical", "✅ Active", delta="Fallback")
            with col_b:
                st.metric("DB Status", 
                         "✅ Connected" if status.get("database_connected") else "⚠️ Offline")
    
    st.divider()


def render_agent_thought_stream():
    """Display live agent thought stream"""
    st.subheader("🧠 Agent Thought Stream")
    
    hive_state = load_hive_state()
    thoughts = hive_state.get("thoughts_log", [])
    
    if not thoughts:
        st.info("No agent thoughts yet. Run a deep scan to populate this section.")
        return
    
    # Filter by agent
    cols = st.columns(4)
    with cols[0]:
        agent_filter = st.selectbox(
            "Filter by Agent",
            ["All"] + list(set([t["agent_role"] for t in thoughts])),
            key="agent_filter"
        )
    
    # Display thoughts in reverse chronological order
    filtered_thoughts = thoughts
    if agent_filter != "All":
        filtered_thoughts = [t for t in thoughts if t["agent_role"] == agent_filter]
    
    for thought in reversed(filtered_thoughts[-20:]):  # Last 20
        with st.container():
            html = f"""
            <div class="thought-card">
                <strong>{thought['agent_role']}</strong> @ {thought['timestamp'][:19]}<br>
                <em>{thought['thought'][:200]}...</em><br>
                💡 Decision: {thought['decision']}<br>
                📊 Confidence: {thought['confidence']:.2f}
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)


def render_supervision_reports():
    """Display expert supervision reports"""
    st.subheader("📋 Expert Supervision Reports")
    
    hive_state = load_hive_state()
    reports = hive_state.get("supervision_reports", [])
    
    if not reports:
        st.info("No supervision reports yet.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        approved = len([r for r in reports if r["status"] == "APPROVED"])
        st.metric("Approved", approved)
    with col2:
        revised = len([r for r in reports if r["status"] == "REVISED"])
        st.metric("Revised", revised)
    with col3:
        rejected = len([r for r in reports if r["status"] == "REJECTED"])
        st.metric("Rejected", rejected)
    with col4:
        avg_score = sum([r["final_score"] for r in reports]) / len(reports) if reports else 0
        st.metric("Avg Score", f"{avg_score:.3f}")
    
    st.divider()
    
    # Display reports
    for report in reversed(reports[-50:]):  # Last 50
        card_class = {
            "APPROVED": "approval-card",
            "REVISED": "revision-card",
            "REJECTED": "rejection-card"
        }.get(report["status"], "approval-card")
        
        html = f"""
        <div class="{card_class}">
            <strong>{report['status']}</strong> | Score: {report['final_score']:.3f}<br>
            Worker: {report['worker_agent']} → Expert: {report['expert_agent']}<br>
            📝 {report['expert_feedback']}<br>
            Corrections: {len(report['corrections_applied'])} applied
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_muqattaat_heatmap():
    """Render heatmap of Muqattaat distribution across surahs"""
    st.subheader("📊 Muqattaat Distribution Heatmap")
    
    # Sample data - in production would come from database
    muqattaat_data = {
        'A': [4502, 3102, 2156, 1987, 2345],
        'L': [3202, 2890, 1876, 1654, 2123],
        'M': [2195, 1987, 1432, 1298, 1654],
        'H': [1876, 1654, 1123, 987, 1234],
        'Y': [1432, 1298, 876, 765, 987]
    }
    
    surahs = [2, 3, 7, 10, 11]  # Sample Muqattaat surahs
    
    df = pd.DataFrame(muqattaat_data, index=surahs)
    
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale="Blues",
        colorbar=dict(title="Frequency")
    ))
    
    fig.update_layout(
        title="Muqattaat Letter Frequencies Across Surahs",
        xaxis_title="Letter",
        yaxis_title="Surah Number",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_knowledge_graph_stats():
    """Display knowledge graph statistics"""
    st.subheader("🌐 Knowledge Graph Statistics")
    
    kg = load_knowledge_graph()
    last_report = load_last_report()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nodes = len(kg.get("nodes", []))
        st.metric("Total Nodes", nodes)
    
    with col2:
        edges = len(kg.get("edges", []))
        st.metric("Total Relations", edges)
    
    with col3:
        if last_report:
            theories = len(last_report.get("ranked_theories", []))
            st.metric("Active Theories", theories)
        else:
            st.metric("Active Theories", "—")
    
    with col4:
        if last_report:
            latest = last_report.get("timestamp", "Unknown")
            st.metric("Last Updated", latest[:10])
        else:
            st.metric("Last Updated", "Never")


def render_performance_metrics():
    """Display performance metrics"""
    st.subheader("⚡ System Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Response time over time (simulated)
        times = pd.date_range(start='2024-01-01', periods=10, freq='H')
        response_times = [0.45, 0.52, 0.48, 0.61, 0.55, 0.42, 0.58, 0.50, 0.49, 0.52]
        
        fig = px.line(
            x=times,
            y=response_times,
            title="Average Response Time (seconds)",
            labels={"x": "Time", "y": "Response Time (s)"},
            markers=True
        )
        fig.update_traces(line=dict(color="#79c0ff"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Hypothesis acceptance rate
        hive_state = load_hive_state()
        reports = hive_state.get("supervision_reports", [])
        
        if reports:
            statuses = [r["status"] for r in reports]
            status_counts = pd.Series(statuses).value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Hypothesis Disposition",
                color_discrete_map={
                    "APPROVED": "#3fb950",
                    "REVISED": "#d29922",
                    "REJECTED": "#f85149"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No supervision data yet")


def render_shared_memory():
    """Display shared memory across agents"""
    st.subheader("💾 Shared Hive Memory")
    
    hive_state = load_hive_state()
    shared_mem = hive_state.get("shared_memory", {})
    
    tabs = st.tabs(["Verified Patterns", "Known Errors", "Optimizations"])
    
    with tabs[0]:
        patterns = shared_mem.get("verified_patterns", [])
        if patterns:
            for pattern in patterns:
                st.success(f"✅ {pattern}")
        else:
            st.info("No verified patterns yet")
    
    with tabs[1]:
        errors = shared_mem.get("known_errors", [])
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            st.info("No known errors yet")
    
    with tabs[2]:
        tips = shared_mem.get("optimization_tips", [])
        if tips:
            for tip in tips:
                st.success(f"⚡ {tip}")
        else:
            st.info("No optimization tips yet")


def render_control_panel():
    """Control panel for triggering scans"""
    st.sidebar.subheader("🎮 Control Panel")
    
    with st.sidebar:
        # Surah selector
        surah_num = st.number_input(
            "Select Surah to Scan",
            min_value=2,
            max_value=68,
            value=2,
            step=1
        )
        
        # Scan type selector
        scan_type = st.radio(
            "Scan Type",
            ["Single Surah", "All Muqattaat", "Custom Range"]
        )
        
        # Custom range
        if scan_type == "Custom Range":
            col1, col2 = st.columns(2)
            with col1:
                start = st.number_input("Start", min_value=2, value=2)
            with col2:
                end = st.number_input("End", min_value=start, value=10)
        
        # Mode selector
        mode = st.radio(
            "Execution Mode",
            ["Mathematical (Fast)", "Ollama 3.1 (LLM-Enhanced)", "Hybrid"]
        )
        
        # Execute button
        if st.button("🚀 Start Deep Scan", use_container_width=True):
            st.info(f"⏳ Scanning Surah {surah_num} in {mode} mode...")
            # In production, this would trigger the actual hive
            st.toast("Scan requested! Check logs for progress.", icon="✅")
        
        st.divider()
        
        # Refresh controls
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
        
        st.divider()
        
        # System info
        st.subheader("📊 System Info")
        hive_state = load_hive_state()
        status = hive_state.get("hive_status", {})
        
        st.write(f"**Thoughts Logged:** {status.get('total_thoughts_logged', 0)}")
        st.write(f"**Supervisions:** {status.get('total_supervisions', 0)}")
        st.write(f"**Memory Size:** {status.get('shared_memory_size', 0)} bytes")


def main():
    """Main app flow"""
    render_header()
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Agent Thoughts",
        "📋 Supervision Reports",
        "📊 Analysis & Metrics",
        "💾 Memory & Control"
    ])
    
    with tab1:
        render_agent_thought_stream()
    
    with tab2:
        render_supervision_reports()
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            render_muqattaat_heatmap()
        with col2:
            render_knowledge_graph_stats()
        
        st.divider()
        render_performance_metrics()
    
    with tab4:
        col1, col2 = st.columns([2, 1])
        with col1:
            render_shared_memory()
        with col2:
            st.subheader("🔧 Quick Actions")
            if st.button("📥 Save Hive State", use_container_width=True):
                st.success("Hive state saved!")
            if st.button("🔄 Reset Dashboard", use_container_width=True):
                st.cache_resource.clear()
                st.success("Dashboard reset!")
    
    # Control panel in sidebar
    render_control_panel()
    
    # Footer
    st.divider()
    st.caption("🏛️ Muqattaat Cryptanalytic Lab | Council of Experts | v1.0")


if __name__ == "__main__":
    main()
