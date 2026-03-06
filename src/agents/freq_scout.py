import numpy as np
from scipy import stats
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis

class FreqScout(BaseScout):
    """
    The Statistical Dominator for Muqattaat frequency analysis.
    Performs Chi-Squared tests on letter frequencies.
    """

    name = "FreqScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def __init__(self):
        # Abjad values for reference (though not used in frequency analysis)
        self.abjad_values = {
            'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6,
            'ز': 7, 'ح': 8, 'ط': 9, 'ي': 10, 'ك': 20, 'ل': 30,
            'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
            'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500,
            'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000
        }

    def calculate_z_score(self, observed_freq, expected_freq, total_letters):
        """
        Calculate Z-score for frequency anomaly.
        Z = (observed - expected) / sqrt(expected * (1 - expected/total))
        """
        if expected_freq == 0:
            return 0

        variance = expected_freq * (1 - expected_freq / total_letters)
        if variance <= 0:
            return 0

        std_dev = np.sqrt(variance)
        z_score = (observed_freq - expected_freq) / std_dev
        return z_score

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze frequency patterns in Muqattaat letters.
        """
        hypotheses = []

        rasm_matrices = state.get("rasm_matrices", {})
        muqattaat_map = state.get("muqattaat_map", {})

        # Calculate global averages across all Surahs
        global_letter_counts = {}
        total_global_letters = 0

        for surah_num, letters in rasm_matrices.items():
            for letter in letters:
                global_letter_counts[letter] = global_letter_counts.get(letter, 0) + 1
                total_global_letters += 1

        # Global averages
        global_averages = {}
        for letter, count in global_letter_counts.items():
            global_averages[letter] = count / total_global_letters

        for surah_num in rasm_matrices:
            if surah_num not in muqattaat_map:
                continue

            muqattaat = muqattaat_map[surah_num]
            surah_letters = rasm_matrices[surah_num]
            surah_length = len(surah_letters)

            if surah_length == 0:
                continue

            # Count frequencies in this Surah
            surah_counts = {}
            for letter in surah_letters:
                surah_counts[letter] = surah_counts.get(letter, 0) + 1

            # Analyze each Muqattaat letter
            anomalous_letters = []
            for letter in set(muqattaat):
                observed_count = surah_counts.get(letter, 0)
                expected_count = global_averages.get(letter, 0) * surah_length

                z_score = self.calculate_z_score(observed_count, expected_count, surah_length)

                # Check if significantly anomalous (Z > 2 or Z < -2)
                if abs(z_score) > 2:
                    anomalous_letters.append((letter, observed_count, expected_count, z_score))

            if anomalous_letters:
                # Sort by absolute Z-score
                anomalous_letters.sort(key=lambda x: abs(x[3]), reverse=True)

                evidence = []
                for letter, obs, exp, z in anomalous_letters[:3]:  # Top 3
                    direction = "higher" if z > 0 else "lower"
                    evidence.append(f"{letter}: {obs} observed vs {exp:.1f} expected (Z={z:.2f}, {direction} frequency)")

                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link="Meaning = A 'Checksum' or 'Phonetic Index' ensuring the lexical integrity of the Surah.",
                    description=f"Frequency analysis found {len(anomalous_letters)} anomalous Muqattaat letters in Surah {surah_num}",
                    transformation_steps=2,  # Frequency counting + Z-score normalization
                    evidence_snippets=evidence,
                    surah_refs=[surah_num]
                )
                hypotheses.append(hypothesis)

        return hypotheses
