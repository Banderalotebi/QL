# 🎯 SOVEREIGN DASHBOARD - QUICK START GUIDE

## Starting the Dashboard

### Option 1: Direct Mode (Fastest - No API Server Needed)
```bash
cd /workspaces/QL
streamlit run frontend/sovereign_dashboard.py
```
- Low latency, direct component access
- Perfect for development and testing
- No external dependencies

### Option 2: API Mode (Production-Ready)
```bash
# Terminal 1: Start FastAPI backend
cd /workspaces/QL
python -m uvicorn backend.hive_api:app --reload --port 8000

# Terminal 2: Start Streamlit frontend with API mode enabled
cd /workspaces/QL
USE_API=true streamlit run frontend/sovereign_dashboard.py
```
- Decoupled frontend/backend
- Scales to multiple instances
- Supports remote deployment

---

## Dashboard Tabs & Features

### 1. 🏆 Meritocracy Tab
**Shows**: Agent performance, credits, rankings

**Components**:
- **Leaderboard** - Top 10 agents by total credits
  - Displays rank, agent name, role, credits, status
  - Purple highlights top performer
  - Updates in real-time

- **Agent Metrics** - Detailed performance for each agent
  - Hypotheses tested
  - Accuracy percentage  
  - Patterns discovered
  - Broadcasts sent

- **Rewards Panel** - Recent credit awards
  - Who awarded credits
  - Amount awarded
  - Reason for award
  - Timestamp

**Data Source**: MeritocracyDB (SQLite)

**Try It**: 
```
1. View the leaderboard - all agents visible
2. Click menus to see individual agent metrics
3. Awards appear automatically when supervision occurs
```

---

### 2. 🕸️ Pattern Web Tab
**Shows**: 3D pattern visualization, clustering, execution queue

**Components**:
- **3D Pattern Graph** - Interactive network visualization
  - X, Y, Z coordinates for spatial layout
  - Color-coded by status (Blue: pending, Gold: executing, Green: verified)
  - Click patterns to inspect details
  - Hover for pattern names

- **Pattern Stats** - Distribution and metadata
  - Total patterns: 10
  - Clusters: 4 (Phonetic, Structural, Root, Cryptanalytic)
  - Current status distribution
  - Pattern types breakdown

- **Execution Queue** - Pattern processing status
  - Patterns waiting to execute
  - Estimated execution time
  - Add patterns manually via dropdown
  - View execution history

**Data Source**: PatternWebVisualizer (in-memory + file cache)

**Try It**:
```
1. Scroll the 3D graph - see pattern relationships
2. Click "Add to Queue" dropdown - select pattern 41
3. Watch queue size increase
4. Click "Execute Queue" to process
5. Patterns move from "queued" → "executing" → "verified"
```

---

### 3. 📢 Broadcast Tab
**Shows**: Knowledge sharing between agents

**Components**:
- **Send Broadcast** - Agent communication interface
  - Content text area for knowledge/hypotheses
  - Message type selector (discovery, alert, synthesis, etc.)
  - Priority level (normal, high, urgent)
  - Send button

- **Broadcast History** - Archive of all messages
  - Message content
  - Sender (usually "system")
  - Type and priority
  - Timestamp
  - Who acknowledged

- **Pending Broadcasts** - Waiting for acknowledgment
  - Lists broadcasts awaiting responses
  - From which agents they're pending
  - Age of message
  - Acknowledge button

**Data Source**: HiveCouncil.shared_memory['broadcasts']

**Try It**:
```
1. Type in "Test discovery" in Send Broadcast
2. Select type "pattern_discovery"
3. Click Send
4. Message appears in History immediately
5. Check Pending - shows your broadcast waiting for acks
```

---

### 4. ⚙️ Control Tab
**Shows**: System pause/resume, checkpoints, interrupts

**Components**:
- **System Control** - Execution state management
  - Current state display (idle/running/paused)
  - Pause All button - stops all agent execution
  - Resume All button - restarts execution
  - Status indicators update in real-time

- **Checkpoint Management** - State snapshots
  - Create Checkpoint - save current system state
  - Checkpoint List - view all saved snapshots
    - Timestamp of snapshot
    - IDs and descriptions
  - Restore button - recover from checkpoint

- **Interrupt Management** - Force agent stops
  - Pending interrupts list
  - Source and target information
  - Resolve button to clear interrupts

**Data Source**: GraphController (LangGraph)

**Try It**:
```
1. Check current state - should show "idle"
2. Click "Pause All" - executes pause
3. State changes to "paused"
4. Click "Create Checkpoint" - saves snapshot
5. See checkpoint appear in list with timestamp
6. Click "Resume All" - back to running
```

---

## Dashboard Functionality Map

```
┌──────────────────────────────────────┐
│     SOVEREIGN DASHBOARD              │
├──────┬────────┬──────────┬───────────┤
│ Merit│Pattern │Broadcast │ Control   │
│ocracy│  Web   │          │           │
├──────┼────────┼──────────┼───────────┤
│ Ldr. │ 3D Grph│ Send Msg │ Pause     │
│ Metrics│Stats  │ History  │ Resume    │
│ Awards│Queue  │ Pending  │Checkpoints│
│      │Execute │ Ack      │Interrupts │
└──────┴────────┴──────────┴───────────┘
  ↓      ↓         ↓          ↓
 DB    Memory    Memory     LangGraph
API    API       API        API
```

---

## Typical Workflow

### Scenario 1: Watch Pattern Discovery
```
1. Go to Pattern Web tab
2. See 10 patterns in 3D space
3. Select pattern "41" in Add to Queue dropdown
4. Watch queue size increase to 1
5. Click Execute Queue
6. Pattern status changes: pending → queued → executing → verified
7. See execution time display update
```

### Scenario 2: Broadcast Knowledge Discovery
```
1. Go to Meritocracy tab
2. Note current top agent and their credits
3. Go to Broadcast tab
4. Type: "Found 5 new mathematical patterns in Surah 2"
5. Select type: "pattern_discovery"
6. Click Send Broadcast
7. Message appears in History
8. Wait for acknowledgments in Pending tab
```

### Scenario 3: System Maintenance
```
1. Go to Control tab
2. Verify current state
3. If running long operation, click Pause All
4. Create a checkpoint to save state
5. View checkpoint in history
6. After maintenance, Resume All
7. Or restore from checkpoint if needed
```

### Scenario 4: Performance Review
```
1. Go to Meritocracy tab
2. Review leaderboard - top 3 agents
3. Click each to see detailed metrics
4. Check who has highest accuracy
5. Check who found most patterns
6. Note reward distribution in Awards section
```

---

## Common Commands

### Programmatic Access (Python)
```python
# Direct mode
from src.agents.hive_council import get_hive_council
hive = get_hive_council()
leaderboard = hive.get_leaderboard()

# API mode
import requests
response = requests.get("http://localhost:8000/meritocracy/leaderboard")
leaderboard = response.json()["leaderboard"]
```

### Dashboard Tests
```bash
# Test direct mode
streamlit run frontend/sovereign_dashboard.py

# Test API mode
USE_API=true streamlit run frontend/sovereign_dashboard.py

# Full integration test
python tests/test_integration_wiring.py
```

---

## Keyboard Shortcuts & Tips

### Pattern Web Tab
- **Scroll wheel** - Zoom in/out on 3D graph
- **Click + drag** - Rotate graph
- **Hover** - Shows pattern details

### Broadcast Tab
- **Tab** - Move between fields
- **Enter** - Quick send (if implemented)

### All Tabs
- **Shift+R** - Refresh page
- **F11** - Full screen mode (browser)

---

## Data Sources & APIs

### Meritocracy Data
- **Source**: MeritocracyDB (SQLite)
- **API Endpoint**: `GET /meritocracy/leaderboard`
- **Update Frequency**: Real-time
- **Fields**: agent_id, role, total_credits, status

### Pattern Data
- **Source**: PatternWebVisualizer (memory + file cache)
- **API Endpoint**: `GET /patterns/stats`
- **Update Frequency**: On-demand
- **Fields**: pattern_id, cluster_id, status, 3D coordinates

### Broadcast Data
- **Source**: HiveCouncil.shared_memory
- **API Endpoint**: `GET /broadcast/history`
- **Update Frequency**: Real-time
- **Fields**: id, content, message_type, timestamp

### Control Data
- **Source**: GraphController (LangGraph)
- **API Endpoint**: `GET /control/status`
- **Update Frequency**: Real-time
- **Fields**: execution_state, paused_nodes, last_checkpoint_id

---

## Troubleshooting Dashboard Issues

### Dashboard Won't Start
```bash
# Check if port 8501 is in use
lsof -i :8501

# Run on different port
streamlit run frontend/sovereign_dashboard.py --server.port 8502
```

### API Mode Shows "Connection Refused"
```bash
# Ensure FastAPI is running
ps aux | grep uvicorn

# Start API server if missing
python -m uvicorn backend.hive_api:app --reload
```

### Meritocracy Tab Shows No Agents
```bash
# Initialize database
python -c "from src.data.meritocracy_db import init_db; init_db()"

# Verify database
python -c "from src.data.meritocracy_db import get_meritocracy_db; db = get_meritocracy_db(); print(db.get_all_agents())"
```

### Pattern Web Shows Blank Graph
```bash
# Regenerate patterns
python -c "
from frontend.components.pattern_web import get_pattern_web_visualizer
web = get_pattern_web_visualizer()
print(f'Patterns: {len(web.patterns)}')
print(f'Clusters: {len(web.clusters)}')
"
```

---

## Performance Tips

1. **Use Direct Mode for Development**
   - Faster iteration
   - No network latency
   - Easier debugging

2. **Use API Mode for Production**
   - Better separation of concerns
   - Scale to multiple instances
   - Easier to deploy

3. **Pattern Web Optimization**
   - 3D graph can be slow with 100+ patterns
   - Consider clustering for large datasets
   - Use "Hide edges" option for clarity

4. **Broadcast Performance**
   - Archive old broadcasts to keep history manageable
   - Use message filtering for high-volume scenarios

---

## Advanced Features

### Custom Metrics (Extend Meritocracy)
```python
# In meritocracy_db.py
def add_custom_metric(self, agent_id: str, metric_name: str, value: float):
    # Record custom metric for agent
    pass
```

### Pattern Similarity Analysis
```python
# In pattern_web.py
similar = web.get_pattern_similarity(pattern_id="41", top_n=5)
# Returns: list of similar pattern IDs with similarity scores
```

### Selective Broadcast
```python
# In hive_council.py
hive.broadcast_knowledge(
    content="Private message",
    target_agents=["researcher_1", "validator_1"]
)
```

---

## Keyboard Navigation

```
Home          - Go to first tab
End           - Go to last tab
→ / ←         - Switch tabs (if implemented)
R             - Refresh current section
? or H        - Help (if implemented)
Esc           - Close modals/dropdowns
```

---

## Support Resources

1. **System Integration Guide**: `SYSTEM_INTEGRATION_GUIDE.md`
2. **API Documentation**: Visit `http://localhost:8000/docs` (when API running)
3. **Test Suite**: `tests/test_integration_wiring.py`
4. **Debug Mode**: Set `DEBUG_MODE=true` in dashboard

---

**Dashboard Version**: v1.0  
**Last Updated**: 2024-01-15  
**Status**: ✅ All Features Operational

Enjoy exploring the Sovereign Command Center! 🚀
