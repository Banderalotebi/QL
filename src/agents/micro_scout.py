# src/agents/micro_scout.py
from langchain_ollama import ChatOllama
from src.core.state import ResearchState, Hypothesis
from src.data.db import record_hypothesis, NeonLabAPI

class MicroScout:
    def __init__(self):
        self.llm = ChatOllama(
            model="ollama/llama3.1", # Changed from "llama3.1:8b" to "ollama/llama3.1"
            temperature=0.1,
            num_ctx=131072
        )
        self.api = NeonLabAPI()

    def run(self, state: ResearchState) -> dict:
        surahs = state.get("surah_numbers", [])
        run_id = state.get("run_id", "local_run")
        new_hypotheses = []

        for s_id in surahs:
            try:
                # 1. Start Event API Loop - Open Ticket
                try:
                    self.api.open_ticket(run_id, "MicroScout", f"Acronym Analysis Surah {s_id}")
                except Exception:
                    pass  # Graceful failure
                
                # 2. Get Data Free - Fetch from Neon
                try:
                    context = self.api.get_surah_context(s_id)
                except Exception:
                    context = None
                
                if not context: continue

                # 3. Process with Llama 3.1
                words = context['content'].split()[:30]
                prompt = f"Analyze the opening initials for acronym patterns in Surah {s_id}: {' '.join(words)}"
                response = self.llm.invoke(prompt)

                # 4. Log Discovery - Automatic recording to Neon
                hyp = Hypothesis(
                    source_scout="MicroScout",
                    goal_link=f"Acronym testing",
                    transformation_steps=1,
                    evidence_snippets=[" ".join(words[:5])],
                    description=response.content.strip(),
                    score=0.8,
                    surah_refs=[s_id]
                )
                
                try:
                    record_hypothesis(run_id, hyp)
                except Exception:
                    pass  # Graceful failure
                
                new_hypotheses.append(hyp)
            except Exception:
                continue

        return {"raw_hypotheses": new_hypotheses}
