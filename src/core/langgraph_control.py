"""
LangGraph Control System - Pause/Resume Checkpoint Management
State machine controls for orchestrating hive execution with interrupts
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionState(Enum):
    """States in the execution workflow"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    RESUMED = "resumed"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass
class ExecutionSnapshot:
    """Snapshot of execution state for checkpointing"""
    snapshot_id: str
    state_name: str
    state_data: Dict[str, Any]
    timestamp: str
    agent_id: str
    task_id: str
    is_checkpoint: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


class GraphController:
    """
    Controls LangGraph execution with pause/resume capabilities
    Manages checkpoints and state transitions
    """
    
    def __init__(self, checkpoint_dir: str = "/workspaces/QL/data/processed/checkpoints"):
        """Initialize graph controller"""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.execution_state = ExecutionState.IDLE
        self.current_snapshot: Optional[ExecutionSnapshot] = None
        self.snapshots: List[ExecutionSnapshot] = []
        self.pause_points: Dict[str, bool] = {
            "researcher": False,
            "auditor": False,
            "synthesizer": False
        }
        self.execution_history: List[Dict[str, Any]] = []
        self._load_checkpoints()
        logger.info("GraphController initialized")
    
    def _load_checkpoints(self):
        """Load checkpoints from disk"""
        try:
            checkpoint_files = list(self.checkpoint_dir.glob("*.json"))
            for file in sorted(checkpoint_files)[-10:]:  # Load last 10
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        snapshot = ExecutionSnapshot(**data)
                        self.snapshots.append(snapshot)
                except Exception as e:
                    logger.warning(f"Could not load checkpoint {file}: {e}")
        except Exception as e:
            logger.error(f"Error loading checkpoints: {e}")
    
    def create_checkpoint(self, state_name: str, state_data: Dict, agent_id: str, task_id: str) -> str:
        """Create a checkpoint of current execution state"""
        snapshot_id = f"SNAPSHOT_{datetime.now().timestamp()}"
        
        snapshot = ExecutionSnapshot(
            snapshot_id=snapshot_id,
            state_name=state_name,
            state_data=state_data,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            task_id=task_id,
            is_checkpoint=True
        )
        
        self.snapshots.append(snapshot)
        self.current_snapshot = snapshot
        
        # Save to disk
        snapshot_path = self.checkpoint_dir / f"{snapshot_id}.json"
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        
        logger.info(f"Created checkpoint {snapshot_id}")
        return snapshot_id
    
    def pause_execution(self, node_name: str) -> bool:
        """Set pause point before executing node"""
        if node_name in self.pause_points:
            self.pause_points[node_name] = True
            self.execution_state = ExecutionState.PAUSED
            logger.info(f"Pause set for node: {node_name}")
            return True
        return False
    
    def resume_execution(self, node_name: str) -> bool:
        """Resume execution from pause point"""
        if node_name in self.pause_points:
            self.pause_points[node_name] = False
            self.execution_state = ExecutionState.RESUMED
            logger.info(f"Resume from pause point: {node_name}")
            return True
        return False
    
    def pause_all(self) -> None:
        """Pause all execution nodes"""
        for node in self.pause_points:
            self.pause_points[node] = True
        self.execution_state = ExecutionState.PAUSED
        logger.info("All execution nodes paused")
    
    def resume_all(self) -> None:
        """Resume all execution nodes"""
        for node in self.pause_points:
            self.pause_points[node] = False
        self.execution_state = ExecutionState.RUNNING
        logger.info("All execution nodes resumed")
    
    def get_pause_status(self) -> Dict[str, bool]:
        """Get pause status for all nodes"""
        return self.pause_points.copy()
    
    def restore_from_checkpoint(self, snapshot_id: str) -> Optional[Dict]:
        """Restore state from a checkpoint"""
        snapshot = None
        for s in self.snapshots:
            if s.snapshot_id == snapshot_id:
                snapshot = s
                break
        
        if not snapshot:
            logger.warning(f"Checkpoint {snapshot_id} not found")
            return None
        
        self.current_snapshot = snapshot
        self.execution_state = ExecutionState.RESUMED
        logger.info(f"Restored from checkpoint {snapshot_id}")
        
        return snapshot.state_data
    
    def get_checkpoint_list(self) -> List[Dict]:
        """Get list of available checkpoints"""
        return [
            {
                "snapshot_id": s.snapshot_id,
                "state_name": s.state_name,
                "timestamp": s.timestamp,
                "agent_id": s.agent_id,
                "task_id": s.task_id
            }
            for s in sorted(self.snapshots, key=lambda x: x.timestamp, reverse=True)[:20]
        ]
    
    def record_execution(self, state_name: str, agent_id: str, result: str, duration_ms: float):
        """Record execution event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "state_name": state_name,
            "agent_id": agent_id,
            "result": result,
            "duration_ms": duration_ms
        }
        
        self.execution_history.append(event)
        logger.info(f"Recorded execution event: {state_name} -> {result}")
    
    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """Get execution history"""
        return self.execution_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current controller status"""
        return {
            "execution_state": self.execution_state.value,
            "pause_status": self.pause_points,
            "current_snapshot": self.current_snapshot.to_dict() if self.current_snapshot else None,
            "total_checkpoints": len(self.snapshots),
            "total_executions": len(self.execution_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def export_state(self) -> Dict:
        """Export complete state for logging"""
        return {
            "status": self.get_status(),
            "checkpoints": self.get_checkpoint_list(),
            "execution_history": self.get_execution_history(100),
            "timestamp": datetime.now().isoformat()
        }


class WorkflowInterrupt:
    """Represents an interrupt in the workflow"""
    
    def __init__(self, interrupt_id: str, node_name: str, reason: str):
        self.interrupt_id = interrupt_id
        self.node_name = node_name
        self.reason = reason
        self.timestamp = datetime.now().isoformat()
        self.resolved = False
    
    def resolve(self):
        """Mark interrupt as resolved"""
        self.resolved = True


class InterruptManager:
    """Manages workflow interrupts"""
    
    def __init__(self):
        self.interrupts: List[WorkflowInterrupt] = []
    
    def add_interrupt(self, node_name: str, reason: str) -> str:
        """Add an interrupt"""
        interrupt_id = f"INT_{datetime.now().timestamp()}"
        interrupt = WorkflowInterrupt(interrupt_id, node_name, reason)
        self.interrupts.append(interrupt)
        logger.info(f"Interrupt added: {node_name} - {reason}")
        return interrupt_id
    
    def resolve_interrupt(self, interrupt_id: str) -> bool:
        """Mark interrupt as resolved"""
        for interrupt in self.interrupts:
            if interrupt.interrupt_id == interrupt_id:
                interrupt.resolve()
                logger.info(f"Interrupt resolved: {interrupt_id}")
                return True
        return False
    
    def get_pending_interrupts(self) -> List[Dict]:
        """Get pending interrupts"""
        return [
            {
                "interrupt_id": i.interrupt_id,
                "node_name": i.node_name,
                "reason": i.reason,
                "timestamp": i.timestamp
            }
            for i in self.interrupts if not i.resolved
        ]


# Global instances
_graph_controller: Optional[GraphController] = None
_interrupt_manager: Optional[InterruptManager] = None


def get_graph_controller() -> GraphController:
    """Get or create global graph controller"""
    global _graph_controller
    if _graph_controller is None:
        _graph_controller = GraphController()
    return _graph_controller


def get_interrupt_manager() -> InterruptManager:
    """Get or create global interrupt manager"""
    global _interrupt_manager
    if _interrupt_manager is None:
        _interrupt_manager = InterruptManager()
    return _interrupt_manager
