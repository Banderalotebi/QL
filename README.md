# Muqattaat Cryptanalytic Lab
### الحروف المقطعة — The Disjointed Letters

> **Primary Goal**: Discover the meaning of the Muqattaat — the isolated letter-sequences
> (ن ق ص حم كهيعص ALM etc.) that open 29 Surahs of the Quran.
> Every agent in this system exists to serve this one mission.

---

## Quick Start with Aider

```bash
# Clone / enter the project
cd muqattaat_lab

# Install dependencies
pip install -r requirements.txt

# Launch aider in architect mode (as intended)
aider --architect \
      --model anthropic/claude-opus-4-6 \
      --editor-model anthropic/claude-sonnet-4-6 \
      AIDER_PROMPT.md

# Or start aider interactively with the conventions preloaded
aider --architect \
      --model anthropic/claude-opus-4-6 \
      --editor-model anthropic/claude-sonnet-4-6 \
      --read CONVENTIONS.md
```

## Run the Lab

```bash
# Analyze a subset of Muqattaat Surahs
python main.py --surahs 2 3 7 19 20 --focus muqattaat

# Analyze ALL 29 Muqattaat-bearing Surahs
python main.py --all-muqattaat

# Show top 20 theories
python main.py --all-muqattaat --top 20
```

---

## Architecture

```
Raw Quran Text
      │
      ▼
┌─────────────────────────────────────────────┐
│  Ingestion Pipeline                          │
│  Layer A: Rasm Matrix  (skeletal letters)    │
│  Layer B: Tashkeel Matrix (diacritics)       │
│  Muqattaat Isolator  → tags Isolated_Seq     │
└────────────────┬────────────────────────────┘
                 │ ResearchState (shared memory)
                 ▼
┌────────────────────────────────────────────────────────┐
│               Parallel Scout Array (7 agents)          │
│  MicroScout  │ StaticScout  │ LinguisticScout           │
│  SymbolicScout │ MathScout  │ FreqScout │ DeepScout     │
└────────────────┬───────────────────────────────────────┘
                 │ raw_hypotheses[]
                 ▼
         ┌───────────────┐
         │   The Fool    │  ← challenges every hypothesis
         │  (Auditor)    │    rejects weak/ungrounded ones
         └───────┬───────┘
                 │ survivor_hypotheses[]
                 ▼
         ┌───────────────┐
         │  Synthesizer  │  ← merges cross-scout overlaps
         └───────┬───────┘
                 │ synthesized_theories[]
                 ▼
         ┌───────────────┐
         │ Occam Scorer  │  score = ew * e^(-λ·steps) + goal_bonus
         └───────┬───────┘
                 │ scored_theories[]
                 ▼
         ┌───────────────┐
         │ Graph Linker  │  ← Neo4j: saves findings + dead-ends
         └───────┬───────┘
                 ▼
            Lab Report
```

## The 7 Scouts

| Scout | Layer | Primary Question |
|-------|-------|-----------------|
| **MicroScout** | Rasm | Do Muqattaat letters act as literal abbreviations for the words that follow? |
| **StaticScout** | Rasm | Do Muqattaat Surahs have a statistically distinct entropy fingerprint? |
| **LinguisticScout** | Tashkeel | Are the Muqattaat the consonantal skeleton of the Surah's phonetic identity? |
| **SymbolicScout** | Rasm | Does the geometric isolation of these letters carry symbolic meaning? |
| **MathScout** | Rasm | Do Abjad values of Muqattaat encode numerical metadata about their Surah? |
| **FreqScout** | Rasm | Do Muqattaat letters artificially dominate their Surah's letter frequency? |
| **DeepScout** | Tashkeel | Is there a strict transition grammar governing which letters can follow which? |

## Core Invariants

1. **Goal Lock** — Every Hypothesis must have a `goal_link` explaining its connection to Muqattaat meaning
2. **Layer Purity** — Rasm scouts never see Tashkeel data; Tashkeel scouts never see Rasm data
3. **Occam Penalty** — `score = evidence_weight × e^(-0.15 × steps)` — complexity is punished
4. **Negative Nodes** — Dead-ends are saved to the knowledge graph, never deleted
5. **The Fool is sovereign** — No hypothesis bypasses the auditor

## Dataset

- `data/raw/quran-uthmani-min/` — Uthmani script Quran (per-Surah files)
- `data/raw/surah_mathematical_patterns.csv` — Pre-computed nearest-neighbor patterns
- `data/processed/knowledge_graph.json` — Persistent findings + dead-ends (auto-generated)
