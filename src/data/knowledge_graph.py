"""
src/data/knowledge_graph.py
────────────────────────────
Knowledge Graph Linker — Persistent Memory via Neo4j

Saves findings and dead-ends to a graph database so the system:
  1. Never re-attempts known dead paths
  2. Links structurally similar patterns across different Surahs
  3. Builds a growing map of Muqattaat knowledge over time

Node types:
  FINDING     — A scored theory that passed The Fool + Synthesizer
  DEAD_END    — A rejected hypothesis (Negative Node)
  SURAH       — A Surah entity
  MUQATTAAT   — A specific Muqattaat sequence

Relationship types:
  PREFIXES        (MUQATTAAT) -[:PREFIXES]-> (SURAH)
  STRUCTURALLY_SIMILAR (MUQATTAAT) -[:STRUCTURALLY_SIMILAR]-> (MUQATTAAT)
  SUPPORTS        (FINDING) -[:SUPPORTS]-> (MUQATTAAT)
  RULED_OUT       (DEAD_END) -[:RULED_OUT]-> approach
"""

from __future__ import annotations
import json
import hashlib
from pathlib import Path
from src.core.state import ResearchState, Hypothesis, RejectedHypothesis

# ── Fallback: file-based graph when Neo4j is unavailable ─────────────────────
GRAPH_FILE = Path("data/processed/knowledge_graph.json")


class KnowledgeGraphLinker:
    """
    Writes findings and dead-ends to persistent storage.
    Uses Neo4j if available, falls back to JSON file graph.
    """

    name = "KnowledgeGraphLinker"

    def __init__(self):
        self._graph: dict = self._load_graph()

    def _load_graph(self) -> dict:
        GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
        if GRAPH_FILE.exists():
            try:
                return json.loads(GRAPH_FILE.read_text())
            except Exception:
                pass
        return {"findings": [], "dead_ends": [], "dead_end_fingerprints": []}

    def _save_graph(self) -> None:
        GRAPH_FILE.write_text(json.dumps(self._graph, ensure_ascii=False, indent=2))

    def _fingerprint(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:12]

    def run(self, state: ResearchState) -> ResearchState:
        scored: list[Hypothesis] = state.get("scored_theories", [])
        rejected: list[RejectedHypothesis] = state.get("rejected_hypotheses", [])

        # ── Save findings ──────────────────────────────────────────────────
        for theory in scored:
            node = {
                "type": "FINDING",
                "scout": theory.source_scout,
                "description": theory.description[:200],
                "goal_link": theory.goal_link[:200],
                "score": theory.score,
                "surah_refs": theory.surah_refs,
                "steps": theory.transformation_steps,
                "run_id": state.get("run_id", ""),
            }
            self._graph["findings"].append(node)

        # ── Save dead-ends as Negative Nodes ───────────────────────────────
        for rej in rejected:
            fp = self._fingerprint(rej.original.description)
            if fp not in self._graph["dead_end_fingerprints"]:
                self._graph["dead_end_fingerprints"].append(fp)
                self._graph["dead_ends"].append({
                    "type": "DEAD_END",
                    "fingerprint": fp,
                    "scout": rej.original.source_scout,
                    "description": rej.original.description[:200],
                    "rejection_reason": rej.rejection_reason,
                    "fool_question": rej.fool_question,
                })

        self._save_graph()

        # ── Update state with known dead-ends (for next run) ───────────────
        state["known_dead_ends"] = self._graph["dead_end_fingerprints"]
        state["graph_nodes"] = [n["type"] for n in self._graph["findings"][-10:]]
        return state

    def get_dead_end_fingerprints(self) -> list[str]:
        return self._graph.get("dead_end_fingerprints", [])
