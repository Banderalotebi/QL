# Implementation Plan

[Overview]
Build the complete "Sovereign Command Center" frontend dashboard for the Muqattaat Cryptanalytic Lab, featuring a 3D Pattern Web visualization, Agent Meritocracy Ledger (SQLite), Knowledge Broadcast System, and LangGraph Kill-Switch integration.

[Types]

## Data Models

### Meritocracy Ledger (SQLite)
- AgentRegistry: agent_id (PK), role, total_credits, accuracy_score, tasks_completed, last_active
- RewardLog: log_id (PK), agent_id (FK), reward_amount, reason, timestamp
- AgentOfTheDay: date (PK), agent_id, achievement_summary

### Pattern Web Node (3D Visualization)
- PatternNode: pattern_id, pattern_type, x, y, z coordinates, status, connections
- ExecutionQueue: queue_id, pattern_id, status, added_at

### Knowledge Broadcast Message
- BroadcastMessage: message_id, content, sender, timestamp, priority, recipients

[Files]

## New Files to Create
1. src/data/meritocracy_db.py - SQLite database for agent rewards
2. frontend/components/pattern_web.py - 3D Pattern Web visualization
3. frontend/components/meritocracy_panel.py - Agent rewards panel
4. frontend/components/knowledge_broadcast.py - Knowledge push UI
5. frontend/components/execution_queue.py - Pattern execution queue
6. src/core/langgraph_control.py - LangGraph Kill-Switch
7. frontend/sovereign_dashboard.py - Complete Sovereign Command dashboard
8. tests/test_meritocracy.py - Unit tests for meritocracy

## Existing Files to Modify
1. frontend/streamlit_dashboard.py - Add imports, new tabs
2. src/agents/hive_council.py - Add meritocracy integration
3. backend/hive_api.py - Add meritocracy endpoints
4. requirements.txt - Add pyvis, networkx

[Functions]

## New Functions
- initialize_meritocracy_db(), register_agent(), award_credits(), get_leaderboard()
- calculate_agent_of_the_day(), record_agent_activity()
- load_patterns_for_visualization(), render_pyvis_network(), handle_node_drag()
- create_checkpointer(), pause_execution(), resume_execution(), get_execution_state()
- broadcast_to_agents(), get_broadcast_history(), acknowledge_broadcast()

## Modified Functions
- HiveCouncil: receive_broadcast(), execute_from_queue(), report_task_completion()
- streamlit_dashboard.py: main() with new Sovereign tabs

[Classes]

## New Classes
- MeritocracyDB, AgentMetrics (src/data/meritocracy_db.py)
- PatternWebVisualizer, PatternCluster (frontend/components/pattern_web.py)
- MeritocracyPanel, LeaderboardWidget (frontend/components/meritocracy_panel.py)
- GraphController, ExecutionSnapshot (src/core/langgraph_control.py)
- BroadcastPanel, MessageQueue (frontend/components/knowledge_broadcast.py)

[Dependencies]
- pyvis>=0.3.0, networkx>=3.0, streamlit-webrtc>=0.4.0

[Testing]
- Unit tests for meritocracy operations
- Integration tests for dashboard rendering
- API endpoint verification

[Implementation Order]
1. Database Layer (Priority: HIGH) - meritocracy_db.py
2. LangGraph Integration (Priority: HIGH) - langgraph_control.py
3. Frontend Components (Priority: MEDIUM) - pattern_web, meritocracy_panel, etc.
4. API Extensions (Priority: MEDIUM) - Add endpoints
5. Hive Council Integration (Priority: MEDIUM) - Connect to meritocracy
6. Dashboard Assembly (Priority: HIGH) - sovereign_dashboard.py
7. Testing & Validation (Priority: HIGH)
8. Dependencies (Priority: HIGH)
