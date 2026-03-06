from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class SymbolicScout(BaseScout):
    """
    The Geometric Archeologist for Muqattaat sequences.
    Analyzes physical strokes and geometric components.
    """

    name = "SymbolicScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def __init__(self):
        # Geometric categories based on 7th-century skeletal script
        self.geometric_weights = {
            'verticals': ['ا', 'ل', 'ط'],  # Alif, Lam, Ta - structural pillars
            'enclosures': ['م', 'ق', 'ه', 'ص'],  # Meem, Qaf, Ha, Sad - containers/foci
            'sweeps': ['ك', 'ي', 'ر']  # Kaaf, Ya, Ra - directional flow
        }

    def calculate_visual_weight(self, sequence):
        """
        Calculate the Visual Weight (VW) of a Muqattaat sequence.
        VW = (v * W_v) + (e * W_e) + (s * W_s)
        """
        v = sum(1 for letter in sequence if letter in self.geometric_weights['verticals'])
        e = sum(1 for letter in sequence if letter in self.geometric_weights['enclosures'])
        s = sum(1 for letter in sequence if letter in self.geometric_weights['sweeps'])

        # Weight constants based on early Hijazi/Kufic script density
        W_v, W_e, W_s = 1.0, 1.5, 0.8

        vw = (v * W_v) + (e * W_e) + (s * W_s)
        return vw, v, e, s

    def categorize_sequence(self, sequence):
        """
        Categorize a sequence as Vertical Dominant, Enclosure Dominant, or Sweep Dominant.
        """
        vw, v, e, s = self.calculate_visual_weight(sequence)

        if v > e and v > s:
            return "Vertical Dominant"
        elif e > v and e > s:
            return "Enclosure Dominant"
        elif s > v and s > e:
            return "Sweep Dominant"
        else:
            return "Balanced"

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze geometric patterns in Muqattaat sequences.
        """
        hypotheses = []

        muqattaat_map = state.get("muqattaat_map", {})

        for surah_num, sequence in muqattaat_map.items():
            vw, v, e, s = self.calculate_visual_weight(sequence)
            category = self.categorize_sequence(sequence)

            # Create hypothesis about geometric structure
            hypothesis = Hypothesis(
                source_scout=self.name,
                goal_link="Meaning = A visual 'Table of Contents' or a tally system used by early scribes to organize the codex.",
                description=f"Geometric analysis: {sequence} categorized as '{category}' with VW={vw:.1f} (V:{v}, E:{e}, S:{s})",
                transformation_steps=3,  # Decomposition + Weighting + Structural Correlation
                evidence_snippets=[
                    f"Sequence: {sequence}",
                    f"Category: {category}",
                    f"Visual Weight: {vw:.2f}",
                    f"Components: Verticals={v}, Enclosures={e}, Sweeps={s}"
                ],
                surah_refs=[surah_num]
            )
            hypotheses.append(hypothesis)

        return hypotheses
