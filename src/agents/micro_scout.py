# src/agents/micro_scout.py
from src.core.state import ResearchState, Hypothesis
from langchain_ollama import ChatOllama
from src.data.ingestion import load_surah_text

class MicroScout:
    def __init__(self):
        # Initializing Ollama 8B (Llama 3) with infinite predict & max context
        self.llm = ChatOllama(
            model="llama3:8b",
            temperature=0.1,
            num_predict=-1,
            num_ctx=8192
        )

    def run(self, state: ResearchState) -> dict:
        surahs = state.get("surah_numbers", state.get("input_surah_numbers", []))
        new_hypotheses = []
        errors = []

        for surah in surahs:
            try:
                # Load text and grab the first ~30 words (approx 3 ayahs)
                text = load_surah_text(surah, "quran-simple-clean")
                words = text.split()[:30]
                first_letters = [w[0] for w in words if w]
                
                # Socratic Acronym Prompt
                prompt = f"""
                You are the MicroScout cryptanalyst. 
                Your task is to test the 'Acronym Theory' for Surah {surah}.
                Do the isolated letters (Muqattaat) at the start of this Surah stand for the first letters of the subsequent words?
                
                First 30 words of Surah {surah}:
                {' '.join(words)}
                
                First letters of these words:
                {' '.join(first_letters)}
                
                Analyze if there is a deliberate acronym pattern. Give a concise summary of your finding.
                """
                
                response = self.llm.invoke(prompt)
                
                # Goal Lock: Every Hypothesis must have a meaning-oriented goal_link
                hypothesis = Hypothesis(
                    source_scout="MicroScout",
                    goal_link=f"Tests if Surah {surah}'s Muqattaat are literal acronyms of its opening ayahs.",
                    transformation_steps=1,
                    evidence_snippets=[" ".join(words[:10])],
                    description=response.content.strip(),
                    score=0.85, # Temporary base score before Occam's Razor
                    surah_refs=[surah]
                )
                new_hypotheses.append(hypothesis)
                
            except Exception as e:
                errors.append(f"MicroScout Error on Surah {surah}: {str(e)}")

        return {"raw_hypotheses": new_hypotheses, "errors": errors}
