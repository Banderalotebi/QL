from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis

class MathScout(BaseScout):
    """
    The Metadata Auditor for Abjad numerical analysis.
    Converts letters to numbers and looks for checksums.
    """

    name = "MathScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def __init__(self):
        self.abjad_table = {
            'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6,
            'ز': 7, 'ح': 8, 'ط': 9, 'ي': 10, 'ك': 20, 'ل': 30,
            'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
            'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500,
            'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000
        }

    def calculate_abjad_sum(self, sequence):
        """
        Calculate the Abjad numerical sum of a letter sequence.
        """
        total = 0
        for letter in sequence:
            total += self.abjad_table.get(letter, 0)
        return total

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze Abjad values and look for metadata collisions.
        """
        hypotheses = []

        muqattaat_map = state.get("muqattaat_map", {})

        for surah_num, sequence in muqattaat_map.items():
            abjad_sum = self.calculate_abjad_sum(sequence)

            # Get Surah metadata (this would need to be provided in state)
            # For now, we'll create hypotheses based on the sum itself
            # In a full implementation, compare to verse counts, word counts, etc.

            hypothesis = Hypothesis(
                source_scout=self.name,
                goal_link="Meaning = A 'File Header' containing the checksum of the document's length and index.",
                description=f"Abjad analysis: {sequence} sums to {abjad_sum}",
                transformation_steps=1,  # Simple Summation
                evidence_snippets=[
                    f"Sequence: {sequence}",
                    f"Abjad Sum: {abjad_sum}",
                    f"Individual values: {[(letter, self.abjad_table.get(letter, 0)) for letter in sequence]}"
                ],
                surah_refs=[surah_num]
            )
            hypotheses.append(hypothesis)

        return hypotheses
