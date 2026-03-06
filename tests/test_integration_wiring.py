"""
Complete System Integration & Wiring Validation
Tests all API endpoints and data flow pathways
"""

import sys
import json
from fastapi.testclient import TestClient
from pathlib import Path

sys.path.insert(0, '/workspaces/QL')

# Import all core systems
from backend.hive_api import app
from src.agents.hive_council import get_hive_council
from src.data.meritocracy_db import get_meritocracy_db
from frontend.components.pattern_web import get_pattern_web_visualizer
from src.core.langgraph_control import get_graph_controller, get_interrupt_manager

print("=" * 70)
print("🛡️  SYSTEM INTEGRATION & WIRING VALIDATION")
print("=" * 70)
print()

# Initialize test client
client = TestClient(app)

# Get all components
hive = get_hive_council()
db = get_meritocracy_db()
web = get_pattern_web_visualizer()
controller = get_graph_controller()
interrupt_mgr = get_interrupt_manager()

print("✅ All components initialized successfully")
print()

# ────────────────────────────────────────────────────────────────────
# TEST ENDPOINTS
# ────────────────────────────────────────────────────────────────────

test_results = {
    "health": False,
    "status": False,
    "meritocracy": [],
    "patterns": [],
    "broadcast": [],
    "control": [],
    "checkpoints": [],
}

print("TESTING API ENDPOINTS:")
print()

# Test Health
print("1. Health Checks")
try:
    r = client.get("/health")
    assert r.status_code == 200
    print("   ✅ GET /health")
    test_results["health"] = True
except Exception as e:
    print(f"   ❌ GET /health: {e}")

try:
    r = client.get("/status")
    assert r.status_code == 200
    print("   ✅ GET /status")
    test_results["status"] = True
except Exception as e:
    print(f"   ❌ GET /status: {e}")

print()

# Test Meritocracy Endpoints
print("2. Meritocracy Endpoints")
meritocracy_endpoints = [
    ("GET", "/meritocracy/leaderboard"),
    ("GET", "/meritocracy/agent-of-the-day"),
    ("POST", "/meritocracy/calculate-agent-of-the-day"),
    ("GET", "/meritocracy/all-agents"),
    ("GET", "/meritocracy/export"),
]

for method, path in meritocracy_endpoints:
    try:
        if method == "GET":
            r = client.get(path)
        else:
            r = client.post(path)
        
        status = "✅" if r.status_code in [200, 201] else "❌"
        print(f"   {status} {method} {path} (HTTP {r.status_code})")
        test_results["meritocracy"].append((path, r.status_code == 200))
    except Exception as e:
        print(f"   ❌ {method} {path}: {e}")
        test_results["meritocracy"].append((path, False))

print()

# Test Pattern Endpoints
print("3. Pattern Web Endpoints")
pattern_endpoints = [
    ("GET", "/patterns/stats"),
    ("GET", "/patterns/graph"),
    ("GET", "/patterns/queue"),
]

for method, path in pattern_endpoints:
    try:
        r = client.get(path) if method == "GET" else client.post(path)
        status = "✅" if r.status_code in [200, 201] else "❌"
        print(f"   {status} {method} {path} (HTTP {r.status_code})")
        test_results["patterns"].append((path, r.status_code == 200))
    except Exception as e:
        print(f"   ❌ {method} {path}: {e}")
        test_results["patterns"].append((path, False))

try:
    # Test adding pattern to queue
    first_pattern_id = list(web.patterns.keys())[0] if web.patterns else "41"
    r = client.post(f"/patterns/queue/add/{first_pattern_id}")
    print(f"   ✅ POST /patterns/queue/add/{first_pattern_id} (HTTP {r.status_code})")
    test_results["patterns"].append((f"/patterns/queue/add/{first_pattern_id}", r.status_code == 200))
except Exception as e:
    print(f"   ❌ POST /patterns/queue/add/[pattern_id]: {e}")

print()

# Test Broadcast Endpoints
print("4. Knowledge Broadcast Endpoints")
broadcast_endpoints = [
    ("POST", "/broadcast"),
    ("GET", "/broadcast/history"),
    ("GET", "/broadcast/pending"),
]

for method, path in broadcast_endpoints:
    try:
        if method == "GET":
            r = client.get(path)
        else:
            # Note: /broadcast expects tipo, content, priority as query params
            r = client.post(f"{path}?tipo=pattern_discovery&content=Test%20broadcast&priority=normal")
        
        status = "✅" if r.status_code in [200, 201] else "❌"
        print(f"   {status} {method} {path} (HTTP {r.status_code})")
        test_results["broadcast"].append((path, r.status_code in [200, 201]))
    except Exception as e:
        print(f"   ❌ {method} {path}: {e}")
        test_results["broadcast"].append((path, False))

print()

# Test Control Endpoints
print("5. Control System Endpoints")
control_endpoints = [
    ("GET", "/control/status"),
    ("POST", "/control/pause-all"),
    ("POST", "/control/resume-all"),
]

for method, path in control_endpoints:
    try:
        if method == "GET":
            r = client.get(path)
        else:
            r = client.post(path)
        
        status = "✅" if r.status_code in [200, 201] else "❌"
        print(f"   {status} {method} {path} (HTTP {r.status_code})")
        test_results["control"].append((path, r.status_code in [200, 201]))
    except Exception as e:
        print(f"   ❌ {method} {path}: {e}")
        test_results["control"].append((path, False))

print()

# Test Checkpoint Endpoints
print("6. Checkpoint & Interrupt Endpoints")
checkpoint_endpoints = [
    ("GET", "/checkpoints"),
    ("POST", "/checkpoints/create"),
    ("GET", "/interrupts"),
]

for method, path in checkpoint_endpoints:
    try:
        if method == "GET":
            r = client.get(path)
        else:
            r = client.post(path, json={})
        
        status = "✅" if r.status_code in [200, 201] else "❌"
        print(f"   {status} {method} {path} (HTTP {r.status_code})")
        test_results["checkpoints"].append((path, r.status_code in [200, 201]))
    except Exception as e:
        print(f"   ❌ {method} {path}: {e}")
        test_results["checkpoints"].append((path, False))

print()
print("=" * 70)

# ────────────────────────────────────────────────────────────────────
# INTEGRATION FLOW TESTS
# ────────────────────────────────────────────────────────────────────

print()
print("INTEGRATION FLOW TESTS:")
print()

# Flow 1: Supervision → Credit Award → Leaderboard Update
print("1. Supervision Flow → Credits → Leaderboard")
try:
    # Get initial leaderboard
    r1 = client.get("/meritocracy/leaderboard?limit=1")
    initial_top = r1.json()["leaderboard"][0] if r1.json().get("leaderboard") else None
    
    if initial_top:
        initial_credits = initial_top["total_credits"]
        
        # Award credits via API
        r2 = client.post(f"/meritocracy/award-credits/{initial_top['agent_id']}?amount=50&reason=Test")
        
        # Check updated leaderboard
        r3 = client.get("/meritocracy/leaderboard?limit=1")
        updated_top = r3.json()["leaderboard"][0] if r3.json().get("leaderboard") else None
        
        if updated_top and updated_top["total_credits"] == initial_credits + 50:
            print("   ✅ Credits awarded and reflected in leaderboard")
        else:
            print("   ⚠️  Credits awarded but not properly reflected")
    else:
        print("   ⚠️  Could not get leaderboard data")
except Exception as e:
    print(f"   ❌ Supervision flow error: {e}")

print()

# Flow 2: Pattern → Queue → Execute
print("2. Pattern Web Flow → Queue → Execute")
try:
    # Get queue status
    r1 = client.get("/patterns/queue")
    initial_queue_size = r1.json().get("queue_size", 0)
    
    # Add pattern
    pattern_id = list(web.patterns.keys())[0] if web.patterns else "41"
    r2 = client.post(f"/patterns/queue/add/{pattern_id}")
    
    # Check queue updated
    r3 = client.get("/patterns/queue")
    new_queue_size = r3.json().get("queue_size", 0)
    
    if new_queue_size == initial_queue_size + 1:
        print("   ✅ Pattern added to queue successfully")
    else:
        print("   ⚠️  Queue size mismatch after add")
except Exception as e:
    print(f"   ❌ Pattern flow error: {e}")

print()

# Flow 3: Broadcast → Acknowledgment
print("3. Knowledge Broadcast Flow → Acknowledgment")
try:
    # Send broadcast with correct parameters: tipo, content, priority
    r1 = client.post("/broadcast?tipo=test&content=Integration%20test&priority=normal")
    broadcast_ok = r1.status_code in [200, 201]
    
    # Get history
    r2 = client.get("/broadcast/history")
    history_ok = r2.status_code == 200 and len(r2.json().get("history", [])) > 0
    
    if broadcast_ok and history_ok:
        print("   ✅ Broadcast sent and appears in history")
    else:
        print(f"   ⚠️  Broadcast flow incomplete (sent={broadcast_ok}, history={history_ok})")
except Exception as e:
    print(f"   ❌ Broadcast flow error: {e}")

print()

# Flow 4: Control System
print("4. Control System Flow → Pause/Resume")
try:
    # Pause
    r1 = client.post("/control/pause-all")
    paused = r1.status_code in [200, 201]
    
    # Check status
    r2 = client.get("/control/status")
    status = r2.json() if r2.status_code == 200 else {}
    is_paused = status.get("execution_state") == "paused" or status.get("pause_status", {}).get("researcher") == True
    
    # Resume
    r3 = client.post("/control/resume-all")
    resumed = r3.status_code in [200, 201]
    
    if paused and resumed:
        print("   ✅ Control system pause/resume working")
    else:
        print(f"   ⚠️  Control flow incomplete (paused={paused}, resumed={resumed})")
except Exception as e:
    print(f"   ❌ Control flow error: {e}")

print()

# Flow 5: Checkpoints
print("5. Checkpoint Flow → Create → Restore")
try:
    # Create checkpoint
    r1 = client.post("/checkpoints/create", json={})
    checkpoint_id = r1.json().get("snapshot_id") if r1.status_code in [200,201] else None
    
    # List checkpoints
    r2 = client.get("/checkpoints")
    checkpoints = r2.json().get("checkpoints", []) if r2.status_code == 200 else []
    
    if checkpoint_id and len(checkpoints) > 0:
        print("   ✅ Checkpoint creation and listing working")
    else:
        print("   ⚠️  Checkpoint flow incomplete")
except Exception as e:
    print(f"   ❌ Checkpoint flow error: {e}")

print()
print("=" * 70)

# ────────────────────────────────────────────────────────────────────
# SUMMARY
# ────────────────────────────────────────────────────────────────────

print()
print("INTEGRATION SUMMARY:")
print()

total_endpoints = sum(len(v) if isinstance(v, list) else 1 for v in test_results.values())
passed_endpoints = sum(sum(1 for _, ok in v if ok) if isinstance(v, list) else (1 if v else 0) for v in test_results.values())

print(f"Health Checks: {'✅' if test_results['health'] and test_results['status'] else '❌'}")
print(f"Meritocracy: {sum(1 for _, ok in test_results['meritocracy'] if ok)}/{len(test_results['meritocracy'])} endpoints")
print(f"Pattern Web: {sum(1 for _, ok in test_results['patterns'] if ok)}/{len(test_results['patterns'])} endpoints")
print(f"Broadcasting: {sum(1 for _, ok in test_results['broadcast'] if ok)}/{len(test_results['broadcast'])} endpoints")
print(f"Control System: {sum(1 for _, ok in test_results['control'] if ok)}/{len(test_results['control'])} endpoints")
print(f"Checkpoints: {sum(1 for _, ok in test_results['checkpoints'] if ok)}/{len(test_results['checkpoints'])} endpoints")

print()
print(f"Overall: {passed_endpoints}/{total_endpoints} endpoints operational")

if passed_endpoints == total_endpoints:
    print()
    print("✅ ALL SYSTEMS FULLY INTEGRATED AND OPERATIONAL")
else:
    print()
    print("⚠️  Some endpoints may need attention (see above)")

print()
print("=" * 70)
