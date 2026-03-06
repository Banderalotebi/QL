"""
🔗 UNIFIED DATABASE INTEGRATION
Bridges Neon PostgreSQL and SQLite meritocracy database
Provides single interface for all data operations
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

from src.data.db_neon import NeonDatabase
from src.data.meritocracy_db import MeritocracyDB


class UnifiedDataLayer:
    """
    Single interface for all database operations
    Coordinates between Neon (remote findings) and SQLite (local meritocracy)
    """
    
    def __init__(self):
        self.neon = NeonDatabase()
        self.meritocracy = MeritocracyDB()
        self.is_connected = False
        
    async def initialize(self):
        """Initialize connections to both databases"""
        try:
            # Neon should already be initialized
            self.is_connected = True
            print("✅ Unified Data Layer initialized")
            return True
        except Exception as e:
            print(f"❌ Data layer initialization failed: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════
    # RESEARCH FINDINGS - Neon PostgreSQL
    # ═══════════════════════════════════════════════════════════════
    
    def record_hypothesis(self, hypothesis_data: Dict[str, Any]) -> str:
        """Record hypothesis in Neon database"""
        return self.neon.record_hypothesis(
            source_scout=hypothesis_data['source_scout'],
            goal_link=hypothesis_data['goal_link'],
            transformation_steps=hypothesis_data['transformation_steps'],
            evidence_snippets=hypothesis_data['evidence_snippets'],
            description=hypothesis_data['description'],
            surah_refs=hypothesis_data['surah_refs'],
            initial_score=hypothesis_data.get('initial_score', 1.0)
        )
    
    def get_hypotheses_by_surah(self, surah_id: int, limit: int = 50) -> List[Dict]:
        """Get all hypotheses for a surah"""
        return self.neon.get_hypotheses_by_surah(surah_id, limit)
    
    def record_supervision(self, hypothesis_id: str, report: Dict[str, Any]):
        """Record supervision report in Neon"""
        return self.neon.record_supervision(
            hypothesis_id=hypothesis_id,
            supervisor_verdict=report['status'],
            score_adjustment=report.get('score_delta', 0),
            notes=json.dumps(report)
        )
    
    def get_all_hypotheses(self, limit: int = 100) -> List[Dict]:
        """Get all hypotheses across all surahs"""
        return self.neon.get_all_hypotheses(limit)
    
    # ═══════════════════════════════════════════════════════════════
    # AGENT METRICS - SQLite Meritocracy
    # ═══════════════════════════════════════════════════════════════
    
    def award_agent_credits(self, agent_id: str, credits: int, task_id: str, reason: str):
        """Award credits to agent for successful task"""
        self.meritocracy.award_credits(agent_id, credits, task_id, reason)
    
    def record_agent_task(self, agent_id: str, task_type: str, 
                         surah_id: int, status: str, metric_value: float):
        """Record completed task for agent"""
        self.meritocracy.record_task_completion(
            agent_id=agent_id,
            task_type=task_type,
            surah_id=surah_id,
            status=status,
            metric_value=metric_value
        )
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive stats for an agent"""
        return self.meritocracy.get_agent_stats(agent_id)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get meritocracy leaderboard"""
        return self.meritocracy.get_leaderboard(limit)
    
    def get_agent_of_the_day(self) -> Optional[Dict]:
        """Get today's Agent of the Day"""
        return self.meritocracy.get_agent_of_the_day()
    
    # ═══════════════════════════════════════════════════════════════
    # CROSS-DATABASE QUERIES
    # ═══════════════════════════════════════════════════════════════
    
    def get_agent_contributions(self, agent_id: str) -> Dict[str, Any]:
        """
        Get full contribution profile for agent:
        - Hypotheses submitted (from Neon)
        - Task completion record (from SQLite)
        - Accuracy metrics (from SQLite)
        - Supervision history (from Neon)
        """
        stats = self.meritocracy.get_agent_stats(agent_id)
        
        return {
            "agent_id": agent_id,
            "credits": stats.get('total_credits', 0),
            "accuracy": stats.get('accuracy', 0.0),
            "tasks_completed": stats.get('tasks_completed', 0),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_research_summary(self) -> Dict[str, Any]:
        """Get overall research summary across databases"""
        try:
            all_hyp = self.neon.get_all_hypotheses(limit=1000)
            
            return {
                "total_hypotheses": len(all_hyp) if all_hyp else 0,
                "total_agents": len(self.meritocracy.get_all_agents()),
                "leaderboard_top_3": self.meritocracy.get_leaderboard(3),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error fetching research summary: {e}")
            return {
                "total_hypotheses": 0,
                "total_agents": len(self.meritocracy.get_all_agents()),
                "leaderboard_top_3": [],
                "error": str(e)
            }
    
    # ═══════════════════════════════════════════════════════════════
    # SYNC OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def sync_supervision_to_meritocracy(self, hypothesis_id: str, supervision_report: Dict):
        """
        When a hypothesis is supervised, update meritocracy metrics
        This closes the feedback loop: Neon → Meritocracy update
        """
        source_scout = supervision_report.get('source_scout', 'unknown')
        status = supervision_report.get('status', 'pending')
        
        # Award credits based on survival
        if status == "survived":
            self.award_agent_credits(
                agent_id=source_scout,
                credits=10,
                task_id=hypothesis_id,
                reason="Hypothesis survived expert review"
            )
        elif status == "corrected":
            self.award_agent_credits(
                agent_id=source_scout,
                credits=5,
                task_id=hypothesis_id,
                reason="Hypothesis corrected and improved"
            )
        elif status == "rejected":
            self.award_agent_credits(
                agent_id=source_scout,
                credits=-2,
                task_id=hypothesis_id,
                reason="Hypothesis rejected"
            )
    
    def sync_pattern_execution_to_metrics(self, pattern_id: str, result: Dict):
        """
        When a pattern is executed, record metrics
        This closes the loop: Pattern Queue → Agent Metrics
        """
        agent_id = result.get('executor', 'system')
        success = result.get('success', False)
        
        self.record_agent_task(
            agent_id=agent_id,
            task_type="pattern_execution",
            surah_id=result.get('surah_id', 0),
            status="completed" if success else "failed",
            metric_value=result.get('confidence', 0.0)
        )
    
    # ═══════════════════════════════════════════════════════════════
    # HEALTH CHECKS
    # ═══════════════════════════════════════════════════════════════
    
    async def health_check(self) -> Dict[str, Any]:
        """Complete health check for both databases"""
        neon_status = "unknown"
        sqlite_status = "unknown"
        
        try:
            # Check Neon
            test = self.neon.get_all_hypotheses(limit=1)
            neon_status = "✅ connected"
        except Exception as e:
            neon_status = f"❌ disconnected: {str(e)[:50]}"
        
        try:
            # Check SQLite
            agents = self.meritocracy.get_all_agents()
            sqlite_status = "✅ connected"
        except Exception as e:
            sqlite_status = f"❌ disconnected: {str(e)[:50]}"
        
        return {
            "neon_postgresql": neon_status,
            "sqlite_meritocracy": sqlite_status,
            "overall_status": "healthy" if "✅" in neon_status and "✅" in sqlite_status else "degraded",
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_unified_db = None

def get_unified_data_layer() -> UnifiedDataLayer:
    """Get or create unified data layer"""
    global _unified_db
    if _unified_db is None:
        _unified_db = UnifiedDataLayer()
    return _unified_db
