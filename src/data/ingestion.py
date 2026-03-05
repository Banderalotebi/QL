# src/data/ingestion.py
# Ingestion module for the Muqattaat Cryptanalytic Lab

from __future__ import annotations

import requests

from src.core.state import ResearchState

# ── Constants ───────────────────────────────────────────────────────────────

CHAT_OLLAMA_API_URL = "https://api.chatollama.com/v1"

# ── Functions ───────────────────────────────────────────────────────────────

def run_ingestion(state: ResearchState) -> ResearchState:
    # Send request to ChatOllama API
    response = requests.post(
        CHAT_OLLAMA_API_URL,
        json={"prompt": state.prompt, "max_tokens": state.max_tokens}
    )

    # Parse response
    response_json = response.json()

    # Update state
    state.hypotheses = response_json["output"]

    return state
