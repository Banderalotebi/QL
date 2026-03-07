# Ollama 3.1 Integration Guide

## 🚀 Quick Start

The system has been updated to use **Ollama 3.1** as the LLM backend instead of CrewAI. This provides direct access to the Llama 3.1 model with lower dependencies and better performance.

### Prerequisites

1. **Install Ollama**: Download from [https://ollama.ai](https://ollama.ai)
2. **Pull Llama 3.1 model**: 
   ```bash
   ollama pull llama3.1
   ```
3. **Start Ollama server**:
   ```bash
   ollama serve
   ```
   By default, Ollama runs on `http://localhost:11434`

### Environment Variables

Configure Ollama connection via environment variables:

```bash
# Set custom Ollama base URL (default: http://localhost:11434)
export OLLAMA_BASE_URL="http://localhost:11434"

# Set Ollama model (default: llama3.1)
export OLLAMA_MODEL="llama3.1"
```

### Running the Dashboard

**With Ollama enabled:**
```bash
cd /workspaces/QL
streamlit run frontend/sovereign_dashboard.py
```

**With API backend:**
```bash
USE_API=true streamlit run frontend/sovereign_dashboard.py
```

The system will automatically detect if Ollama is available and gracefully fallback to mathematical orchestration if needed.

## 📊 System Architecture

### Agent Roles

The system maintains four expert agent roles that operate through Ollama:

- **Crypt-Worker**: Cryptographic analysis with Abjad numerology
- **Senior Architect**: Validation and bug-detection oversight
- **Linguistic-Worker**: Phonetic density and Tajweed analysis  
- **Philologist**: Root-pattern consistency verification

### Operational Modes

1. **Mathematical (Fallback)**: Pure pattern-matching without LLM
2. **Ollama 3.1 (LLM-Enhanced)**: Full multi-agent reasoning via Ollama
3. **Hybrid**: Combines Ollama analysis with mathematical verification

### API Integration Points

```python
from src.agents.hive_council import HiveCouncil

# Initialize with Ollama
hive = HiveCouncil(use_ollama=True)

# Run deep scan with agent coordination
results = hive.orchestrate_deep_scan(surah_num=19, muqattaat_sequence="كهيعص")

# Access hive status
status = hive.get_hive_status()
print(f"Ollama Enabled: {status['ollama_enabled']}")
print(f"Model: {status['ollama_model']}")
```

## 🔧 Key Changes from CrewAI

### Before (CrewAI)
- Dependency: `from crewai import Agent, Task, Crew, Process`
- Agent setup required complex configuration
- Multi-framework setup (CrewAI + LangChain Ollama)

### After (Direct Ollama)
- Direct HTTP API calls to Ollama
- Simpler initialization and control flow
- Single model dependency
- Graceful fallback to mathematical mode

### Method Replacements

| Old              | New                  |
|------------------|----------------------|
| `_init_crewai_hive()` | `_init_ollama_hive()` |
| `self.crewai_initialized` | `self.ollama_initialized` |
| CrewAI Crew.kickoff() | `self._call_ollama()` |
| `crewai_enabled` | `ollama_enabled` |

## 🛡️ Fallback Behavior

If Ollama is unavailable, the system automatically falls back to:

1. **Mathematical Auditing**: Pattern verification using algorithms
2. **Phonetic Analysis**: Built-in linguistic rules
3. **Meritocracy Tracking**: Credit system continues to function

No data loss occurs—the system degrades gracefully.

## 📈 Performance Considerations

- **cold start**: First Ollama query (~2-5s) loads model into VRAM
- **warm queries**: Subsequent requests (~0.5-1s) with `keep_alive` set to 5m
- **timeout**: Default 30s per query; adjust if needed
- **temperature**: Set to 0.7 for analysis (balance creativity/consistency)

## 🐛 Troubleshooting

### Ollama not connecting
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Model not found
```bash
ollama pull llama3.1
ollama list  # Verify installation
```

### Slow responses
- Reduce system load
- Check available VRAM: `nvidia-smi` or `system_profiler`
- Consider using a smaller model: `ollama pull mistral`

## 📝 Configuration Example

Create `.env` file for persistent settings:

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
USE_API=true
PYTHONPATH=/workspaces/QL:$PYTHONPATH
```

Then run:
```bash
source .env
streamlit run frontend/sovereign_dashboard.py
```

## 🔗 Related Files

- [hive_council.py](src/agents/hive_council.py) - Agent orchestration
- [sovereign_dashboard.py](frontend/sovereign_dashboard.py) - UI interface
- [hive_api.py](backend/hive_api.py) - API backend
- [requirements.txt](requirements.txt) - Dependencies (no CrewAI needed)
