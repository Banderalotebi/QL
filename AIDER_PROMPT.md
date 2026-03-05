# MISSION: Transition to Ollama 8B & Implement Dual-Leadership Supervisor

## 1. INFRASTRUCTURE SHIFT (Ollama Integration)
- Replace all `litellm` and Anthropic API calls with `langchain-ollama`.
- Initialize `ChatOllama(model="llama3:8b", temperature=0.1)` as the primary engine in `src/core/graph.py`.
- Update `requirements.txt` to include `ollama` and `langchain-ollama`.

## 2. DATA PATH FIX (Phase 2 Correction)
- Update `src/data/ingestion.py` to correctly resolve the folder structure:
  - Base: `QL/data/Quran_Extracted_Texts/`
  - Subfolders: `quran-uthmani-min`, `quran-simple-clean`, `quran-simple-min`.
- Ensure `load_surah_text()` uses `os.path.join` to handle both local and containerized execution paths.

## 3. DUAL-LEADERSHIP IMPLEMENTATION (The Agent Factory)
- Create `src/core/leaders.py` with two primary classes:
  - **ExecutionerLeader (Results CEO)**: Monitors `scorer.py` metrics. If a Surah results in 0 hypotheses or low scores, it triggers a "Factory Spawn" to create a high-compute Specialist Agent.
  - **AlchemistLeader (Meaning CEO)**: Audits the `goal_link` of every hypothesis. It ensures findings connect to "Meaning Anchors" (e.g., Jeddah Latitude or Muqattaat DNA). It rewards meaningful patterns by pinning them to the Knowledge Graph.
- Update `src/core/graph.py` to add these as **Supervisor Nodes** that audit the state before final output.

## 4. AGENT COMPLETION (Phase 3)
- **MicroScout**: Implement the "First Letter" acronym test. Do Muqattaat letters match the start of words in the first 3 ayahs?
- **The Fool**: Upgrade with Socratic Dialogue logic. If the MathScout uses complex algebra, The Fool must add an interrogation note to the Research Record: "Why is this math necessary for this script? Is this a coincidence?"
- **Research Record**: Ensure all results are saved to a shared folder `/results/` in a Markdown table format showing: [Agent] [Action] [Why] [Pattern] [Result].

## 5. INCLUSIVE COLLABORATION
- Implement a "Human Hypothesis" watcher. The system must read `.md` files from `/human_hypotheses/` at the start of every run and inject them into the AlchemistLeader's "Reward List."