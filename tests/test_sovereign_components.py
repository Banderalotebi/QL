"""
Test Suite for Sovereign Command Center Components
Validates all new components: meritocracy, pattern web, broadcasting, etc.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

# Import components to test
from src.data.meritocracy_db import MeritocracyDB, get_meritocracy_db
from frontend.components.pattern_web import PatternWebVisualizer, PatternNode, PatternCluster
from src.core.langgraph_control import GraphController, InterruptManager, ExecutionState
from src.agents.hive_council import get_hive_council
from backend.hive_api import app


# ──────────────────────────────────────────────────────────────────
# MERITOCRACY DATABASE TESTS
# ──────────────────────────────────────────────────────────────────

class TestMeritocracyDB:
    """Test suite for meritocracy database"""
    
    def setup_method(self):
        """Setup test database"""
        self.db = MeritocracyDB(db_path=":memory:")  # Use in-memory for tests
    
    def test_register_agent(self):
        """Test agent registration"""
        success = self.db.register_agent("TestAgent", "Test Role", 1000)
        assert success
        
        metrics = self.db.get_agent_metrics("TestAgent")
        assert metrics is not None
        assert metrics['agent_id'] == "TestAgent"
        assert metrics['total_credits'] == 1000
    
    def test_award_credits(self):
        """Test awarding credits"""
        self.db.register_agent("Agent1", "Role1", 500)
        
        success = self.db.award_credits("Agent1", 100, "Test bonus")
        assert success
        
        metrics = self.db.get_agent_metrics("Agent1")
        assert metrics['total_credits'] == 600
    
    def test_record_task_completion(self):
        """Test recording task completion"""
        self.db.register_agent("Agent2", "Role2", 1000)
        
        success = self.db.record_task_completion(
            agent_id="Agent2",
            task_type="pattern",
            status="success",
            confidence_score=0.95
        )
        assert success
        
        metrics = self.db.get_agent_metrics("Agent2")
        assert metrics['tasks_completed'] > 0
    
    def test_leaderboard(self):
        """Test leaderboard retrieval"""
        self.db.register_agent("Agent1", "Role1", 5000)
        self.db.register_agent("Agent2", "Role2", 3000)
        self.db.register_agent("Agent3", "Role3", 4000)
        
        leaderboard = self.db.get_leaderboard(limit=10)
        assert len(leaderboard) == 3
        assert leaderboard[0]['agent_id'] == "Agent1"  # Highest credits first
    
    def test_agent_of_the_day(self):
        """Test Agent of the Day calculation"""
        self.db.register_agent("Agent1", "Role1", 1000)
        self.db.record_task_completion("Agent1", status="success", confidence_score=0.95)
        self.db.update_accuracy_score("Agent1", 0.95)
        
        winner = self.db.calculate_agent_of_the_day()
        assert winner is not None
        
        aotd = self.db.get_today_agent_of_the_day()
        assert aotd is not None
        assert aotd['agent_id'] == "Agent1"


# ──────────────────────────────────────────────────────────────────
# PATTERN WEB VISUALIZER TESTS
# ──────────────────────────────────────────────────────────────────

class TestPatternWeb:
    """Test suite for pattern web visualizer"""
    
    def setup_method(self):
        """Setup pattern web"""
        self.web = PatternWebVisualizer()
    
    def test_pattern_node_creation(self):
        """Test pattern node creation"""
        node = PatternNode("41", "mathematical", 10.0, 20.0, 30.0)
        assert node.pattern_id == "41"
        assert node.pattern_type == "mathematical"
        assert node.status == "pending"
    
    def test_pattern_cluster(self):
        """Test pattern cluster"""
        cluster = PatternCluster("crypto", "Cryptographic", "mathematical")
        node = PatternNode("100", "mathematical")
        
        cluster.add_pattern(node)
        assert len(cluster.patterns) == 1
    
    def test_add_to_queue(self):
        """Test adding pattern to execution queue"""
        if "41" in self.web.patterns:
            success = self.web.add_pattern_to_queue("41")
            assert success
            assert "41" in self.web.execution_queue
            assert self.web.patterns["41"].status == "queued"
    
    def test_remove_from_queue(self):
        """Test removing pattern from queue"""
        if "41" in self.web.patterns:
            self.web.add_pattern_to_queue("41")
            success = self.web.remove_from_queue("41")
            assert success
            assert "41" not in self.web.execution_queue
    
    def test_execute_queue(self):
        """Test executing queue"""
        if "41" in self.web.patterns and "35" in self.web.patterns:
            self.web.add_pattern_to_queue("41")
            self.web.add_pattern_to_queue("35")
            
            result = self.web.execute_queue()
            assert len(result['executed']) == 2
            assert len(self.web.execution_queue) == 0
    
    def test_statistics(self):
        """Test getting statistics"""
        stats = self.web.get_statistics()
        assert stats['total_patterns'] > 0
        assert stats['total_clusters'] > 0


# ──────────────────────────────────────────────────────────────────
# LANGGRAPH CONTROL TESTS
# ──────────────────────────────────────────────────────────────────

class TestGraphController:
    """Test suite for graph controller"""
    
    def setup_method(self):
        """Setup graph controller"""
        self.controller = GraphController(checkpoint_dir="/tmp/test_checkpoints")
    
    def test_initial_state(self):
        """Test initial state"""
        status = self.controller.get_status()
        assert status['execution_state'] == ExecutionState.IDLE.value
    
    def test_pause_execution(self):
        """Test pausing execution"""
        success = self.controller.pause_execution("researcher")
        assert success
        assert self.controller.pause_points["researcher"] == True
    
    def test_resume_execution(self):
        """Test resuming execution"""
        self.controller.pause_execution("researcher")
        success = self.controller.resume_execution("researcher")
        assert success
        assert self.controller.pause_points["researcher"] == False
    
    def test_pause_all(self):
        """Test pausing all nodes"""
        self.controller.pause_all()
        for paused in self.controller.pause_points.values():
            assert paused == True
    
    def test_resume_all(self):
        """Test resuming all nodes"""
        self.controller.pause_all()
        self.controller.resume_all()
        for paused in self.controller.pause_points.values():
            assert paused == False
    
    def test_checkpoint_creation(self):
        """Test checkpoint creation"""
        snapshot_id = self.controller.create_checkpoint(
            state_name="test_state",
            state_data={"key": "value"},
            agent_id="test_agent",
            task_id="test_task"
        )
        assert snapshot_id is not None
        assert self.controller.current_snapshot is not None
    
    def test_checkpoint_restore(self):
        """Test checkpoint restoration"""
        snapshot_id = self.controller.create_checkpoint(
            state_name="test_state",
            state_data={"key": "value"},
            agent_id="test_agent",
            task_id="test_task"
        )
        
        restored = self.controller.restore_from_checkpoint(snapshot_id)
        assert restored is not None
        assert restored['key'] == "value"


# ──────────────────────────────────────────────────────────────────
# INTERRUPT MANAGER TESTS
# ──────────────────────────────────────────────────────────────────

class TestInterruptManager:
    """Test suite for interrupt manager"""
    
    def setup_method(self):
        """Setup interrupt manager"""
        self.manager = InterruptManager()
    
    def test_add_interrupt(self):
        """Test adding interrupt"""
        interrupt_id = self.manager.add_interrupt("researcher", "Test interruption")
        assert interrupt_id is not None
    
    def test_pending_interrupts(self):
        """Test getting pending interrupts"""
        self.manager.add_interrupt("researcher", "Test 1")
        self.manager.add_interrupt("auditor", "Test 2")
        
        pending = self.manager.get_pending_interrupts()
        assert len(pending) == 2
    
    def test_resolve_interrupt(self):
        """Test resolving interrupt"""
        interrupt_id = self.manager.add_interrupt("researcher", "Test")
        
        success = self.manager.resolve_interrupt(interrupt_id)
        assert success
        
        pending = self.manager.get_pending_interrupts()
        assert len(pending) == 0


# ──────────────────────────────────────────────────────────────────
# HIVE COUNCIL MERITOCRACY INTEGRATION TESTS
# ──────────────────────────────────────────────────────────────────

class TestHiveCouncilMeritocracy:
    """Test suite for HiveCouncil meritocracy integration"""
    
    def setup_method(self):
        """Setup hive council"""
        self.hive = get_hive_council()
    
    def test_leaderboard_available(self):
        """Test leaderboard is available"""
        leaderboard = self.hive.get_leaderboard()
        assert isinstance(leaderboard, list)
        # Should have at least 4 agents from council initialization
        assert len(leaderboard) >= 4
    
    def test_agent_metrics(self):
        """Test getting agent metrics"""
        from src.agents.hive_council import AgentRole
        agent_id = AgentRole.SENIOR_ARCHITECT.value
        
        metrics = self.hive.get_agent_metrics(agent_id)
        assert metrics is not None
        assert metrics['agent_id'] == agent_id
    
    def test_meritocracy_db_connection(self):
        """Test meritocracy db is connected"""
        assert self.hive.meritocracy_db is not None
        agents = self.hive.meritocracy_db.get_all_agents()
        assert len(agents) >= 4


# ──────────────────────────────────────────────────────────────────
# API ENDPOINT TESTS
# ──────────────────────────────────────────────────────────────────

class TestMeritocracyAPI:
    """Test suite for meritocracy API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        from fastapi.testclient import TestClient
        self.client = TestClient(app)
    
    def test_leaderboard_endpoint(self):
        """Test leaderboard endpoint"""
        response = self.client.get("/meritocracy/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        assert "rank_count" in data
    
    def test_agent_of_the_day_endpoint(self):
        """Test Agent of the Day endpoint"""
        response = self.client.get("/meritocracy/agent-of-the-day")
        assert response.status_code == 200
        data = response.json()
        assert "agent_of_the_day" in data
    
    def test_all_agents_endpoint(self):
        """Test all agents endpoint"""
        response = self.client.get("/meritocracy/all-agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "agent_count" in data
    
    def test_export_endpoint(self):
        """Test export endpoint"""
        response = self.client.get("/meritocracy/export")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


# ──────────────────────────────────────────────────────────────────
# RUN TESTS
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run with: python -m pytest tests/test_sovereign_components.py -v
    pytest.main([__file__, "-v", "--tb=short"])
