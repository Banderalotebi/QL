"""
Meritocracy Ledger Database
SQLite-backed reward and performance tracking system for agents in the Hive.
Tracks agent credits, accuracy scores, tasks completed, and daily leaderboard.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class MeritocracyDB:
    """
    SQLite database for tracking agent performance, rewards, and meritocracy.
    
    Tables:
    - agent_registry: Core agent profiles (credits, accuracy, activity)
    - reward_logs: Audit trail of all credit awards
    - agent_of_the_day: Daily leaderboard results
    - task_metrics: Per-task performance tracking
    """
    
    def __init__(self, db_path: str = "/workspaces/QL/data/processed/meritocracy.db"):
        """Initialize the meritocracy database."""
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()
        logger.info(f"Meritocracy DB initialized at {self.db_path}")
    
    def _initialize_schema(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Agent Registry: Core agent profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_registry (
                agent_id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                total_credits INTEGER DEFAULT 0,
                accuracy_score REAL DEFAULT 0.0,
                tasks_completed INTEGER DEFAULT 0,
                tasks_successful INTEGER DEFAULT 0,
                last_active TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Reward Logs: Audit trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reward_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                reward_amount INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                FOREIGN KEY(agent_id) REFERENCES agent_registry(agent_id)
            )
        """)
        
        # Agent of the Day: Daily leaderboard
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_of_the_day (
                date DATE PRIMARY KEY,
                agent_id TEXT NOT NULL,
                performance_score REAL NOT NULL,
                achievement_summary TEXT,
                patternstask_count INTEGER,
                FOREIGN KEY(agent_id) REFERENCES agent_registry(agent_id)
            )
        """)
        
        # Task Metrics: Per-task performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_metrics (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                task_type TEXT,
                pattern_id TEXT,
                surah_id INTEGER,
                status TEXT,
                execution_time_ms REAL,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agent_id) REFERENCES agent_registry(agent_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON agent_registry(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reward_agent ON reward_logs(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_agent ON task_metrics(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_created ON task_metrics(created_at)")
        
        self.conn.commit()
        logger.info("Meritocracy schema initialized")
    
    def register_agent(self, agent_id: str, role: str, initial_credits: int = 1000) -> bool:
        """Register a new agent in the ledger."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO agent_registry 
                (agent_id, role, total_credits, accuracy_score, tasks_completed, last_active)
                VALUES (?, ?, ?, 0.0, 0, ?)
            """, (agent_id, role, initial_credits, datetime.now()))
            self.conn.commit()
            logger.info(f"Registered agent: {agent_id} with role: {role}")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def award_credits(self, agent_id: str, amount: int, reason: str = "", created_by: str = "system") -> bool:
        """Award credits to an agent."""
        cursor = self.conn.cursor()
        try:
            # Record in reward log
            cursor.execute("""
                INSERT INTO reward_logs (agent_id, reward_amount, reason, created_by)
                VALUES (?, ?, ?, ?)
            """, (agent_id, amount, reason, created_by))
            
            # Update agent's total credits
            cursor.execute("""
                UPDATE agent_registry
                SET total_credits = total_credits + ?,
                    last_active = ?
                WHERE agent_id = ?
            """, (amount, datetime.now(), agent_id))
            
            self.conn.commit()
            logger.info(f"Awarded {amount} credits to {agent_id}: {reason}")
            return True
        except Exception as e:
            logger.error(f"Failed to award credits to {agent_id}: {e}")
            return False
    
    def update_accuracy_score(self, agent_id: str, accuracy: float) -> bool:
        """Update an agent's accuracy score."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE agent_registry
                SET accuracy_score = ?, last_active = ?
                WHERE agent_id = ?
            """, (accuracy, datetime.now(), agent_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update accuracy for {agent_id}: {e}")
            return False
    
    def record_task_completion(self, agent_id: str, task_type: str = "pattern", 
                             pattern_id: str = "", surah_id: int = 0,
                             status: str = "success", execution_time_ms: float = 0,
                             confidence_score: float = 0.0) -> bool:
        """Record a completed task for metrics tracking."""
        cursor = self.conn.cursor()
        try:
            # Insert task metric
            cursor.execute("""
                INSERT INTO task_metrics 
                (agent_id, task_type, pattern_id, surah_id, status, execution_time_ms, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (agent_id, task_type, pattern_id, surah_id, status, execution_time_ms, confidence_score))
            
            # Update agent's task counts
            successful = 1 if status == "success" else 0
            cursor.execute("""
                UPDATE agent_registry
                SET tasks_completed = tasks_completed + 1,
                    tasks_successful = tasks_successful + ?,
                    last_active = ?
                WHERE agent_id = ?
            """, (successful, datetime.now(), agent_id))
            
            # Award small bounty for task completion
            if status == "success":
                cursor.execute("""
                    INSERT INTO reward_logs (agent_id, reward_amount, reason, created_by)
                    VALUES (?, 10, 'Task completion bonus', 'system')
                """, (agent_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to record task for {agent_id}: {e}")
            return False
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top agents by combined performance metric."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT agent_id, role, total_credits, accuracy_score, tasks_completed, tasks_successful
                FROM agent_registry
                ORDER BY total_credits DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch leaderboard: {e}")
            return []
    
    def get_agent_metrics(self, agent_id: str) -> Optional[Dict]:
        """Get detailed metrics for a specific agent."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT agent_id, role, total_credits, accuracy_score, 
                       tasks_completed, tasks_successful, last_active
                FROM agent_registry
                WHERE agent_id = ?
            """, (agent_id,))
            
            row = cursor.fetchone()
            if row:
                metrics = dict(row)
                metrics['success_rate'] = (
                    metrics['tasks_successful'] / metrics['tasks_completed'] 
                    if metrics['tasks_completed'] > 0 else 0.0
                )
                return metrics
            return None
        except Exception as e:
            logger.error(f"Failed to fetch metrics for {agent_id}: {e}")
            return None
    
    def calculate_agent_of_the_day(self) -> Optional[str]:
        """Calculate today's top agent using performance scoring."""
        cursor = self.conn.cursor()
        today = datetime.now().date()
        
        try:
            # Performance index: (accurate_tasks * 0.4) + (accuracy_score * 0.6)
            cursor.execute("""
                SELECT 
                    agent_id,
                    (tasks_successful * 0.4 + accuracy_score * 0.6) as performance_score,
                    tasks_completed
                FROM agent_registry
                WHERE tasks_completed > 0
                ORDER BY performance_score DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                winner_id = result['agent_id']
                performance_score = result['performance_score']
                task_count = result['tasks_completed']
                
                # Record in agent_of_the_day table
                cursor.execute("""
                    INSERT OR REPLACE INTO agent_of_the_day
                    (date, agent_id, performance_score, achievement_summary, patternstask_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    today,
                    winner_id,
                    performance_score,
                    f"Achieved performance score of {performance_score:.2f} with {task_count} tasks",
                    task_count
                ))
                
                # Award bonus credits
                cursor.execute("""
                    INSERT INTO reward_logs (agent_id, reward_amount, reason, created_by)
                    VALUES (?, 500, 'Agent of the Day bonus', 'system')
                """, (winner_id,))
                
                # Update agent's credits
                cursor.execute("""
                    UPDATE agent_registry
                    SET total_credits = total_credits + 500
                    WHERE agent_id = ?
                """, (winner_id,))
                
                self.conn.commit()
                logger.info(f"Agent of the Day: {winner_id} (score: {performance_score:.2f})")
                return winner_id
            
            return None
        except Exception as e:
            logger.error(f"Failed to calculate Agent of the Day: {e}")
            return None
    
    def get_today_agent_of_the_day(self) -> Optional[Dict]:
        """Get today's Agent of the Day record."""
        cursor = self.conn.cursor()
        today = datetime.now().date()
        
        try:
            cursor.execute("""
                SELECT agent_id, performance_score, achievement_summary, patternstask_count
                FROM agent_of_the_day
                WHERE date = ?
            """, (today,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to fetch today's Agent of the Day: {e}")
            return None
    
    def get_agent_history(self, agent_id: str, days: int = 7) -> List[Dict]:
        """Get recent reward/activity history for an agent."""
        cursor = self.conn.cursor()
        since_date = datetime.now() - timedelta(days=days)
        
        try:
            cursor.execute("""
                SELECT agent_id, reward_amount, reason, timestamp, created_by
                FROM reward_logs
                WHERE agent_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (agent_id, since_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch history for {agent_id}: {e}")
            return []
    
    def get_all_agents(self) -> List[Dict]:
        """Get all registered agents."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT agent_id, role, total_credits, accuracy_score, 
                       tasks_completed, tasks_successful, last_active
                FROM agent_registry
                ORDER BY total_credits DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch all agents: {e}")
            return []
    
    def reset_daily_metrics(self) -> bool:
        """Reset daily task counts at midnight (for Agent of the Day calculations)."""
        cursor = self.conn.cursor()
        try:
            # This would be called by a scheduler at midnight
            # For now, just ensure Agent of Day calculation runs
            self.calculate_agent_of_the_day()
            return True
        except Exception as e:
            logger.error(f"Failed to reset daily metrics: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info("Meritocracy DB closed")
    
    def export_metrics(self) -> Dict:
        """Export all metrics for logging/reporting."""
        return {
            "agents": self.get_all_agents(),
            "leaderboard": self.get_leaderboard(limit=10),
            "agent_of_the_day": self.get_today_agent_of_the_day(),
            "timestamp": str(datetime.now())
        }


# Global instance
_meritocracy_db: Optional[MeritocracyDB] = None


def get_meritocracy_db() -> MeritocracyDB:
    """Get or create global meritocracy database instance."""
    global _meritocracy_db
    if _meritocracy_db is None:
        _meritocracy_db = MeritocracyDB()
    return _meritocracy_db
