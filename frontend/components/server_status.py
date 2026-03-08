"""
🖥️ SERVER STATUS COMPONENT - Real-Time Service Monitoring
Shows status of all Hive Lab services: API, Dashboard, Continuous Hive, Database
"""

import streamlit as st
import requests
import psutil
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


# Service configuration
API_BASE = "http://localhost:8000"
API_PORT = 8000
DASHBOARD_PORT = 8501
HIVE_PID_FILE = "/workspaces/QL/.hive_pid"
HIVE_LOG_DIR = "/workspaces/QL/logs"


def check_port_in_use(port: int) -> bool:
    """Check if a port is currently in use"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False


def get_process_info(pid: int) -> Optional[Dict[str, Any]]:
    """Get detailed process information"""
    try:
        process = psutil.Process(pid)
        return {
            "pid": process.pid,
            "name": process.name(),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "create_time": datetime.fromtimestamp(process.create_time()),
            "num_threads": process.num_threads(),
            "cmdline": " ".join(process.cmdline()[:3]) if process.cmdline() else "N/A"
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def get_hive_process_info() -> Optional[Dict[str, Any]]:
    """Get information about the running Hive process"""
    pid_file = Path(HIVE_PID_FILE)
    if not pid_file.exists():
        return None
    
    try:
        pid = int(pid_file.read_text().strip())
        return get_process_info(pid)
    except (ValueError, FileNotFoundError):
        return None


def get_uptime(start_time: datetime) -> str:
    """Calculate and format uptime"""
    delta = datetime.now() - start_time
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"


def check_api_status() -> Dict[str, Any]:
    """Check API server status"""
    try:
        response = requests.get(f"{API_BASE}/system/health", timeout=2)
        if response.status_code == 200:
            return {
                "status": "running",
                "response_time": response.elapsed.total_seconds(),
                "details": response.json()
            }
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        return {"status": "timeout", "response_time": 5.0}
    
    return {"status": "stopped", "response_time": None}


def check_database_status() -> Dict[str, Any]:
    """Check database connection status"""
    try:
        response = requests.get(f"{API_BASE}/system/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            db_status = data.get("components", {}).get("hive_council", "")
            return {
                "status": "connected" if "operational" in db_status else "disconnected",
                "details": db_status
            }
    except:
        pass
    
    return {"status": "unknown"}


def get_service_status(service_name: str) -> Dict[str, Any]:
    """Get status for a specific service"""
    status = {"name": service_name, "status": "stopped", "details": {}}
    
    if service_name == "API Server":
        status["port"] = API_PORT
        api_check = check_api_status()
        status["status"] = api_check.get("status", "stopped")
        status["response_time"] = api_check.get("response_time")
        if api_check.get("details"):
            status["details"] = api_check["details"]
    
    elif service_name == "Streamlit Dashboard":
        status["port"] = DASHBOARD_PORT
        status["status"] = "running" if check_port_in_use(DASHBOARD_PORT) else "stopped"
    
    elif service_name == "Continuous Hive":
        hive_info = get_hive_process_info()
        if hive_info:
            status["status"] = "running"
            status["pid"] = hive_info["pid"]
            status["uptime"] = get_uptime(hive_info["create_time"])
            status["cpu_percent"] = hive_info["cpu_percent"]
            status["memory_mb"] = hive_info["memory_mb"]
            status["details"] = hive_info
        else:
            status["status"] = "stopped"
    
    elif service_name == "Database":
        db_check = check_database_status()
        status["status"] = db_check.get("status", "unknown")
        status["details"] = db_check.get("details", "")
    
    return status


def get_latest_hive_logs(lines: int = 50) -> List[str]:
    """Get latest lines from Hive log"""
    log_dir = Path(HIVE_LOG_DIR)
    if not log_dir.exists():
        return []
    
    log_files = list(log_dir.glob("hive_*.log"))
    if not log_files:
        return []
    
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    try:
        with open(latest_log, 'r') as f:
            all_lines = f.readlines()
            return [line.strip() for line in all_lines[-lines:]]
    except Exception:
        return []


def render_server_status_panel():
    """Render the main server status panel"""
    st.subheader("🖥️ Server Status")
    
    # Services to check
    services = ["API Server", "Streamlit Dashboard", "Continuous Hive", "Database"]
    
    # Get status for all services
    service_statuses = {}
    for service in services:
        service_statuses[service] = get_service_status(service)
    
    # Display status cards
    cols = st.columns(4)
    
    for idx, (service, status) in enumerate(service_statuses.items()):
        with cols[idx]:
            # Status indicator
            if status["status"] == "running":
                status_icon = "🟢"
                status_color = "green"
            elif status["status"] == "connected":
                status_icon = "🟢"
                status_color = "green"
            elif status["status"] == "timeout":
                status_icon = "🟡"
                status_color = "yellow"
            else:
                status_icon = "🔴"
                status_color = "red"
            
            st.markdown(f"""
            <div style="
                padding: 10px; 
                border-radius: 5px; 
                background-color: #1e1e1e;
                border-left: 4px solid {status_color};
                margin-bottom: 10px;
            ">
                <strong>{status_icon} {service}</strong><br>
                <small>Status: {status['status'].upper()}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Show additional details
            if service == "API Server" and status.get("response_time"):
                st.metric("Response Time", f"{status['response_time']*1000:.0f}ms")
            
            if service == "Continuous Hive" and status.get("status") == "running":
                st.metric("CPU", f"{status.get('cpu_percent', 0):.1f}%")
                st.metric("Memory", f"{status.get('memory_mb', 0):.1f} MB")
                st.caption(f"Uptime: {status.get('uptime', 'N/A')}")
                st.caption(f"PID: {status.get('pid', 'N/A')}")
            
            if service == "Database":
                st.caption(status.get("details", ""))


def render_process_details():
    """Render detailed process information"""
    st.divider()
    st.subheader("⚙️ Process Details")
    
    hive_info = get_hive_process_info()
    
    if hive_info:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PID", hive_info["pid"])
        with col2:
            st.metric("Threads", hive_info["num_threads"])
        with col3:
            st.metric("Memory", f"{hive_info['memory_mb']:.1f} MB")
        with col4:
            st.metric("CPU", f"{hive_info['cpu_percent']:.1f}%")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status", hive_info["status"])
        with col2:
            st.metric("Uptime", get_uptime(hive_info["create_time"]))
        
        with st.expander("View Process Command"):
            st.code(hive_info.get("cmdline", "N/A"))
    else:
        st.info("No Hive process currently running")


def render_log_viewer():
    """Render log viewer section"""
    st.divider()
    st.subheader("📋 Live Hive Logs")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        num_lines = st.selectbox("Lines", [20, 50, 100, 200], index=1)
    
    with col2:
        if st.button("🔄 Refresh Logs"):
            st.rerun()
    
    logs = get_latest_hive_logs(num_lines)
    
    if logs:
        st.text_area(
            "Log Output",
            "\n".join(logs),
            height=300,
            disabled=True
        )
    else:
        st.info("No logs available")


def render_control_buttons():
    """Render service control buttons"""
    st.divider()
    st.subheader("🎮 Service Control")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        hive_info = get_hive_process_info()
        if hive_info:
            if st.button("⏹️ Stop Hive", use_container_width=True):
                try:
                    os.kill(hive_info["pid"], 9)
                    st.success("Hive stopped!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            if st.button("🚀 Start Hive", use_container_width=True):
                import subprocess
                subprocess.Popen(
                    ["bash", "/workspaces/QL/start_hive.sh"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                st.success("Hive starting...")
                time.sleep(2)
                st.rerun()
    
    with col2:
        if st.button("📊 Monitor Hive", use_container_width=True):
            st.info("Use terminal: ./monitor_hive.sh")
    
    with col3:
        if st.button("💾 Save State", use_container_width=True):
            try:
                requests.post(f"{API_BASE}/hive/save", timeout=5)
                st.success("State saved!")
            except:
                st.error("API not available")
    
    with col4:
        if st.button("🔄 Restart All", use_container_width=True):
            st.warning("Restarting services...")


def create_server_status_tab():
    """Create the complete server status tab"""
    st.header("🖥️ Server Status & Control")
    
    # Main status panel
    render_server_status_panel()
    
    # Process details
    render_process_details()
    
    # Control buttons
    render_control_buttons()
    
    # Log viewer
    render_log_viewer()


# For standalone testing
if __name__ == "__main__":
    import streamlit as st
    
    st.set_page_config(page_title="Server Status Test", layout="wide")
    st.title("Server Status Component Test")
    
    create_server_status_tab()

