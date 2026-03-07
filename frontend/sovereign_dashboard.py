"""
🛡️ SOVEREIGN COMMAND CENTER - Complete Streamlit Dashboard
The nerve center for commanding the Muqattaat Research Hive
Integrates: Pattern Web, Meritocracy, Knowledge Broadcast, Execution Control
"""

import streamlit as st
import logging
from datetime import datetime
from pathlib import Path
import os
import sys

# Add parent directory to path so we can import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

# network access for API-based operation
import requests

# Determine whether to use backend API or direct imports
USE_API = os.getenv("USE_API", "false").lower() == "true"
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# Import all components (direct mode)
from src.agents.hive_council import get_hive_council
from src.data.meritocracy_db import get_meritocracy_db
from src.core.langgraph_control import get_graph_controller, get_interrupt_manager
from frontend.components.pattern_web import get_pattern_web_visualizer
from frontend.components.meritocracy_panel import create_meritocracy_tab, MeritocracyPanel
from frontend.components.knowledge_broadcast import create_knowledge_broadcast_tab
from frontend.components.execution_queue import create_execution_queue_tab
from frontend.components.pattern_web import PatternWebVisualizer

# API helpers

def api_get(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"API GET failed {path}: {e}")
        return {}


def api_post(path, data=None, params=None):
    try:
        r = requests.post(f"{API_BASE}{path}", json=data or {}, params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"API POST failed {path}: {e}")
        return {}


logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# API / LOCAL WRAPPERS
# ──────────────────────────────────────────────────────────────────

def _hive():
    # always instantiate hive for direct mode
    return get_hive_council()


class HiveProxy:
    """Proxy object that forwards calls to either the local hive or the REST API"""

    def get_hive_status(self):
        if USE_API:
            return api_get("/status")
        return _hive().get_hive_status()

    def get_leaderboard(self, limit=20):
        return get_leaderboard(limit)

    def get_agent_of_the_day(self):
        return get_agent_of_the_day()

    def calculate_agent_of_the_day(self):
        return recalc_agent_of_day()

    def get_agent_metrics(self, agent_id: str):
        if USE_API:
            return api_get(f"/meritocracy/agent/{agent_id}")
        return _hive().get_agent_metrics(agent_id)

    @property
    def meritocracy_db(self):
        class _DB:
            def get_agent_history(self, agent_id: str, days: int = 30):
                if USE_API:
                    return api_get(f"/meritocracy/agent/{agent_id}/history", params={"days": days}).get("history", [])
                return _hive().meritocracy_db.get_agent_history(agent_id, days)
        return _DB()

    @property
    def shared_memory(self):
        if USE_API:
            return {
                "pending_broadcasts": broadcast_pending(),
                "broadcast_history": broadcast_history(),
                "broadcasts": broadcast_history(),
            }
        return _hive().shared_memory

    @property
    def supervision_reports(self):
        if USE_API:
            # fetch recent reports (limit high to approximate all-time)
            return api_get("/supervisions/recent", params={"limit": 1000}).get("reports", [])
        return _hive().supervision_reports

    def broadcast_knowledge(self, message: str, agent_id: str = "system"):
        if USE_API:
            return broadcast_send(message, agent_id)
        return _hive().broadcast_knowledge(message, agent_id)

    def acknowledge_broadcast(self, broadcast_id: str):
        if USE_API:
            return broadcast_ack(broadcast_id)
        return _hive().acknowledge_broadcast(broadcast_id)


# instantiate a proxy for use throughout the dashboard
hive = HiveProxy()

# Hive wrappers

def get_hive_status():
    if USE_API:
        return api_get("/status")
    return _hive().get_hive_status()


def recalc_agent_of_day():
    if USE_API:
        return api_post("/meritocracy/calculate-agent-of-the-day").get("winner")
    return _hive().calculate_agent_of_the_day()


def save_hive_state():
    if USE_API:
        return api_post("/hive/save")
    return _hive().save_hive_state()


def get_leaderboard(limit=20):
    if USE_API:
        return api_get("/meritocracy/leaderboard", params={"limit": limit}).get("leaderboard", [])
    return _hive().get_leaderboard(limit)


def get_agent_of_the_day():
    if USE_API:
        return api_get("/meritocracy/agent-of-the-day")
    return _hive().get_agent_of_the_day()


def get_all_agents():
    if USE_API:
        return api_get("/meritocracy/all-agents").get("agents", [])
    return _hive().meritocracy_db.get_all_agents()


def export_metrics():
    if USE_API:
        return api_get("/meritocracy/export").get("metrics", {})
    return _hive().meritocracy_db.export_metrics()

# Pattern web wrappers

def pattern_stats():
    if USE_API:
        return api_get("/patterns/stats")
    return pattern_web.get_statistics()


def pattern_queue_status():
    if USE_API:
        return api_get("/patterns/queue")
    return pattern_web.get_queue_status()


def pattern_execute_queue():
    if USE_API:
        return api_post("/patterns/queue/execute")
    return pattern_web.execute_queue()


def pattern_clear_queue():
    if USE_API:
        return api_post("/patterns/queue/clear")
    else:
        pattern_web.execution_queue.clear()
        return {}


# Proxy for pattern_web to route certain methods through API
class PatternWebProxy:
    def __init__(self, real):
        self._real = real

    def get_queue_status(self):
        return pattern_queue_status()

    def execute_queue(self):
        return pattern_execute_queue()

    def add_pattern_to_queue(self, pattern_id):
        if USE_API:
            return api_post(f"/patterns/queue/add/{pattern_id}")
        return self._real.add_pattern_to_queue(pattern_id)

    def __getattr__(self, name):
        # delegate other attributes/methods to the real object
        return getattr(self._real, name)


# Control wrappers

def control_pause_all():
    if USE_API:
        return api_post("/control/pause-all")
    return graph_controller.pause_all()


def control_resume_all():
    if USE_API:
        return api_post("/control/resume-all")
    return graph_controller.resume_all()


def control_status():
    if USE_API:
        return api_get("/control/status")
    return graph_controller.get_status()


def control_pause_node(node_name):
    if USE_API:
        return api_post(f"/control/pause/{node_name}")
    return graph_controller.pause_execution(node_name)


def control_resume_node(node_name):
    if USE_API:
        return api_post(f"/control/resume/{node_name}")
    return graph_controller.resume_execution(node_name)

# Broadcast wrappers

def broadcast_history():
    if USE_API:
        return api_get("/broadcast/history").get("history", [])
    return _hive().broadcast_history


def broadcast_pending():
    if USE_API:
        return api_get("/broadcast/pending").get("pending", [])
    return _hive().get_pending_broadcasts()


def broadcast_send(message, agent_id="system"):
    if USE_API:
        return api_post("/broadcast", data={"content": message, "sender": agent_id, "tipo": "message", "priority": "normal"})
    return _hive().broadcast_knowledge(message, agent_id)


def broadcast_ack(broadcast_id):
    if USE_API:
        return api_post(f"/broadcast/ack/{broadcast_id}")
    return _hive().acknowledge_broadcast(broadcast_id)



# ──────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="🛡️ Sovereign Command Center",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        border: 2px solid #1f77b4;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .sovereign-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# SIDEBAR - HIVE CONTROLS
# ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🛡️ Command Center")
    st.divider()
    
    # Initialize system components
    # hive proxy already created globally (may call API or local)
    meritocracy_db = get_meritocracy_db()
    graph_controller = get_graph_controller()
    interrupt_manager = get_interrupt_manager()
    pattern_web = get_pattern_web_visualizer()
    if USE_API:
        pattern_web = PatternWebProxy(pattern_web)
    
    # Hive Control Section
    st.subheader("🕹️ Hive Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⏸️ PAUSE ALL", use_container_width=True):
            control_pause_all()
            st.success("All agents paused ✓")
    
    with col2:
        if st.button("▶️ RESUME", use_container_width=True):
            control_resume_all()
            st.success("All agents resumed ✓")
    
    st.divider()
    
    # Status Section
    st.subheader("📊 System Status")
    hive_status = get_hive_status()
    
    col1, col2 = st.columns(2)
    col1.metric("Agents", "4", "Active")
    col2.metric("State", graph_controller.execution_state.value.upper(), "")
    
    st.divider()
    
    # Quick Links
    st.subheader("🔗 Quick Links")
    
    if st.button("🔄 Recalculate Agent of the Day"):
        winner = recalc_agent_of_day()
        st.success(f"✅ {winner if winner else 'Calculating...'}")
    
    if st.button("💾 Save Hive State"):
        save_hive_state()
        st.success("Hive state saved ✓")
    
    if st.button("📊 Export Metrics"):
        metrics = export_metrics()
        st.json(metrics)
    
    st.divider()
    
    # System Info
    st.subheader("ℹ️ System Info")
    st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"**Ollama 3.1:** {'✓' if hive_status.get('ollama_enabled') else '✗'}")
    st.write(f"**Database:** {'✓' if hive_status.get('database_connected') else '✗'}")
    st.write(f"**Meritocracy:** ✓")


# ──────────────────────────────────────────────────────────────────
# MAIN CONTENT - TABS
# ──────────────────────────────────────────────────────────────────

st.markdown("""
    <div class="sovereign-header">
        <h1>⚔️ SOVEREIGN COMMAND CENTER</h1>
        <p>The Nerve Center of the Muqattaat Research Hive</p>
    </div>
""", unsafe_allow_html=True)

# Create main tabs
tab_research, tab_meritocracy, tab_knowledge, tab_execution, tab_control, tab_dashboard = st.tabs([
    "🔮 Research Foundry",
    "🏆 Agent Meritocracy",
    "📡 Knowledge Broadcast",
    "📋 Execution Queue",
    "🕹️ System Control",
    "📊 Dashboard"
])

# ──────────────────────────────────────────────────────────────────
# TAB 1: RESEARCH FOUNDRY
# ──────────────────────────────────────────────────────────────────

with tab_research:
    st.header("🔮 Research Foundry")
    st.write("Interactive pattern web with drag-and-drop execution queuing")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("3D Pattern Web")
        st.info("Interactive visualization: patterns cultered by type with force-directed layout")
        
        # Display pattern statistics
        stats = pattern_stats()
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Total Patterns", stats['total_patterns'])
        col_b.metric("Clusters", stats['total_clusters'])
        col_c.metric("Graph Edges", stats['graph_edges'])
        col_d.metric("Queued", stats['queue_size'])
        
        # Search functionality
        st.subheader("Search & Filter")
        search_term = st.text_input("Search patterns by ID or name")
        pattern_type = st.multiselect("Filter by type", ["mathematical", "linguistic", "cryptographic", "phonetic"])
        
        if st.button("🔍 Search"):
            if search_term:
                st.write(f"Found patterns matching: {search_term}")
    
    with col2:
        st.subheader("Execution Queue")
        queue_status = pattern_queue_status()
        st.metric("Queue Size", queue_status['queue_size'])
        
        if st.button("🚀 Execute Queue"):
            result = pattern_execute_queue()
            st.success(f"✅ Executed {len(result.get('executed', []))} patterns")
        
        if st.button("🗑️ Clear Queue"):
            pattern_clear_queue()
            st.info("Queue cleared")


# ──────────────────────────────────────────────────────────────────
# TAB 2: AGENT MERITOCRACY
# ──────────────────────────────────────────────────────────────────

with tab_meritocracy:
    st.header("🏆 Agent Meritocracy System")
    create_meritocracy_tab(hive)


# ──────────────────────────────────────────────────────────────────
# TAB 3: KNOWLEDGE BROADCAST
# ──────────────────────────────────────────────────────────────────

with tab_knowledge:
    st.header("📡 Knowledge Broadcast System")
    create_knowledge_broadcast_tab(hive)


# ──────────────────────────────────────────────────────────────────
# TAB 4: EXECUTION QUEUE
# ──────────────────────────────────────────────────────────────────

with tab_execution:
    st.header("📋 Pattern Execution Queue")
    create_execution_queue_tab(hive, pattern_web)


# ──────────────────────────────────────────────────────────────────
# TAB 5: SYSTEM CONTROL
# ──────────────────────────────────────────────────────────────────

with tab_control:
    st.header("🕹️ System Control & Checkpoints")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏸️ Execution Control")
        
        # Pause/Resume controls
        st.write("**Global Execution State**")
        status = control_status()
        st.metric("Current State", status['execution_state'].upper())
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("⏸️ PAUSE ALL NODES", use_container_width=True):
                control_pause_all()
                st.success("All nodes paused")
        
        with col_b:
            if st.button("▶️ RESUME ALL NODES", use_container_width=True):
                control_resume_all()
                st.success("All nodes resumed")
        
        st.divider()
        
        # Individual node control
        st.write("**Individual Node Control**")
        for node_name, is_paused in status['pause_status'].items():
            col_x, col_y = st.columns([2, 1])
            
            with col_x:
                st.write(f"**{node_name.title()}**")
            
            with col_y:
                if is_paused:
                    if st.button(f"▶️ Resume {node_name}", use_container_width=True):
                        control_resume_node(node_name)
                        st.rerun()
                else:
                    if st.button(f"⏸️ Pause {node_name}", use_container_width=True):
                        control_pause_node(node_name)
    with col2:
        st.subheader("💾 Checkpoint Management")
        
        # Create checkpoint
        st.write("**Create Checkpoint**")
        if st.button("📸 Create Checkpoint", use_container_width=True):
            checkpoint_id = graph_controller.create_checkpoint(
                state_name="manual_checkpoint",
                state_data={"hive_state": get_hive_status()},
                agent_id="system",
                task_id="manual"
            )
            st.success(f"Checkpoint created: {checkpoint_id[:20]}...")
        
        st.divider()
        
        # Restore from checkpoint
        st.write("**Restore from Checkpoint**")
        checkpoints = graph_controller.get_checkpoint_list()
        
        if checkpoints:
            checkpoint_options = {
                c['snapshot_id']: f"{c['state_name']} ({c['timestamp'].split('T')[1][:5]})"
                for c in checkpoints
            }
            
            selected_checkpoint = st.selectbox(
                "Select checkpoint to restore",
                options=list(checkpoint_options.keys()),
                format_func=lambda x: checkpoint_options.get(x, x)
            )
            
            if st.button("🔄 Restore Checkpoint", use_container_width=True):
                restored_state = graph_controller.restore_from_checkpoint(selected_checkpoint)
                st.success("Checkpoint restored")
                st.json(restored_state)
        else:
            st.info("No checkpoints available")
        
        st.divider()
        
        # Interrupts
        st.write("**Workflow Interrupts**")
        pending = interrupt_manager.get_pending_interrupts()
        
        if pending:
            st.warning(f"{len(pending)} pending interrupt(s)")
            for interrupt in pending:
                st.write(f"- {interrupt['node_name']}: {interrupt['reason']}")
        else:
            st.success("No interrupts")


# ──────────────────────────────────────────────────────────────────
# TAB 6: DASHBOARD
# ──────────────────────────────────────────────────────────────────

with tab_dashboard:
    st.header("📊 System Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get current metrics
    leaderboard = hive.get_leaderboard(limit=10)
    aotd = hive.get_agent_of_the_day()
    supervision_stats = None  # Would get from hive
    
    with col1:
        if leaderboard:
            top_agent = leaderboard[0]
            st.metric("Top Agent", top_agent['agent_id'], f"{top_agent['total_credits']:,} 💎")
    
    with col2:
        if aotd and aotd.get('agent_id') != 'None':
            st.metric("Agent of Day", aotd['agent_id'], f"Score: {aotd.get('performance_score', 0):.2f}")
    
    with col3:
        total_agents = len(hive.meritocracy_db.get_all_agents())
        st.metric("Active Agents", total_agents, "In Hive")
    
    with col4:
        st.metric("Supervisions", len(hive.supervision_reports), "All-time")
    
    st.divider()
    
    # Summary panels
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🏆 Top 5 Agents")
        for i, agent in enumerate(leaderboard[:5]):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            st.write(
                f"{medal} {agent['agent_id']}: "
                f"{agent['total_credits']:,} 💎 "
                f"({agent['accuracy_score']:.1f}% accuracy)"
            )
    
    with col_right:
        st.subheader("📈 System Metrics")
        
        hive_metrics = hive.get_hive_status()
        st.metric("Thoughts Logged", hive_metrics.get('total_thoughts_logged', 0))
        st.metric("Supervisions", hive_metrics.get('total_supervisions', 0))
        st.metric("Ollama 3.1 Enabled", "✓" if hive_metrics.get('ollama_enabled') else "✗")
        st.metric("Database Connected", "✓" if hive_metrics.get('database_connected') else "✗")


# ──────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────

st.divider()

col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.write("**System Status**")
    status = graph_controller.get_status()
    st.write(f"State: {status['execution_state'].upper()}")
    st.write(f"Checkpoints: {status['total_checkpoints']}")

with col_footer2:
    st.write("**Last Updated**")
    st.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_footer3:
    st.write("**Quick Actions**")
    if st.button("🔄 Refresh"):
        st.rerun()


logger.info("Sovereign Command Center dashboard loaded")
