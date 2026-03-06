import numpy as np
import pandas as pd
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class DeepScout(BaseScout):
    """
    The Transition Grammar Agent for Muqattaat sequences.
    Analyzes the probability of letter transitions in Muqattaat.
    """

    name = "DeepScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def __init__(self):
        self.muqattaat_sequences = list(KNOWN_MUQATTAAT.values())

    def generate_transition_matrix(self):
        """
        Generate a Markov transition matrix for Muqattaat letter sequences.
        """
        # Get all unique letters from Muqattaat
        all_letters = set()
        for seq in self.muqattaat_sequences:
            all_letters.update(seq)

        letters = sorted(list(all_letters))
        n = len(letters)
        transition_matrix = np.zeros((n, n))

        # Count transitions
        for seq in self.muqattaat_sequences:
            for i in range(len(seq) - 1):
                current = letters.index(seq[i])
                next_letter = letters.index(seq[i + 1])
                transition_matrix[current][next_letter] += 1

        # Normalize to probabilities
        row_sums = transition_matrix.sum(axis=1)
        # Avoid division by zero
        row_sums[row_sums == 0] = 1
        transition_matrix = transition_matrix / row_sums[:, np.newaxis]

        return pd.DataFrame(transition_matrix, index=letters, columns=letters)

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze transition patterns in Muqattaat sequences.
        """
        hypotheses = []

        # Generate transition matrix
        transition_df = self.generate_transition_matrix()

        # Find highly likely transitions
        likely_transitions = []
        forbidden_transitions = []

        for i, letter in enumerate(transition_df.index):
            for j, next_letter in enumerate(transition_df.columns):
                prob = transition_df.iloc[i, j]
                if prob > 0.5:  # High probability
                    likely_transitions.append((letter, next_letter, prob))
                elif prob == 0 and i != j:  # Forbidden transition (not self-loop)
                    forbidden_transitions.append((letter, next_letter))

        # Create hypothesis about transition grammar
        if likely_transitions or forbidden_transitions:
            evidence = []
            if likely_transitions:
                top_transitions = sorted(likely_transitions, key=lambda x: x[2], reverse=True)[:3]
                evidence.extend([f"High prob transition: {t[0]} → {t[1]} ({t[2]:.2f})" for t in top_transitions])

            if forbidden_transitions:
                evidence.extend([f"Forbidden: {t[0]} → {t[1]}" for t in forbidden_transitions[:3]])

            hypothesis = Hypothesis(
                source_scout=self.name,
                goal_link="Meaning is found in the directional flow—the letters act as a 'Pointer' to specific linguistic structures.",
                description=f"Transition analysis found {len(likely_transitions)} likely and {len(forbidden_transitions)} forbidden transitions",
                transformation_steps=2,  # Mapping transitions + Probability normalization
                evidence_snippets=evidence,
                surah_refs=list(state.get("surah_numbers", []))
            )
            hypotheses.append(hypothesis)

        return hypotheses
