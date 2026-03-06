# 🛡️ SOVEREIGN COMMAND CENTER - QUICK START GUIDE

## Getting Started in 3 Steps

### Step 1: Start the Sovereign Dashboard
```bash
cd /workspaces/QL
streamlit run frontend/sovereign_dashboard.py
```

Your dashboard will open at: **http://localhost:8501**

### Step 2: Start the FastAPI Backend (Optional but Recommended)
In another terminal:
```bash
cd /workspaces/QL
python -m uvicorn backend.hive_api:app --reload
```

API documentation at: **http://localhost:8000/docs**

### Step 3: Start the Continuous Hive (For Background Operation)
In another terminal:
```bash
cd /workspaces/QL
./start_hive.sh 3 300
```

Monitor with:
```bash
./monitor_hive.sh
```

---

## Dashboard Overview

### 🛡️ Sidebar Controls (Left Side)

**🕹️ Hive Controls**
- `⏸️ PAUSE ALL` - Pauses all agents immediately
- `▶️ RESUME` - Resumes all paused agents
- System status indicators (Agents, State)

**🔗 Quick Links**
- Recalculate Agent of the Day
- Save current hive state
- Export metrics as JSON

**ℹ️ System Info**
- Current timestamp
- CrewAI status (✓ or ✗)
- Database connection status
- Meritocracy system status

---

### 🔮 Research Foundry Tab

**What it does:** Interactive pattern selection and execution queue management

**How to use:**
1. View the 3D Pattern Web statistics
2. Search for patterns by ID or name
3. Filter by pattern type
4. Select patterns and add to queue
5. Execute queue when ready

**Key metrics:**
- Total Patterns (100+ sample patterns)
- Clusters (4 types: mathematical, linguistic, etc.)
- Graph edges (relationships between patterns)
- Queue size

---

### 🏆 Agent Meritocracy Tab

**What it does:** Track agent performance and reward the best performers

#### Sub-Tabs:

**1. 🏆 Leaderboard**
- See all agents ranked by credits
- View accuracy scores
- Task completion counts
- Success rates
- Top 3 agents highlighted with medals

**How to use:**
```
Rank | Agent Name | Role | Credits | Accuracy
🥇  | Senior Arch... | Senior Architect | 1,500 | 99.8%
🥈  | Crypt-Worker | Crypt-Worker | 1,010 | 95.0%
🥉  | Philologist | Linguistic Expert | 1,200 | 92.5%
```

**2. 🌟 Agent of the Day**
- See today's top performer
- Recalculate if needed with 🔄 button
- Agent gets 500 bonus credits
- Achievement summary shown

**Sample:**
```
🏆 Senior Architect
Performance Score: 98.5
Achievement: Excellent pattern analysis
Tasks: 15 | +500 💎 Bonus!
```

**3. 👤 Agent Detail**
- Select any agent from dropdown
- View detailed metrics:
  - Total credits
  - Accuracy percentage
  - Tasks completed
  - Success rate with progress bar
- See reward history (last 30 days)
- Who awarded what and when

---

### 📡 Knowledge Broadcast Tab

**What it does:** Push knowledge updates to all agents' shared memory

#### How to broadcast:
1. Select knowledge type:
   - Pattern Discovery
   - Error Alert
   - Optimization Tip
   - Style Guide
   - Custom

2. Choose priority:
   - Low
   - Normal (default)
   - High
   - Critical

3. Write your knowledge content

4. Click `🚀 Broadcast Now`

**Example:**
```
Type: Pattern Discovery
Priority: High
Content: Pattern #521 exhibits Modulo-19 conformance! 
         Recommend for cryptographic analysis.
```

#### Knowledge Categories Shown:
- 143 Pattern Discoveries
- 28 Known Errors Documented
- 67 Optimization Tips
- 12 Active Style Rules

#### Broadcasting Features:
- `💾 Save Draft` - Save for later
- `📜 Broadcast History` - View past broadcasts
- `✓ Acknowledgments` - See which agents received updates

---

### 📋 Execution Queue Tab

**What it does:** Manage which patterns are queued for execution

#### Sub-Tabs:

**1. 📋 Queue**
- Shows current patterns waiting to execute
- Drag patterns into queue from pattern web
- Control buttons:
  - `🚀 Execute Queue` - Run all queued patterns
  - `⏸️ Pause Queue` - Pause execution
  - `🗑️ Clear Queue` - Empty the queue

**Queue Overview:**
```
Queue Size: 3
Patterns Pending: 3
Est. Time: 15s
Avg. Duration: ~5s per pattern
```

**2. 📊 History**
- Shows recently executed patterns
- Success/failure counts
- Execution duration
- Timestamps

**3. ⚙️ Settings**
- Batch size (how many patterns per batch)
- Interval (seconds between batches)
- Batch processing configuration

---

### 🕹️ System Control Tab

**What it does:** Advanced control over agent execution and state recovery

#### Left Side: ⏸️ Execution Control

**Global State:**
- Shows current state (IDLE, RUNNING, PAUSED, etc.)
- `⏸️ PAUSE ALL NODES` - Emergency stop
- `▶️ RESUME ALL NODES` - Resume all

**Individual Node Control:**
For each agent (researcher, auditor, etc.):
- See if node is paused or running
- Individual pause/resume buttons

#### Right Side: 💾 Checkpoint Management

**Create Checkpoint:**
- Click `📸 Create Checkpoint`
- Saves current hive state
- Can restore later if needed

**Restore from Checkpoint:**
- Select timestamp from dropdown
- Shows state name and time
- Click `🔄 Restore Checkpoint`
- Hive continues from saved state

**Workflow Interrupts:**
- Shows pending interrupts
- Reason for interruption
- Can resolve interrupts as needed

---

### 📊 Dashboard Tab

**What it does:** Real-time summary of system status and key metrics

**Top Metrics:**
```
🥇 Top Agent        | Agent of Day    | Active Agents | Supervisions
Senior Architect    | Auditor         | 4               | 127
1,500 💎           | Score: 98.5     | In Hive        | All-time
```

**Top 5 Agents Section:**
- Rankings with medals (🥇🥈🥉)
- Credits and accuracy percentage
- Quick reference for leaderboard

**System Metrics Section:**
- Total thoughts logged
- Total supervisions completed
- CrewAI status
- Database connection status

---

## Common Tasks

### Award Credits to an Agent
1. Go to **🏆 Agent Meritocracy** tab
2. Click **🌟 Agent of the Day** sub-tab
3. Scroll to **🎁 Award Credits** section
4. Enter agent name (e.g., "Senior Architect")
5. Enter credit amount (e.g., 500)
6. Enter reason (e.g., "Excellent Modulo-19 analysis")
7. Click `🎉 Award!`

### Pause All Agents Immediately
1. Click `⏸️ PAUSE ALL` button in sidebar
2. Confirmation will show "All agents paused ✓"
3. All agents stop executing instantly

### Create a Checkpoint
1. Go to **🕹️ System Control** tab
2. Find **💾 Checkpoint Management** section
3. Click `📸 Create Checkpoint`
4. Success message shows checkpoint ID
5. Can restore from this checkpoint anytime

### Find Similar Patterns
1. Go to **🔮 Research Foundry** tab
2. Enter pattern ID in search box
3. Select pattern filters (optional)
4. Click `🔍 Search`
5. Similar patterns displayed with scores

### Broadcast Updates to Agents
1. Go to **📡 Knowledge Broadcast** tab
2. Select knowledge type
3. Set priority level
4. Write the update
5. Click `🚀 Broadcast Now`
6. All agents immediately receive and acknowledge

---

## API Usage Examples

### Get Leaderboard
```bash
curl http://localhost:8000/meritocracy/leaderboard?limit=10
```

Response:
```json
{
  "status": "success",
  "rank_count": 4,
  "leaderboard": [
    {
      "agent_id": "Senior Architect",
      "role": "Senior Architect & Reviewer",
      "total_credits": 1500,
      "accuracy_score": 99.8,
      "tasks_completed": 120
    }
  ]
}
```

### Award Credits via API
```bash
curl -X POST \
  "http://localhost:8000/meritocracy/award-credits/Senior%20Architect?amount=100&reason=Excellent%20work" \
  -H "Content-Type: application/json"
```

### Get Agent of the Day
```bash
curl http://localhost:8000/meritocracy/agent-of-the-day
```

### Export All Metrics
```bash
curl http://localhost:8000/meritocracy/export > metrics.json
```

### View API Documentation
Open: **http://localhost:8000/docs**

---

## Database Access

### View Agents via SQLite
```bash
sqlite3 /workspaces/QL/data/processed/meritocracy.db
```

```sql
-- See all agents
SELECT agent_id, role, total_credits, accuracy_score FROM agent_registry;

-- See rewards given today
SELECT * FROM reward_logs WHERE date(timestamp) = date('now');

-- See Agent of the Day history
SELECT * FROM agent_of_the_day ORDER BY date DESC LIMIT 7;
```

### Backup Database
```bash
cp /workspaces/QL/data/processed/meritocracy.db \
   /workspaces/QL/data/processed/meritocracy_backup_$(date +%Y%m%d).db
```

---

## Troubleshooting

### Dashboard won't start
```bash
# Check if another instance is running
lsof -i :8501
# Kill it if needed
kill -9 <PID>
# Try again
streamlit run frontend/sovereign_dashboard.py
```

### API endpoints not responding
```bash
# Check if FastAPI is running
lsof -i :8000
# Restart it
python -m uvicorn backend.hive_api:app --reload
```

### Meritocracy database error
```bash
# Check database integrity
sqlite3 /workspaces/QL/data/processed/meritocracy.db ".integrity_check"

# Reset if corrupted
rm /workspaces/QL/data/processed/meritocracy.db
# Will recreate on next run
```

### Checkpoints not found
```bash
# Verify checkpoint directory
ls -la /workspaces/QL/data/processed/checkpoints/

# Create if missing
mkdir -p /workspaces/QL/data/processed/checkpoints
```

---

## Performance Tips

1. **For Large Datasets:**
   - Use `/meritocracy/leaderboard?limit=50` for pagination
   - Don't load all history at once

2. **For Real-time Updates:**
   - Refresh dashboard every 5-10 seconds
   - Use WebSocket API (coming soon)

3. **For Frequent Checkpoints:**
   - Rotate old checkpoints monthly
   - Keep only last 20-50

4. **For High Agent Count:**
   - Use database indices (automatically created)
   - Archive old records annually

---

## What Happens Automatically

### During Continuous Hive Operation
Every hive cycle automatically:
1. ✅ Records task completion metrics
2. ✅ Updates agent accuracy scores
3. ✅ Awards completion bonuses
4. ✅ Tracks execution time
5. ✅ Saves hive state

### At Midnight
Daily:
1. ✅ Calculates Agent of the Day
2. ✅ Awards 500 bonus credits to winner
3. ✅ Archives previous day's metrics

### Whenever You Click Save
1. ✅ Exports hive state to JSON
2. ✅ Persists all agent metrics
3. ✅ Backs up knowledge base

---

## Next Steps

1. **Start the dashboard** - See your hive in action
2. **Try the tasks** - Award credits, broadcast knowledge
3. **Monitor agents** - Watch Agent of the Day change
4. **Use the API** - Integrate with your own tools
5. **Create checkpoints** - Protect your progress

---

**Ready to command your Hive? 🛡️**

Open your dashboard now:
```bash
streamlit run frontend/sovereign_dashboard.py
```

Visit: **http://localhost:8501**

---

*Last Updated: March 6, 2026*
