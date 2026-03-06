import math
import json
import datetime
from pathlib import Path

class HypothesisValidator:
    """
    Hypothesis Submission Validator for the Muqattaat Cryptanalytic Lab.
    Enforces Layer Purity and calculates the Occam Score in real-time.
    """

    def __init__(self, decay_constant=0.15):
        self.decay_constant = decay_constant
        self.knowledge_graph_path = Path("data/processed/knowledge_graph.json")

    def submit(self, scout_id, layer_target, goal_link, complexity_steps, evidence_weight, source_summary=""):
        """
        Submit a hypothesis for validation.

        Args:
            scout_id: Which agent generated this (e.g., "FreqScout")
            layer_target: "Rasm" or "Tashkeel"
            goal_link: How this explains the meaning
            complexity_steps: Number of logical leaps (1-8)
            evidence_weight: Statistical significance (0.0-1.0)
            source_summary: Brief description of the finding

        Returns:
            dict: Validation report with score and acceptance status
        """
        # Calculate Occam Score
        occam_score = evidence_weight * math.exp(-self.decay_constant * complexity_steps)

        # Determine acceptance based on score thresholds
        if complexity_steps <= 3:
            verdict = "Elite Tier" if occam_score >= 0.86 else "Strong Tier" if occam_score >= 0.63 else "Warning Tier"
            accepted = occam_score >= 0.47
        elif complexity_steps <= 6:
            verdict = "Strong Tier" if occam_score >= 0.63 else "Warning Tier"
            accepted = occam_score >= 0.47
        else:
            verdict = "Rejected"
            accepted = False

        # Create report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "scout_id": scout_id,
            "layer_target": layer_target,
            "goal_link": goal_link,
            "complexity_steps": complexity_steps,
            "evidence_weight": evidence_weight,
            "occam_score": round(occam_score, 3),
            "verdict": verdict,
            "accepted": accepted,
            "source_summary": source_summary
        }

        # If accepted, add to knowledge graph
        if accepted:
            self._add_to_knowledge_graph(report)

        return report

    def _add_to_knowledge_graph(self, report):
        """
        Add accepted hypothesis to the knowledge graph.
        """
        # Load existing graph
        if self.knowledge_graph_path.exists():
            with open(self.knowledge_graph_path, 'r', encoding='utf-8') as f:
                graph = json.load(f)
        else:
            graph = {"hypotheses": [], "relationships": []}

        # Add hypothesis
        graph["hypotheses"].append(report)

        # Save updated graph
        self.knowledge_graph_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.knowledge_graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    validator = HypothesisValidator()

    # A "LinguisticScout" entry that is too complex
    report = validator.submit(
        scout_id="LinguisticScout_01",
        layer_target="Tashkeel",
        goal_link="Phonetic patterns indicate melodic structure",
        complexity_steps=5,
        evidence_weight=0.75,
        source_summary="Phonetic analysis of surah verse endings"
    )

    print(json.dumps(report, indent=2))