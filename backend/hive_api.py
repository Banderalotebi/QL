"""
🌐 FASTAPI INTEGRATION - BRIDGE HIVE TO FRONTEND
Expose the Council of Experts via REST API
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
import asyncio
import json
from datetime import datetime

from src.agents.hive_council import get_hive_council
from src.core.state import Hypothesis
from src.utils.arabic import MUQATTAAT_SURAH_NUMBERS
from src.data.meritocracy_db import get_meritocracy_db
from frontend.components.pattern_web import get_pattern_web_visualizer
from src.core.langgraph_control import get_graph_controller, get_interrupt_manager

# FastAPI app
app = FastAPI(
    title="Muqattaat Hive API",
    description="REST API for the Council of Experts",
    version="1.0.0"
)

# Models for request/response
class ScanRequest(BaseModel):
    surah_id: int
    scan_type: str = "single"  # "single", "range", "all_muqattaat"
    start_surah: Optional[int] = None
    end_surah: Optional[int] = None
    execution_mode: str = "mathematical"  # "mathematical", "crewai", "hybrid"


class HypothesisRequest(BaseModel):
    source_scout: str
    goal_link: str
    transformation_steps: int
    evidence_snippets: List[str]
    description: str
    surah_refs: List[int]


class SupervisionRequest(BaseModel):
    hypothesis: HypothesisRequest
    surah_num: int


class AgentThoughtRequest(BaseModel):
    agent_role: str
    thought: str
    confidence: float
    decision: str
    evidence: List[str]


# ──────────────────────────────────────────
# HEALTH & STATUS ENDPOINTS
# ──────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint - redirects to API documentation"""
    return {
        "message": "Muqattaat Hive API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "/status"
    }


@app.get("/health")
async def health_check():
    """Check if the hive is operational"""
    hive = get_hive_council()
    return {
        "status": "healthy",
        "hive_operational": True,
        "timestamp": datetime.now().isoformat(),
        "hive_status": hive.get_hive_status()
    }


@app.get("/status")
async def get_status():
    """Get detailed hive status"""
    hive = get_hive_council()
    return {
        "status": "operational",
        "hive_council": hive.get_hive_status(),
        "thoughts_logged": len(hive.thoughts_log),
        "supervision_reports": len(hive.supervision_reports),
        "shared_memory_keys": list(hive.shared_memory.keys())
    }


# ──────────────────────────────────────────
# SUPERVISION ENDPOINTS
# ──────────────────────────────────────────

@app.post("/supervise")
async def supervise_hypothesis(request: SupervisionRequest):
    """
    Submit a hypothesis for expert supervision
    Returns: Supervision report with corrections and final score
    """
    hive = get_hive_council()
    
    try:
        # Convert request to Hypothesis object
        hyp = Hypothesis(
            source_scout=request.hypothesis.source_scout,
            goal_link=request.hypothesis.goal_link,
            transformation_steps=request.hypothesis.transformation_steps,
            evidence_snippets=request.hypothesis.evidence_snippets,
            description=request.hypothesis.description,
            surah_refs=request.hypothesis.surah_refs,
            score=1.0  # Initial score
        )
        
        # Run supervision
        report = hive.supervise_hypothesis(hyp, request.surah_num)
        
        return {
            "status": "supervised",
            "report": {
                "worker_agent": report.worker_agent,
                "expert_agent": report.expert_agent,
                "status": report.status,
                "final_score": report.final_score,
                "corrections_applied": report.corrections_applied,
                "original_score": hyp.score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/supervisions/recent")
async def get_recent_supervisions(limit: int = 50):
    """Get recent supervision reports"""
    hive = get_hive_council()
    
    reports = hive.supervision_reports[-limit:]
    return {
        "count": len(reports),
        "reports": [
            {
                "worker": r.worker_agent,
                "expert": r.expert_agent,
                "status": r.status,
                "final_score": r.final_score
            }
            for r in reports
        ]
    }


@app.get("/supervisions/statistics")
async def get_supervision_statistics():
    """Get supervision statistics"""
    hive = get_hive_council()
    
    if not hive.supervision_reports:
        return {
            "total": 0,
            "approved": 0,
            "revised": 0,
            "rejected": 0,
            "average_score": 0
        }
    
    reports = hive.supervision_reports
    statuses = {r.status: 0 for r in reports}
    
    for r in reports:
        statuses[r.status] = statuses.get(r.status, 0) + 1
    
    avg_score = sum(r.final_score for r in reports) / len(reports)
    
    return {
        "total": len(reports),
        "approved": statuses.get("APPROVED", 0),
        "revised": statuses.get("REVISED", 0),
        "rejected": statuses.get("REJECTED", 0),
        "average_score": round(avg_score, 4),
        "approval_rate": round(statuses.get("APPROVED", 0) / len(reports), 2)
    }


# ──────────────────────────────────────────
# SCANNING ENDPOINTS
# ──────────────────────────────────────────

@app.post("/scan")
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start a deep scan using the hive
    Returns: Scan ID and status
    """
    hive = get_hive_council()
    
    # Determine which surahs to scan
    if request.scan_type == "single":
        surahs = [request.surah_id]
    elif request.scan_type == "range":
        surahs = list(range(request.start_surah, request.end_surah + 1))
    elif request.scan_type == "all_muqattaat":
        surahs = list(MUQATTAAT_SURAH_NUMBERS)
    else:
        raise HTTPException(status_code=400, detail="Invalid scan_type")
    
    # Filter to only Muqattaat surahs
    surahs = [s for s in surahs if s in MUQATTAAT_SURAH_NUMBERS]
    
    if not surahs:
        raise HTTPException(status_code=400, detail="No valid Muqattaat surahs in range")
    
    scan_id = f"SCAN_{datetime.now().timestamp()}"
    
    # Validate execution mode
    if request.execution_mode not in ["mathematical", "crewai", "hybrid"]:
        raise HTTPException(status_code=400, detail="Invalid execution_mode")
    
    # Schedule background scan
    async def run_scan():
        for surah in surahs:
            # Get Muqattaat sequence for this surah
            muqattaat_map = {
                2: "ALM", 3: "ALM", 7: "ALMS", 10: "ALR",
                11: "ALR", 12: "ALR", 13: "ALMS", 14: "ALR",
                15: "ALR", 19: "KHY", 20: "HA", 26: "TSM",
                27: "TS", 28: "TSM", 29: "ALMS"
            }
            
            muqattaat_seq = muqattaat_map.get(surah, "UNKNOWN")
            
            # Run orchestrated deep scan
            result = hive.orchestrate_deep_scan(surah, muqattaat_seq)
            
            # Log result
            print(f"✅ Scanned Surah {surah}: {result}")
            
            await asyncio.sleep(0.1)  # Small delay between scans
    
    # Add to background tasks
    background_tasks.add_task(run_scan)
    
    return {
        "scan_id": scan_id,
        "status": "initiated",
        "surahs": surahs,
        "execution_mode": request.execution_mode,
        "estimated_duration_seconds": len(surahs) * 5
    }


@app.get("/scans/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get status of a specific scan"""
    # In a production system, would track scan status in database
    return {
        "scan_id": scan_id,
        "status": "in_progress",
        "progress_percent": 45,
        "surahs_completed": 15,
        "surahs_total": 29
    }


# ──────────────────────────────────────────
# THOUGHT LOGGING ENDPOINTS
# ──────────────────────────────────────────

@app.post("/thoughts")
async def log_thought(request: AgentThoughtRequest):
    """Log an agent's internal thought"""
    hive = get_hive_council()
    
    hive.log_thought(
        agent_role=request.agent_role,
        thought=request.thought,
        confidence=request.confidence,
        decision=request.decision,
        evidence=request.evidence
    )
    
    return {
        "status": "logged",
        "agent": request.agent_role,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/thoughts/recent")
async def get_recent_thoughts(limit: int = 50):
    """Get recent agent thoughts"""
    hive = get_hive_council()
    
    thoughts = hive.thoughts_log[-limit:]
    return {
        "count": len(thoughts),
        "thoughts": [
            {
                "agent": t.agent_role,
                "timestamp": t.timestamp,
                "thought": t.thought[:100],
                "confidence": t.confidence,
                "decision": t.decision
            }
            for t in thoughts
        ]
    }


# ──────────────────────────────────────────
# MEMORY ENDPOINTS
# ──────────────────────────────────────────

@app.get("/memory")
async def get_shared_memory():
    """Get shared hive memory"""
    hive = get_hive_council()
    
    return {
        "verified_patterns": hive.shared_memory.get("verified_patterns", []),
        "known_errors": hive.shared_memory.get("known_errors", []),
        "optimization_tips": hive.shared_memory.get("optimization_tips", []),
        "style_guide": hive.shared_memory.get("style_guide", {})
    }


@app.post("/memory/pattern")
async def add_verified_pattern(pattern: str):
    """Add a pattern to shared memory"""
    hive = get_hive_council()
    
    if pattern not in hive.shared_memory["verified_patterns"]:
        hive.shared_memory["verified_patterns"].append(pattern)
        hive._save_shared_memory()
    
    return {
        "status": "added",
        "pattern": pattern,
        "total_verified": len(hive.shared_memory["verified_patterns"])
    }


@app.post("/memory/error")
async def log_known_error(error: str):
    """Log a known error to shared memory"""
    hive = get_hive_council()
    
    if error not in hive.shared_memory["known_errors"]:
        hive.shared_memory["known_errors"].append(error)
        hive._save_shared_memory()
    
    return {
        "status": "logged",
        "error": error,
        "total_known": len(hive.shared_memory["known_errors"])
    }


# ──────────────────────────────────────────
# HIVE STATE ENDPOINTS
# ──────────────────────────────────────────

@app.post("/hive/save")
async def save_hive_state():
    """Save current hive state to persistent storage"""
    hive = get_hive_council()
    hive.save_hive_state()
    
    return {
        "status": "saved",
        "timestamp": datetime.now().isoformat(),
        "thoughts_count": len(hive.thoughts_log),
        "supervisions_count": len(hive.supervision_reports)
    }


@app.get("/hive/info")
async def get_hive_info():
    """Get comprehensive hive information"""
    hive = get_hive_council()
    
    return {
        "hive_status": hive.get_hive_status(),
        "total_thoughts": len(hive.thoughts_log),
        "total_supervisions": len(hive.supervision_reports),
        "shared_memory": hive.shared_memory,
        "crewai_available": hive.crewai_initialized,
        "database_connected": hive.db.is_connected
    }


# ──────────────────────────────────────────
# MERITOCRACY ENDPOINTS
# ──────────────────────────────────────────

@app.get("/meritocracy/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get agent leaderboard ranked by total credits"""
    hive = get_hive_council()
    leaderboard = hive.get_leaderboard(limit)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "rank_count": len(leaderboard),
        "leaderboard": leaderboard
    }


@app.get("/meritocracy/agent-of-the-day")
async def get_agent_of_the_day():
    """Get today's Agent of the Day"""
    hive = get_hive_council()
    aotd = hive.get_agent_of_the_day()
    
    if not aotd:
        aotd = {"agent_id": "None", "performance_score": 0, "achievement_summary": "No agent selected yet"}
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "agent_of_the_day": aotd
    }


@app.post("/meritocracy/calculate-agent-of-the-day")
async def calculate_agent_of_the_day():
    """Calculate and update today's Agent of the Day"""
    hive = get_hive_council()
    winner = hive.calculate_agent_of_the_day()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "agent_of_the_day": winner,
        "message": f"{winner} has been crowned Agent of the Day!" if winner else "No agents eligible yet"
    }


@app.get("/meritocracy/agent/{agent_id}")
async def get_agent_metrics(agent_id: str):
    """Get detailed metrics for a specific agent"""
    hive = get_hive_council()
    metrics = hive.get_agent_metrics(agent_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "metrics": metrics
    }


@app.post("/meritocracy/award-credits/{agent_id}")
async def award_credits(agent_id: str, amount: int, reason: str = ""):
    """Award credits to an agent"""
    db = get_meritocracy_db()
    
    success = db.award_credits(agent_id, amount, reason, "admin")
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to award credits to {agent_id}")
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "credits_awarded": amount,
        "reason": reason,
        "message": f"{amount} credits awarded to {agent_id}!"
    }


@app.get("/meritocracy/all-agents")
async def get_all_agents():
    """Get all registered agents with their metrics"""
    hive = get_hive_council()
    db = get_meritocracy_db()
    
    agents = db.get_all_agents()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "agent_count": len(agents),
        "agents": agents
    }


@app.get("/meritocracy/agent/{agent_id}/history")
async def get_agent_history(agent_id: str, days: int = 7):
    """Get reward history for an agent"""
    db = get_meritocracy_db()
    
    history = db.get_agent_history(agent_id, days)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "days": days,
        "reward_count": len(history),
        "history": history
    }


@app.get("/meritocracy/export")
async def export_meritocracy_data():
    """Export all meritocracy statistics"""
    hive = get_hive_council()
    db = get_meritocracy_db()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": db.export_metrics()
    }


# ──────────────────────────────────────────
# PATTERN WEB & QUEUE ENDPOINTS
# ──────────────────────────────────────────

@app.get("/patterns/stats")
async def get_pattern_stats():
    """Return statistics about the pattern web"""
    visualizer = get_pattern_web_visualizer()
    return visualizer.get_statistics()


@app.get("/patterns/graph")
async def export_pattern_graph():
    """Export the graph JSON for frontend visualization"""
    visualizer = get_pattern_web_visualizer()
    return visualizer.export_graph_json()


@app.get("/patterns/queue")
async def get_pattern_queue():
    """Get current execution queue status"""
    visualizer = get_pattern_web_visualizer()
    return visualizer.get_queue_status()


@app.post("/patterns/queue/add/{pattern_id}")
async def add_pattern_to_queue(pattern_id: str):
    """Add a pattern to the execution queue"""
    visualizer = get_pattern_web_visualizer()
    success = visualizer.add_pattern_to_queue(pattern_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")
    return {"status": "added", "pattern_id": pattern_id}


@app.post("/patterns/queue/execute")
async def execute_pattern_queue():
    """Execute all patterns in the queue"""
    visualizer = get_pattern_web_visualizer()
    result = visualizer.execute_queue()
    return {"status": "executed", **result}


@app.post("/patterns/queue/clear")
async def clear_pattern_queue():
    """Clear the pattern execution queue"""
    visualizer = get_pattern_web_visualizer()
    visualizer.execution_queue.clear()
    return {"status": "cleared", "queue_size": 0}


@app.get("/patterns/similar/{pattern_id}")
async def get_similar_patterns(pattern_id: str, top_n: int = 5):
    """Get similar patterns to a given id"""
    visualizer = get_pattern_web_visualizer()
    similar = visualizer.get_pattern_similarity(pattern_id, top_n)
    return {"pattern_id": pattern_id, "similar": similar}


# ──────────────────────────────────────────
# BROADCAST ENDPOINTS
# ──────────────────────────────────────────

@app.post("/broadcast")
async def broadcast_knowledge(tipo: str, content: str, priority: str = "normal", sender: str = "system"):
    """Push a knowledge broadcast into hive memory"""
    hive = get_hive_council()
    # forward sender to the hive method so we can track origin
    message = hive.broadcast_knowledge(content, msg_type=tipo, priority=priority, sender=sender)
    return {"status": "broadcasted", "message": message}


@app.get("/broadcast/history")
async def get_broadcast_history():
    """Retrieve broadcast history"""
    hive = get_hive_council()
    return {"history": hive.get_broadcast_history()}


@app.get("/broadcast/pending")
async def get_pending_broadcasts():
    """Retrieve pending broadcasts"""
    hive = get_hive_council()
    return {"pending": hive.get_pending_broadcasts()}


@app.post("/broadcast/ack/{message_id}")
async def ack_broadcast(message_id: str, agent_id: str):
    """Acknowledge a broadcast message"""
    hive = get_hive_council()
    success = hive.acknowledge_broadcast(message_id, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "acknowledged", "message_id": message_id}


# ──────────────────────────────────────────
# CONTROL & CHECKPOINT ENDPOINTS
# ──────────────────────────────────────────

@app.get("/control/status")
async def control_status():
    controller = get_graph_controller()
    return controller.get_status()


@app.post("/control/pause-all")
async def pause_all():
    controller = get_graph_controller()
    controller.pause_all()
    return {"status": "paused_all"}


@app.post("/control/resume-all")
async def resume_all():
    controller = get_graph_controller()
    controller.resume_all()
    return {"status": "resumed_all"}


@app.post("/control/pause/{node_name}")
async def pause_node(node_name: str):
    controller = get_graph_controller()
    ok = controller.pause_execution(node_name)
    if not ok:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"status": "paused", "node": node_name}


@app.post("/control/resume/{node_name}")
async def resume_node(node_name: str):
    controller = get_graph_controller()
    ok = controller.resume_execution(node_name)
    if not ok:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"status": "resumed", "node": node_name}


@app.get("/checkpoints")
async def list_checkpoints():
    controller = get_graph_controller()
    return {"checkpoints": controller.get_checkpoint_list()}


@app.post("/checkpoints/create")
async def create_checkpoint(state_name: str = "manual"):
    controller = get_graph_controller()
    snap = controller.create_checkpoint(state_name=state_name, state_data={}, agent_id="api", task_id="api")
    return {"status": "created", "snapshot_id": snap}


@app.post("/checkpoints/restore/{snapshot_id}")
async def restore_checkpoint(snapshot_id: str):
    controller = get_graph_controller()
    data = controller.restore_from_checkpoint(snapshot_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return {"status": "restored", "data": data}


@app.get("/interrupts")
async def get_interrupts():
    mgr = get_interrupt_manager()
    return {"pending": mgr.get_pending_interrupts()}


@app.post("/interrupts/add/{node_name}")
async def add_interrupt(node_name: str, reason: str = ""):
    mgr = get_interrupt_manager()
    iid = mgr.add_interrupt(node_name, reason)
    return {"status": "added", "interrupt_id": iid}


# ──────────────────────────────────────────
# ERROR HANDLERS
# ──────────────────────────────────────────

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors gracefully"""
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
