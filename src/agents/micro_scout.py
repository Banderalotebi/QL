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
            # 1. Start Event API Loop - Open Ticket
            self.api.open_ticket(run_id, "MicroScout", f"Acronym Analysis Surah {s_id}")
            
            # 2. Get Data Free - Fetch from Neon
            context = self.api.get_surah_context(s_id)
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
            
            record_hypothesis(run_id, hyp)
            new_hypotheses.append(hyp)

        return {"raw_hypotheses": new_hypotheses}
