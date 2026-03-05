# CONVENTIONS.md — Aider Architect Instructions
# Muqattaat Cryptanalytic Lab

> **Primary Mission**: Discover the meaning of the Disjointed Letters (الحروف المقطعة / Muqattaat) —
> the isolated letter-sequences that open 29 Surahs of the Quran. Every agent, every hypothesis,
> every scoring function must ultimately serve this one goal.

---

## Project Stack
- Python 3.11+
- LangGraph (multi-agent state graph)
- Neo4j / Memgraph (persistent knowledge graph)
- pandas, numpy, scipy (analysis)
- networkx (in-memory graph analysis)
- arabic-reshaper + python-bidi (Arabic text rendering)
- pyarabic (Rasm/Tashkeel splitting)
- rich (terminal UI)

## Architecture at a Glance

```
Raw Text Input (Uthmani Quran)
        │
        ▼
┌─────────────────────────────────┐
│   Ingestion Pipeline            │
│   Layer A: Rasm Matrix          │  ← skeletal letters only
│   Layer B: Tashkeel Matrix      │  ← diacritics overlay
│   Muqattaat Isolator            │  ← tags Isolated_Sequence nodes
└────────────┬────────────────────┘
             │  ResearchState dict (shared memory)
             ▼
┌────────────────────────────────────────────────────────┐
│                  Parallel Scout Array                  │
│  MicroScout │ StaticScout │ LinguisticScout            │
│  SymbolicScout │ MathScout │ FreqScout │ DeepScout     │
└────────────┬───────────────────────────────────────────┘
             │  raw_hypotheses[]
             ▼
┌─────────────────────────┐
│   The Fool (Auditor)    │  ← challenges every hypothesis
└────────────┬────────────┘
             │  survivor_hypotheses[]
             ▼
┌─────────────────────────┐
│   Synthesizer           │  ← merges cross-scout overlaps
└────────────┬────────────┘
             │  synthesized_theories[]
             ▼
┌─────────────────────────┐
│   Occam Scorer          │  ← score = f(evidence) * e^(-λ * steps)
└────────────┬────────────┘
             │  scored_theories[]
             ▼
┌─────────────────────────┐
│   Knowledge Graph Linker│  ← Neo4j: saves findings + dead-ends
└────────────┬────────────┘
             │
             ▼
         Lab Report (rich terminal / JSON)
```

---

## Core Invariants — Never Break These

1. **Goal Lock**: Every hypothesis object MUST include `hypothesis.goal_link` — a plain-English
   sentence explaining how this finding contributes to discovering the meaning of the Muqattaat.
   The Fool MUST reject any hypothesis where `goal_link` is empty or generic.

2. **Dual-Matrix Purity**: Rasm scouts NEVER receive Tashkeel data. Tashkeel scouts NEVER receive
   Rasm data. Mixing layers corrupts the baseline.

3. **Occam Penalty**: Score formula is non-negotiable:
   ```
   score = evidence_weight * exp(-lambda * transformation_steps)
   ```
   Default λ = 0.15. A theory needing >5 transformations starts below 0.47 regardless of evidence.

4. **Negative Nodes**: Dead-end paths are saved, not discarded. Tag them `type: DEAD_END` in the
   knowledge graph. The system must check the graph before re-attempting a known dead path.

5. **Isolated Sequence Priority**: Any text block tagged `Isolated_Sequence: True` receives
   priority routing to MathScout + SymbolicScout first. These are the Muqattaat — the primary targets.

---

## File Layout

```
muqattaat_lab/
├── CONVENTIONS.md           ← THIS FILE (aider reads first)
├── .aider.conf.yml          ← aider config
├── main.py                  ← lab entrypoint
├── src/
│   ├── core/
│   │   ├── state.py         ← ResearchState TypedDict
│   │   ├── graph.py         ← LangGraph state machine definition
│   │   └── scorer.py        ← Occam Razor scoring
│   ├── agents/
│   │   ├── base_agent.py    ← Abstract base: all scouts inherit this
│   │   ├── micro_scout.py
│   │   ├── static_scout.py
│   │   ├── linguistic_scout.py
│   │   ├── symbolic_scout.py
│   │   ├── math_scout.py
│   │   ├── freq_scout.py
│   │   ├── deep_scout.py
│   │   ├── the_fool.py      ← Auditor agent
│   │   └── synthesizer.py
│   ├── data/
│   │   ├── ingestion.py     ← Rasm/Tashkeel splitter + Muqattaat tagger
│   │   ├── muqattaat.py     ← Canonical Muqattaat registry
│   │   └── knowledge_graph.py ← Neo4j interface
│   └── utils/
│       ├── arabic.py        ← Arabic text helpers
│       ├── abjad.py         ← Abjad numerical system
│       └── display.py       ← Rich terminal output
├── data/
│   ├── raw/                 ← Quran text files go here
│   └── processed/           ← Cache of Rasm/Tashkeel matrices
└── tests/
    ├── test_ingestion.py
    ├── test_scouts.py
    └── test_scorer.py
```

---

## Coding Rules

- All functions have type annotations.
- All agents implement `run(state: ResearchState) -> ResearchState`.
- Hypotheses are always `Hypothesis` dataclass instances (defined in `state.py`).
- Every Hypothesis must set: `source_scout`, `goal_link`, `transformation_steps`, `evidence_snippets[]`.
- The Fool's rejection log is written to `state["rejected_hypotheses"]` with reason.
- No agent modifies another agent's output key. Scouts write to `state["raw_hypotheses"]` only.
- Use `rich.console` for all terminal output, never bare `print()`.
