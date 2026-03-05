import os
from src.data.db import record_hypothesis
from src.utils.tools import Librarian

class MicroScout:
    def __init__(self):
        # Initializing Ollama 8B (Llama 3) with infinite predict & max context
        self.llm = ChatOllama(
            model="llama3:8b",
            temperature=0.1,
            num_predict=-1,
            num_ctx=8192
        )
        
        # Initialize Librarian
        self.librarian = Librarian()

    def run(self, state: ResearchState) -> dict:
        # Get previous research context for the current Surah
        context = self.librarian.get_context_for_surah(state.surah_id)
        
        # Generate new hypothesis using Ollama
        hypothesis = self.llm.generate_hypothesis(context)
        
        # Record hypothesis in Neon
        record_hypothesis(state.run_id, hypothesis)
        
        return hypothesis
