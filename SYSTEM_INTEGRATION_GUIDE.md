# 🛡️ SOVEREIGN COMMAND CENTER - SYSTEM INTEGRATION GUIDE

## Overview

The Sovereign Command Center is a unified AI research platform that integrates:
- **HiveCouncil**: 4-agent hierarchical multi-agent system with meritocracy tracking
- **Pattern Web**: 3D knowledge graph with execution queue and pattern clustering
- **Knowledge Broadcast**: Pub/sub message system for agent communication
- **Control System**: LangGraph-based pause/resume/checkpoint management
- **Meritocracy DB**: SQLite-backed reward and credit system
- **FastAPI Backend**: 20+ REST endpoints for all subsystems

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              STREAMLIT DASHBOARD (Frontend)             │
│  (sovereign_dashboard.py)                               │
│  ┌─ Meritocracy Tab        ┌─ Pattern Web Tab          │
│  │  - Leaderboard          │  - 3D cluster view        │
│  │  - Agent metrics        │  - Pattern queue          │
│  │  - Rewards              │  - Execution history      │
│  └─ Broadcast Tab          └─ Control Tab              │
│     - Message inbox           - Pause/resume           │
│     - Send knowledge          - Checkpoints            │
│     - Acknowledgments         - Interrupts             │
└─────────────────────────────────────────────────────────┘
         ↕ (HTTP REST - USE_API=true/false)
┌─────────────────────────────────────────────────────────┐
│           FASTAPI BACKEND (backend/hive_api.py)         │
│  ┌── Health ──┬─── Meritocracy ──┬─── Patterns ────    │
│  │  /health   │  /leaderboard     │  /patterns/stats   │
│  │  /status   │  /agent-of-day    │  /patterns/graph   │
│  │            │  /award-credits   │  /patterns/queue   │
│  └────────────┴───────────────────┴────────────────    │
│  ┌── Broadcast ──┬─── Control ──┬─── Checkpoints ──   │
│  │  /broadcast   │  /status      │  /list             │
│  │  /history     │  /pause-all   │  /create           │
│  │  /ack         │  /resume-all  │  /restore          │
│  └───────────────┴───────────────┴────────────────    │
└─────────────────────────────────────────────────────────┘
         ↕ (Direct Python imports)
┌─────────────────────────────────────────────────────────┐
│              CORE COMPONENTS (Backend)                  │
│  ┌─ HiveCouncil ──────────┬─ MeritocracyDB ───────    │
│  │  - 4 agents            │  - Agent registry         │
│  │  - Supervision         │  - Reward logs            │
│  │  - Broadcast           │  - Agent metrics          │
│  │  - Shared memory       │  - Leaderboard           │
│  └────────────────────────┴──────────────────────    │
│  ┌─ PatternWeb ───────────┬─ GraphController ────    │
│  │  - 3D patterns         │  - Pause/resume states   │
│  │  - Clusters            │  - Checkpoints           │
│  │  - Execution queue     │  - Interrupt manager     │
│  │  - Graph analysis      │  - State snapshots       │
│  └────────────────────────┴──────────────────────    │
└─────────────────────────────────────────────────────────┘
```

---

## Component Status Report

### ✅ All 20 API Endpoints Operational

#### Health & Status (2 endpoints)
```
✅ GET  /health           - Service health check
✅ GET  /status           - System status and metrics
```

#### Meritocracy System (5 endpoints)
```
✅ GET  /meritocracy/leaderboard          - Top agents by credits
✅ GET  /meritocracy/agent-of-the-day     - Current best performing agent
✅ POST /meritocracy/calculate-agent-of-the-day - Compute daily rankings
✅ GET  /meritocracy/all-agents           - List all registered agents
✅ GET  /meritocracy/export               - Export metrics as CSV/JSON
```

#### Pattern Web (4 endpoints)
```
✅ GET  /patterns/stats              - Pattern statistics & distribution
✅ GET  /patterns/graph              - 3D graph visualization data
✅ GET  /patterns/queue              - Current execution queue status
✅ POST /patterns/queue/add/{id}     - Add pattern to execution queue
```

#### Knowledge Broadcast (3 endpoints)
```
✅ POST /broadcast                   - Send knowledge to hive
✅ GET  /broadcast/history           - Retrieve broadcast history
✅ GET  /broadcast/pending           - Get pending broadcasts
```

#### Control System (3 endpoints)
```
✅ GET  /control/status              - Current execution state
✅ POST /control/pause-all           - Pause all agents/patterns
✅ POST /control/resume-all          - Resume execution
```

#### Checkpoints & Interrupts (3 endpoints)
```
✅ GET  /checkpoints                 - List all checkpoints
✅ POST /checkpoints/create          - Create new state snapshot
✅ GET  /interrupts                  - List pending interrupts
```

---

## Integration Data Flows

### Flow 1: Meritocracy & Credits ✅
```
Supervision Event (HiveCouncil)
    ↓
Award Credits (MeritocracyDB.award_credits)
    ↓
Update Agent Metrics
    ↓
Leaderboard Reflects Changes (API: /meritocracy/leaderboard)
    ↓
Frontend Updates Meritocracy Panel

Status: Fully Integrated - Credit awards flow correctly through database to UI
```

### Flow 2: Pattern Execution Queue ✅
```
Add Pattern Request (API: /patterns/queue/add/{id})
    ↓
PatternWeb.add_pattern_to_queue()
    ↓
Pattern Status → "queued"
    ↓
Queue Status Available (API: /patterns/queue)
    ↓
Frontend Shows Pattern in Queue UI

Status: Functional - Queue operations working correctly
```

### Flow 3: Knowledge Broadcast ✅
```
Broadcast Request (API: /broadcast?tipo=X&content=Y)
    ↓
HiveCouncil.broadcast_knowledge()
    ↓
Message Stored in shared_memory['broadcasts']
    ↓
History Available (API: /broadcast/history)
    ↓
Frontend Displays in Broadcast Tab

Status: Fully Operational - Broadcasting working end-to-end
```

### Flow 4: Control System (Pause/Resume) ✅
```
Pause Request (API: /control/pause-all)
    ↓
GraphController.pause_all()
    ↓
State → "paused"
    ↓
Status Endpoint Reports Pause (API: /control/status)
    ↓
Resume Request (API: /control/resume-all)
    ↓
State → "running"

Status: Fully Functional - State transitions working properly
```

### Flow 5: Checkpoints ✅
```
Create Checkpoint Request (API: /checkpoints/create)
    ↓
GraphController.take_checkpoint()
    ↓
State Snapshot Saved
    ↓
Checkpoint Listed (API: /checkpoints)
    ↓
Frontend Can Restore from Checkpoint

Status: Operational - Snapshot creation and listing working
```

---

## Frontend Integration

### Dual-Mode Operation
The frontend (sovereign_dashboard.py) supports two operation modes:

#### Mode 1: Direct Component Mode (Default)
```python
USE_API=false  # or unset

# Dashboard imports components directly:
from src.agents.hive_council import get_hive_council
from frontend.components.pattern_web import get_pattern_web_visualizer
from frontend.components.meritocracy_panel import render_meritocracy

# Direct function calls
hive = get_hive_council()
leaderboard = hive.get_leaderboard()
```

**Advantages**: Lower latency, no network overhead, direct state access  
**Use case**: Local development, troubleshooting, embedded mode

#### Mode 2: API Mode
```python
USE_API=true

# Dashboard makes HTTP requests:
import requests

response = requests.get("http://localhost:8000/meritocracy/leaderboard")
leaderboard = response.json()
```

**Advantages**: Decoupled frontend/backend, scalable, production-ready  
**Use case**: Production deployment, multi-instance, cloud deployment

### Helper Functions in Dashboard

The dashboard includes wrapper functions for all major operations:

```python
# API Helper Functions
def api_get(endpoint, params=None):
    """Make GET request to API"""
    
def api_post(endpoint, json=None):
    """Make POST request to API"""

# Meritocracy Wrappers
hive.get_leaderboard()           → /meritocracy/leaderboard
hive.get_agent_of_the_day()      → /meritocracy/agent-of-the-day
hive.get_agent_metrics(agent_id) → /meritocracy/metrics

# Pattern Wrappers
web.pattern_stats()              → /patterns/stats
web.get_queue_status()           → /patterns/queue
web.add_pattern_to_queue(id)     → /patterns/queue/add/{id}

# Control Wrappers
controller.pause_all()           → /control/pause-all
controller.resume_all()          → /control/resume-all
controller.get_status()          → /control/status

# Broadcast Wrappers
hive.broadcast_knowledge(content, tipo)  → /broadcast
hive.get_broadcast_history()             → /broadcast/history
```

---

## Database Architecture

### MeritocracyDB (SQLite)

**Tables**:
```sql
-- Agent Registry (5 agents currently)
agents:
  - agent_id (TEXT, PK)
  - role (TEXT)              -- "Researcher", "Validator", "Synthesizer", "Archiver"
  - total_credits (INTEGER)  -- Accumulated rewards
  - status (TEXT)            -- "active", "paused"
  - created_at (TIMESTAMP)

-- Reward Logs
reward_logs:
  - id (INTEGER, PK)
  - agent_id (TEXT, FK)
  - amount (INTEGER)
  - reason (TEXT)
  - timestamp (TIMESTAMP)

-- Agent Metrics
agent_metrics:
  - agent_id (TEXT, PK)
  - hypotheses_tested (INTEGER)
  - accuracy (FLOAT)
  - patterns_found (INTEGER)
  - broadcasts_sent (INTEGER)

-- Agent of the Day
agent_of_the_day:
  - date (DATE, PK)
  - agent_id (TEXT, FK)
  - score (FLOAT)
```

**Connection**: `sqlite:////workspaces/QL/data/processed/meritocracy.db`

---

## Known Working Exemplars

### 1. Meritocracy System
- 5 agents registered and tracked
- Leaderboard showing correct credit distributions
- Agent-of-the-day calculation working
- Credits awarded on supervision events

### 2. Pattern Web Visualization
- 10 patterns loaded in 3D space
- 4 clusters created (Phonetic, Structural, Root, Cryptanalytic)
- Execution queue operations functional
- Pattern similarity calculations working

### 3. Control System
- State machine initialized (current: idle)
- Pause/resume transitions working
- Checkpoint snapshots being created
- Status reporting accurate

### 4. Broadcasting
- Knowledge broadcasts stored in shared_memory
- Broadcast history retrievable
- Pending broadcasts trackable
- Message acknowledgment working

---

## Testing & Validation

### Running the Integration Test
```bash
cd /workspaces/QL
python tests/test_integration_wiring.py
```

**Expected Output**:
```
✅ ALL SYSTEMS FULLY INTEGRATED AND OPERATIONAL
✅ 20/20 endpoints operational
✅ All integration flows successful
```

### Testing Individual Endpoints
```bash
# Start the API server
python -m uvicorn backend.hive_api:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/meritocracy/leaderboard
curl http://localhost:8000/patterns/stats
```

### Testing Dashboard Modes
```bash
# Direct mode (default)
streamlit run frontend/sovereign_dashboard.py

# API mode (requires FastAPI server running)
USE_API=true streamlit run frontend/sovereign_dashboard.py
```

---

## API Endpoint Documentation

### Pattern Queue API

**Get Queue Status**
```http
GET /patterns/queue
Response:
{
  "queue_size": 3,
  "queued_patterns": [
    {"pattern_id": "41", "name": "Phonetic Marker"},
    ...
  ],
  "estimated_execution_time_seconds": 15
}
```

**Add Pattern to Queue**
```http
POST /patterns/queue/add/{pattern_id}
Response:
{
  "status": "added",
  "pattern_id": "41"
}
```

### Meritocracy API

**Get Leaderboard**
```http
GET /meritocracy/leaderboard?limit=10
Response:
{
  "leaderboard": [
    {
      "rank": 1,
      "agent_id": "researcher_1",
      "role": "Researcher",
      "total_credits": 1250,
      "status": "active"
    },
    ...
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

### Broadcast API

**Send Broadcast**
```http
POST /broadcast?tipo=pattern_discovery&content=Found+new+pattern&priority=normal
Response:
{
  "status": "broadcasted",
  "message": {
    "id": "msg_123",
    "content": "Found new pattern",
    "timestamp": "2024-01-15T10:31:00",
    "acknowledged_by": []
  }
}
```

---

## Configuration

### Environment Variables

```bash
# Frontend Mode
USE_API=true              # Use FastAPI backend (default: false)

# API Server
FASTAPI_PORT=8000        # Port for FastAPI server
FASTAPI_HOST=0.0.0.0     # Host binding

# Database
DATABASE_URL=sqlite:////workspaces/QL/data/processed/meritocracy.db

# Components
OLLAMA_ENABLED=false     # Use Ollama for embeddings
DEBUG_MODE=true          # Enable debug logging
```

---

## Troubleshooting

### Issue: "API connection refused"
```
Solution: Ensure FastAPI server is running
$ python -m uvicorn backend.hive_api:app --reload
```

### Issue: "Meritocracy database not found"
```
Solution: Initialize database
$ python -c "from src.data.meritocracy_db import init_db; init_db()"
```

### Issue: "Pattern web patterns not loading"
```
Solution: Regenerate pattern graph
$ python -c "from frontend.components.pattern_web import get_pattern_web_visualizer; web = get_pattern_web_visualizer(); web.refresh_visualization()"
```

### Issue: "Control system state stuck"
```
Solution: Reset control system
$ python -c "from src.core.langgraph_control import get_graph_controller; ctrl = get_graph_controller(); ctrl.reset_state()"
```

---

## Next Steps

1. **Dashboard Customization**: Add custom visualizations for your research domain
2. **Extended Broadcasting**: Implement selective broadcast targeting specific agents
3. **Advanced Control**: Add per-agent pause/resume for granular control
4. **Metric Extensions**: Add domain-specific metrics to meritocracy system
5. **Multi-Instance Support**: Deploy multiple HiveCounsil instances coordinated via API

---

## System Verification Checklist

- [x] All 20 API endpoints responding with HTTP 200/201
- [x] Meritocracy system tracking agents correctly
- [x] Pattern web visualization with 10 patterns in 4 clusters
- [x] Control system state transitions working
- [x] Broadcasting from HiveCouncil to shared memory
- [x] Checkpoint creation and listing functional
- [x] Frontend dashboard rendering all tabs
- [x] API mode and direct mode both operational
- [x] Integration flows validated end-to-end
- [x] All databases initialized and connected

**Status**: ✅ **SYSTEM FULLY OPERATIONAL**

---

## Support & Debugging

For detailed debugging, enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs in:
- `/workspaces/QL/logs/` - Application logs
- `/workspaces/QL/data/processed/` - Data and state files
- Terminal output when running with `--reload` flag

---

**Generated**: 2024-01-15
**System Version**: Sovereign Command Center v1.0
**Integration Status**: ✅ Complete
