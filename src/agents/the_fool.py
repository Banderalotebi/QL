# src/agents/the_fool.py
from src.core.state import ResearchState, Hypothesis, RejectedHypothesis
from langchain_ollama import ChatOllama
from src.data.muqattaat import MUQATTAAT_ZONE, LITERAL_ZONE, MECCAN_MUQATTAAT, MEDINAN_MUQATTAAT

class TheFool:
    """
    The Fool (Auditor)
    Upgraded to Phase 4: Socratic interrogator using Ollama to attack logic.
    Acts as a strict filter for the Structural Architecture of the Muqattaat.
    """
    def __init__(self):
        # Temperature is slightly higher (0.3) so The Fool can be creative in its logical attacks
        self.llm = ChatOllama(
            model="llama3:8b",
            temperature=0.3,
            num_predict=-1,
            num_ctx=8192
        )

    def run(self, state: ResearchState) -> dict:
        raw_hypotheses = state.get("raw_hypotheses", [])
        survivors = []
        rejected = []
        errors = []

        for hyp in raw_hypotheses:
            try:
                # Prompt the LLM to forcefully audit the hypothesis against the new hardcoded reality
                prompt = f"""
                You are 'The Fool', the strictest, most cynical cryptanalytic auditor in the Muqattaat Lab.
                Your job is to destroy weak hypotheses using aggressive Socratic interrogation.
                
                HYPOTHESIS SUBMITTED BY {hyp.source_scout}:
                Goal/Target: {hyp.goal_link}
                Description: {hyp.description}
                
                CRITICAL STRUCTURAL CONSTRAINTS OF THE DATASET:
                1. The Positional Architecture: The Muqatta'at Zone strictly ends at Surah 68. The "Literal Zone" (Surahs 69-114) completely abandons disjointed letters.
                2. The Revelation Filter: 27 of the 29 lettered Surahs are Meccan. Only 2 are Medinan.
                
                YOUR TASK:
                1. Does this hypothesis logically account for these constraints, or does it blindly ignore why the pattern abruptly halts at Surah 68?
                2. Is the hypothesis making a massive, unjustified leap in logic? (Apply Occam's Razor).
                
                Provide a short, brutal Socratic critique. 
                You MUST end your response with exactly "VERDICT: PASS" if the logic is sound and accounts for constraints, or "VERDICT: REJECT" if the logic is flawed.
                """
                
                response = self.llm.invoke(prompt)
                content = response.content.strip()
                
                if "VERDICT: PASS" in content.upper():
                    # The hypothesis survived the Socratic attack.
                    # We slightly boost its score for surviving.
                    hyp.score = min(1.0, hyp.score + 0.1)
                    survivors.append(hyp)
                else:
                    # The Fool successfully destroyed the hypothesis.
                    rej = RejectedHypothesis(
                        hypothesis=hyp,
                        reason=content
                    )
                    rejected.append(rej)
                    
            except Exception as e:
                errors.append(f"The Fool Error on hypothesis from {hyp.source_scout}: {str(e)}")

        return {
            "survivor_hypotheses": survivors, 
            "rejected_hypotheses": rejected, 
            "errors": errors
        }
