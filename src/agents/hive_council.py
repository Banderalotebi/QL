"""
🏛️ HIERARCHICAL AGENT ARCHITECTURE - COUNCIL OF EXPERTS
Expert Supervision Loop with Worker-Expert Pairs
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import CrewAI, fallback gracefully if not available
try:
    from crewai import Agent, Task, Crew, Process
    from langchain_ollama import ChatOllama
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("⚠️  CrewAI not available - using fallback mathematical orchestration")

from src.agents.mathematical_auditor import get_math_auditor
from src.core.state import Hypothesis
from src.data.neon_db import NeonDB
from src.data.meritocracy_db import get_meritocracy_db


class AgentRole(Enum):
    """Agent role classification in the hive"""
    CRYPT_WORKER = "Crypt-Worker"
    SENIOR_ARCHITECT = "Senior Architect"
    LINGUISTIC_WORKER = "Linguistic-Worker"
    PHILOLOGIST = "Philologist"


@dataclass
class AgentThought:
    """Record of an agent's internal reasoning"""
    agent_role: str
    timestamp: str
    thought: str
    confidence: float
    decision: str
    evidence: List[str]


@dataclass
class SupervisionReport:
    """Report from Expert supervision of Worker output"""
    worker_agent: str
    expert_agent: str
    original_hypothesis: Dict[str, Any]
    expert_feedback: str
    corrections_applied: List[str]
    final_score: float
    status: str  # "APPROVED", "REVISED", "REJECTED"


class HiveCouncil:
    """
    The Council of Experts - Orchestrates Worker-Expert agent pairs
    for supervised analysis of Muqattaat patterns.
    """

    def __init__(self, use_ollama: bool = False):
        """Initialize the Hive Council"""
        self.use_ollama = use_ollama and CREWAI_AVAILABLE
        self.math_auditor = get_math_auditor()
        self.db = NeonDB()
        self.meritocracy_db = get_meritocracy_db()
        self.thoughts_log: List[AgentThought] = []
        self.supervision_reports: List[SupervisionReport] = []
        self.shared_memory_path = Path("/workspaces/QL/data/processed/hive_memory.json")
        self.shared_memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_shared_memory()
        self._initialize_agent_registry()

        # Initialize CrewAI if available
        if self.use_ollama:
            self._init_crewai_hive()
        else:
            self._init_mathematical_hive()

    def _load_shared_memory(self):
        """Load persistent memory from shared storage"""
        if self.shared_memory_path.exists():
            with open(self.shared_memory_path, 'r') as f:
                self.shared_memory = json.load(f)
        else:
            self.shared_memory = {
                "verified_patterns": [],
                "known_errors": [],
                "style_guide": {},
                "optimization_tips": [],
                "broadcast_history": [],
                "pending_broadcasts": [],
                "broadcasts": []
            }

    def _initialize_agent_registry(self):
        """Register all council members in the meritocracy ledger"""
        agents = [
            (AgentRole.CRYPT_WORKER.value, "Cryptographic Engineer", 1000),
            (AgentRole.SENIOR_ARCHITECT.value, "Senior Architect & Reviewer", 1500),
            (AgentRole.LINGUISTIC_WORKER.value, "Linguistic Analyst", 1000),
            (AgentRole.PHILOLOGIST.value, "Philological Expert", 1200),
        ]
        
        for agent_id, role, initial_credits in agents:
            self.meritocracy_db.register_agent(agent_id, role, initial_credits)

    def _save_shared_memory(self):
        """Save persistent memory to shared storage"""
        with open(self.shared_memory_path, 'w') as f:
            json.dump(self.shared_memory, f, indent=2)

    # ----------- Broadcast Helpers ------------
    def broadcast_knowledge(self, content: str, msg_type: str = "Custom",
                            priority: str = "normal", sender: str = "system") -> Dict:
        """Push a knowledge broadcast into shared memory"""
        message = {
            "message_id": f"MSG_{datetime.now().timestamp()}",
            "type": msg_type,
            "priority": priority,
            "content": content,
            "sender": sender,
            "timestamp": datetime.now().isoformat(),
            "acknowledged_by": []
        }
        self.shared_memory.setdefault("broadcast_history", []).append(message)
        self.shared_memory.setdefault("pending_broadcasts", []).append(message)
        self._save_shared_memory()
        return message

    def acknowledge_broadcast(self, message_id: str, agent_id: str) -> bool:
        """Mark a broadcast as acknowledged by an agent"""
        pending = self.shared_memory.get("pending_broadcasts", [])
        for msg in pending:
            if msg.get("message_id") == message_id:
                if agent_id not in msg.get("acknowledged_by", []):
                    msg.setdefault("acknowledged_by", []).append(agent_id)
                # if all four core agents have acked, move to history
                if len(msg.get("acknowledged_by", [])) >= 4:
                    self.shared_memory.setdefault("broadcast_history", []).append(msg)
                    pending.remove(msg)
                self._save_shared_memory()
                return True
        return False

    def get_broadcast_history(self) -> List[Dict]:
        """Return broadcast history"""
        return self.shared_memory.get("broadcast_history", [])

    def get_pending_broadcasts(self) -> List[Dict]:
        """Return currently pending broadcasts"""
        return self.shared_memory.get("pending_broadcasts", [])

    def log_broadcast(self, message: Dict) -> None:
        """Internal helper to log a broadcast message"""
        self.shared_memory.setdefault("broadcasts", []).append(message)
        self._save_shared_memory()


    def _init_crewai_hive(self):
        """Initialize CrewAI-based expert hive with Ollama"""
        try:
            llm = ChatOllama(model="llama3.1", base_url="http://localhost:11434")

            # ALPHA SQUAD: Cryptographic Engineers
            self.crypt_worker = Agent(
                role=AgentRole.CRYPT_WORKER.value,
                goal="Write precise Python scripts for Abjad and Rasm analysis",
                backstory="High-speed developer specializing in Arabic string manipulation",
                llm=llm,
                verbose=True
            )

            self.senior_architect = Agent(
                role=AgentRole.SENIOR_ARCHITECT.value,
                goal="Ensure code is bug-free and mathematically sound",
                backstory="Veteran systems architect who has seen every runtime error",
                llm=llm,
                verbose=True,
                allow_delegation=True
            )

            # BETA SQUAD: Linguistic Sentinels
            self.linguistic_worker = Agent(
                role=AgentRole.LINGUISTIC_WORKER.value,
                goal="Analyze phonetic density and Tajweed-based frequency",
                backstory="Expert in Arabic NLP and classical morphological structures",
                llm=llm,
                verbose=True
            )

            self.philologist = Agent(
                role=AgentRole.PHILOLOGIST.value,
                goal="Ensure root-pattern consistency and classical Arabic integrity",
                backstory="Historical linguist with deep knowledge of root morphology",
                llm=llm,
                verbose=True,
                allow_delegation=True
            )

            self.crewai_initialized = True
        except Exception as e:
            print(f"⚠️  CrewAI initialization failed: {e} - falling back to mathematical hive")
            self.crewai_initialized = False
            self._init_mathematical_hive()

    def _init_mathematical_hive(self):
        """Initialize mathematical hive (no external dependencies)"""
        self.crewai_initialized = False
        self.math_auditor = get_math_auditor()

    def log_thought(self, agent_role: str, thought: str, confidence: float, 
                   decision: str, evidence: List[str]):
        """Log an agent's internal reasoning"""
        thought_record = AgentThought(
            agent_role=agent_role,
            timestamp=datetime.now().isoformat(),
            thought=thought,
            confidence=confidence,
            decision=decision,
            evidence=evidence
        )
        self.thoughts_log.append(thought_record)

    def supervise_hypothesis(self, hypothesis: Hypothesis, surah_num: int) -> SupervisionReport:
        """
        Expert supervision loop:
        1. Original hypothesis is reviewed
        2. Expert provides feedback
        3. Corrections are applied
        4. Final score is computed
        """
        
        # STEP 1: Worker proposes initial score
        worker_confidence = hypothesis.score
        
        # STEP 2: Expert audits with mathematical patterns
        math_boost = self._run_mathematical_audit(hypothesis, surah_num)
        
        # STEP 3: Correct based on patterns
        corrections = []
        final_score = hypothesis.score
        
        if self.math_auditor.pattern_41_verified(hypothesis):
            corrections.append("Pattern #41 (Modulo-19) VERIFIED - confidence boost applied")
            final_score = min(final_score + 0.25, 1.0)
        
        if self.math_auditor.pattern_35_entropy_low(hypothesis):
            corrections.append("Pattern #35 (Shannon Entropy) - Low entropy detected")
            final_score = min(final_score + 0.15, 1.0)
        
        # Check complexity (Occam's Razor)
        if hypothesis.transformation_steps > 8:
            corrections.append(f"⚠️  {hypothesis.transformation_steps} steps exceeds optimal (8)")
            final_score *= 0.5  # Penalty for excessive complexity
            status = "REVISED"
        else:
            status = "APPROVED"
        
        # Create supervision report
        report = SupervisionReport(
            worker_agent=AgentRole.CRYPT_WORKER.value,
            expert_agent=AgentRole.SENIOR_ARCHITECT.value,
            original_hypothesis=asdict(hypothesis),
            expert_feedback=f"Audit completed. Mathematical confidence: {math_boost:.2f}",
            corrections_applied=corrections,
            final_score=final_score,
            status=status
        )
        
        self.supervision_reports.append(report)
        
        # Log to database
        self._log_supervision_report(report)
        
        # Track meritocracy: award credits based on result
        self._award_supervision_credits(report)
        
        return report

    def _run_mathematical_audit(self, hypothesis: Hypothesis, surah_num: int) -> float:
        """Run mathematical audit patterns on hypothesis"""
        boost = 0.0
        
        # Pattern #41: Modulo-19 verification
        if self.math_auditor.pattern_41_verified(hypothesis):
            boost += 0.25
        
        # Pattern #35: Shannon Entropy
        entropy = self.math_auditor.calculate_entropy(hypothesis.goal_link)
        if entropy < 2.0:  # Low entropy = structured pattern
            boost += 0.15
        
        # Pattern #33: Golden Ratio alignment
        if self.math_auditor.check_golden_ratio(hypothesis.evidence_snippets):
            boost += 0.20
        
        # Pattern #12: Abjad numerology
        if self.math_auditor.check_abjad_significance(hypothesis.goal_link):
            boost += 0.15
        
        return boost

    def orchestrate_deep_scan(self, surah_num: int, muqattaat_sequence: str) -> Dict[str, Any]:
        """
        Orchestrate a deep scan of a Surah using the expert hive
        Returns coordinated analysis from all agents
        """
        
        results = {
            "surah_number": surah_num,
            "muqattaat_sequence": muqattaat_sequence,
            "scan_timestamp": datetime.now().isoformat(),
            "worker_proposals": [],
            "expert_approvals": [],
            "linguistic_analysis": {},
            "final_knowledge_graph_update": None
        }
        
        # ALPHA SQUAD: Cryptographic Analysis
        try:
            if self.crewai_initialized:
                # Use CrewAI if available
                crypt_task = Task(
                    description=f"Analyze Surah {surah_num} ({muqattaat_sequence}). "
                                f"Verify if letters follow Abjad numerological patterns.",
                    expected_output="Verified Python report with Abjad checksums"
                )
                crypt_crew = Crew(
                    agents=[self.crypt_worker, self.senior_architect],
                    tasks=[crypt_task],
                    process=Process.hierarchical,
                    verbose=True
                )
                crypt_result = crypt_crew.kickoff()
                results["worker_proposals"].append({
                    "squad": "Alpha (Cryptographic)",
                    "result": str(crypt_result)
                })
            else:
                # Use mathematical fallback
                results["worker_proposals"].append({
                    "squad": "Alpha (Mathematical)",
                    "modulo_19_check": self.math_auditor.check_modulo_19(muqattaat_sequence),
                    "abjad_sum": self.math_auditor.calculate_abjad_sum(muqattaat_sequence)
                })
        except Exception as e:
            results["worker_proposals"].append({
                "squad": "Alpha",
                "error": str(e)
            })
        
        # BETA SQUAD: Linguistic Analysis
        try:
            results["linguistic_analysis"] = {
                "phonetic_density": self._calculate_phonetic_density(muqattaat_sequence),
                "tajweed_parameters": self._extract_tajweed_rules(muqattaat_sequence),
                "root_patterns": self._identify_root_patterns(muqattaat_sequence)
            }
        except Exception as e:
            results["linguistic_analysis"]["error"] = str(e)
        
        return results

    def _calculate_phonetic_density(self, sequence: str) -> Dict[str, float]:
        """Calculate phonetic density metrics"""
        from collections import Counter
        
        if not sequence:
            return {}
        
        letter_counts = Counter(sequence)
        total = len(sequence)
        
        return {
            letter: count / total
            for letter, count in letter_counts.items()
        }

    def _extract_tajweed_rules(self, sequence: str) -> List[str]:
        """Extract Tajweed (Quranic recitation rules) from sequence"""
        # Simplified implementation - in production would use advanced NLP
        rules = []
        
        # Common Tajweed patterns
        if 'ن' in sequence:
            rules.append("Nun rules - check for Assimilation (إدغام)")
        if 'ل' in sequence:
            rules.append("Lam rules - solar letters context")
        if 'م' in sequence:
            rules.append("Meem rules - check for Nasal articulation")
        
        return rules

    def _identify_root_patterns(self, sequence: str) -> Dict[str, List[str]]:
        """Identify Arabic root-word patterns in the sequence"""
        # Simplified - maps to major root patterns
        return {
            "triliteral_roots": ["Pattern analysis for 3-letter roots"],
            "weak_roots": ["Detection of weak letters (و, ي, ء)"],
            "geminate_roots": ["Detection of doubled letters"]
        }

    def _log_supervision_report(self, report: SupervisionReport):
        """Log supervision report to database"""
        try:
            if self.db.is_connected:
                cur = self.db.conn.cursor()
                cur.execute("""
                    INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload)
                    VALUES (%s, %s, %s)
                """, (
                    f"SUPV_{datetime.now().timestamp()}",
                    f"Expert Supervision: {report.status}",
                    json.dumps({
                        "worker": report.worker_agent,
                        "expert": report.expert_agent,
                        "status": report.status,
                        "final_score": report.final_score,
                        "corrections": report.corrections_applied
                    })
                ))
                self.db.conn.commit()
                cur.close()
        except Exception as e:
            pass  # Graceful failure

    def _award_supervision_credits(self, report: SupervisionReport):
        """Award credits to agents based on supervision outcome"""
        # Worker gets base credits for task completion
        self.meritocracy_db.record_task_completion(
            agent_id=report.worker_agent,
            task_type="hypothesis_proposal",
            status="success" if report.status != "REJECTED" else "failure",
            confidence_score=report.final_score
        )
        
        # Expert gets credits for review (higher for APPROVED)
        expert_credits = 50 if report.status == "APPROVED" else 30
        reason = f"Expert supervision - {report.status}"
        self.meritocracy_db.award_credits(
            agent_id=report.expert_agent,
            amount=expert_credits,
            reason=reason
        )
        
        # Update accuracy scores based on final score
        accuracy = report.final_score
        self.meritocracy_db.update_accuracy_score(report.expert_agent, accuracy)

    def get_hive_status(self) -> Dict[str, Any]:
        """Get current status of the hive"""
        return {
            "crewai_enabled": self.crewai_initialized,
            "mathematical_audit_enabled": True,
            "total_thoughts_logged": len(self.thoughts_log),
            "total_supervisions": len(self.supervision_reports),
            "shared_memory_size": len(json.dumps(self.shared_memory)),
            "database_connected": self.db.is_connected,
            "meritocracy_enabled": True,
            "timestamp": datetime.now().isoformat()
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get agent leaderboard from meritocracy ledger"""
        return self.meritocracy_db.get_leaderboard(limit)
    
    def get_agent_of_the_day(self) -> Optional[Dict]:
        """Get today's Agent of the Day"""
        return self.meritocracy_db.get_today_agent_of_the_day()
    
    def calculate_agent_of_the_day(self) -> Optional[str]:
        """Calculate and record today's Agent of the Day"""
        return self.meritocracy_db.calculate_agent_of_the_day()
    
    def get_agent_metrics(self, agent_id: str) -> Optional[Dict]:
        """Get metrics for a specific agent"""
        return self.meritocracy_db.get_agent_metrics(agent_id)

    def save_hive_state(self):
        """Save hive state to persistent storage"""
        state = {
            "thoughts_log": [asdict(t) for t in self.thoughts_log[-100:]],  # Last 100
            "supervision_reports": [asdict(r) for r in self.supervision_reports[-50:]],
            "shared_memory": self.shared_memory,
            "hive_status": self.get_hive_status()
        }
        
        hive_state_path = Path("/workspaces/QL/data/processed/hive_state.json")
        hive_state_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(hive_state_path, 'w') as f:
            json.dump(state, f, indent=2)


# Singleton instance
_hive_instance = None

def get_hive_council() -> HiveCouncil:
    """Get or create the Hive Council singleton"""
    global _hive_instance
    if _hive_instance is None:
        _hive_instance = HiveCouncil(use_ollama=False)  # Mathematical by default
    return _hive_instance
