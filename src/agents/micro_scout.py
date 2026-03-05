import os
from src.data.db import record_hypothesis
from src.utils.tools import Librarian
from src.core.state import ResearchState
from langchain.chat_models import ChatOllama

class MicroScout:
    def __init__(self):
        # Initializing Ollama 3.1 with infinite predict & max context
        self.llm = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
            num_predict=-1,
            num_ctx=8192
        )
        
        # Initialize Librarian
        self.librarian = Librarian()

    def run(self, state: ResearchState) -> dict:
        # 1. Get previous research context for the current Surah
        context = self.librarian.get_context_for_surah(state.surah_id)
        
        # 2. Construct the prompt (incorporating the state and librarian data)
        prompt = f"""
        Research Task: {state.query}
        Surah Context: {context}
        Additional Data: {state.current_findings}
        
        Analyze the above and provide a detailed report.
        """

        # 3. Invoke the LLM
        # Assuming you're using LangChain's ChatOllama based on the syntax
        response = self.llm.invoke(prompt)

        # 4. Update and return the state
        return {
            "research_notes": response.content,
            "status": "complete"
        }
