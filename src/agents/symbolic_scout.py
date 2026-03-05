"""
src/agents/symbolic_scout.py
─────────────────────────────
Symbolic Scout — Geometric & Connection Topology

Strictly visual/geometric analysis. Ignores phonetic meaning entirely.
Analyzes Arabic letter connection typologies:
  R  = Right-joining only (Alif, Dal, Dhal, Ra, Zay, Waw)
  D  = Dual-joining / medial
  I  = Isolated (does not connect left)

PRIMARY GOAL FOCUS:
  The Muqattaat letters are written as ISOLATED shapes — disconnected from
  each other and the following text. Is this geometric isolation itself
  meaningful? Do the connection patterns of the specific letters chosen
  encode a structural or spatial message about the Surah?
"""

from __future__ import annotations
from src.agents.base_agent import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.data.muqattaat import BY_SURAH, MUQATTAAT_SURAHS, UNIQUE_LETTERS


# ── Arabic letter connection typology ─────────────────────────────────────────
# R = right-joining only, D = dual-joining, I = isolated form

LETTER_CONNECTION_TYPE: dict[str, str] = {
    "Alif":  "R",   # ا
    "Ba":    "D",   # ب
    "Ta":    "D",   # ت
    "Tha":   "D",   # ث
    "Jim":   "D",   # ج
    "Ha":    "D",   # ح
    "Kha":   "D",   # خ
    "Dal":   "R",   # د
    "Dhal":  "R",   # ذ
    "Ra":    "R",   # ر
    "Zay":   "R",   # ز
    "Sin":   "D",   # س
    "Shin":  "D",   # ش
    "Sad":   "D",   # ص
    "Dad":   "D",   # ض
    "Ta2":   "D",   # ط
    "Dha":   "D",   # ظ
    "Ain":   "D",   # ع
    "Ghain": "D",   # غ
    "Fa":    "D",   # ف
    "Qaf":   "D",   # ق
    "Kaf":   "D",   # ك
    "Lam":   "D",   # ل
    "Mim":   "D",   # م
    "Nun":   "D",   # ن
    "Ha2":   "D",   # ه
    "Waw":   "R",   # و
    "Ya":    "D",   # ي
}


class SymbolicScout(BaseScout):
    name = "SymbolicScout"
    consumes_rasm = True
    consumes_tashkeel = False

    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []

        # ── Cross-Muqattaat connection topology analysis ───────────────────
        muq_connection_profiles: dict[str, dict[str, int]] = {}

        for snum in state.get("input_surah_numbers", []):
            if snum not in MUQATTAAT_SURAHS:
                continue

            entry = BY_SURAH[snum]
            letter_names = entry.letter_names
            conn_types = [LETTER_CONNECTION_TYPE.get(name, "D") for name in letter_names]
            profile_key = "".join(conn_types)
            muq_connection_profiles[entry.transliteration] = {
                "R": conn_types.count("R"),
                "D": conn_types.count("D"),
                "profile": profile_key,
                "surah": snum,
            }

        if muq_connection_profiles:
            # Find if all single-letter Muqattaat are R-type (right-joining)
            single_letter = {
                k: v for k, v in muq_connection_profiles.items()
                if len(k) == 1
            }

            # Check for geometric skew in the dataset
            all_r = sum(1 for v in muq_connection_profiles.values() if v["R"] > v["D"])
            all_d = sum(1 for v in muq_connection_profiles.values() if v["D"] > v["R"])

            hypotheses.append(self.make_hypothesis(
                description=(
                    f"Muqattaat connection topology: {all_d} sequences are Dual-joining dominant, "
                    f"{all_r} are Right-joining dominant. "
                    f"Profiles: {list(muq_connection_profiles.items())[:5]}"
                ),
                goal_link=(
                    "The Muqattaat letters are always written in their ISOLATED geometric form — "
                    "disconnected even when normally connecting letters are used. "
                    "The skew toward Dual-joining letters written in isolation suggests the geometric "
                    "disruption of their natural connection is itself the message: "
                    "they are meant to stand alone as symbols, not phonemes. "
                    "This supports the 'symbolic/iconic meaning' theory of the Muqattaat."
                ),
                transformation_steps=2,
                evidence_snippets=[
                    f"Total Muqattaat combinations analyzed: {len(muq_connection_profiles)}",
                    f"D-dominant: {all_d}",
                    f"R-dominant: {all_r}",
                    f"Sample profiles: {list(muq_connection_profiles.keys())[:5]}",
                ],
                surah_refs=[
                    v["surah"] for v in muq_connection_profiles.values()
                    if isinstance(v.get("surah"), int)
                ],
            ))

            # ── Dotted vs undotted letters in Muqattaat ───────────────────
            # Undotted (unpointed) letters form a strong statistical bias in Muqattaat
            # (from research doc: "overwhelmingly constructed using the undotted base architecture")
            UNDOTTED_LETTERS = {"Alif", "Lam", "Mim", "Ra", "Ha", "Sad", "Ta", "Kaf", "Qaf", "Nun"}
            DOTTED_LETTERS = {"Ba", "Ta", "Tha", "Jim", "Kha", "Dal", "Dhal", "Zay",
                              "Shin", "Dad", "Dha", "Ain", "Ghain", "Fa", "Ya"}

            total_muq_letters: list[str] = []
            for entry_snum in state.get("input_surah_numbers", []):
                if entry_snum in MUQATTAAT_SURAHS:
                    total_muq_letters.extend(BY_SURAH[entry_snum].letter_names)

            undotted_count = sum(1 for l in total_muq_letters if l in UNDOTTED_LETTERS)
            dotted_count = sum(1 for l in total_muq_letters if l in DOTTED_LETTERS)
            total = len(total_muq_letters)

            if total > 0:
                undotted_ratio = undotted_count / total
                hypotheses.append(self.make_hypothesis(
                    description=(
                        f"Of {total} Muqattaat letter instances analyzed: "
                        f"{undotted_count} undotted ({undotted_ratio:.1%}), "
                        f"{dotted_count} dotted ({1-undotted_ratio:.1%})."
                    ),
                    goal_link=(
                        "The Muqattaat are overwhelmingly built from undotted (unpointed) letters — "
                        "the most ancient, fundamental Arabic letterforms that predate diacritical marking. "
                        "This geometric skew suggests the Muqattaat operate at the level of RASM (skeleton) — "
                        "their meaning is encoded in the base geometric forms, not pronunciation. "
                        "They may represent the geometric/structural alphabet of the text itself."
                    ),
                    transformation_steps=2,
                    evidence_snippets=[
                        f"Undotted count: {undotted_count}",
                        f"Dotted count: {dotted_count}",
                        f"Undotted ratio: {undotted_ratio:.4f}",
                    ],
                    surah_refs=list({
                        snum for snum in state.get("input_surah_numbers", [])
                        if snum in MUQATTAAT_SURAHS
                    }),
                    metadata={"dual_layer_corroborated": False},
                ))

        return hypotheses
from src.agents.base_scout import BaseScout
from src.core.state import ResearchState, Hypothesis
from src.utils.arabic import KNOWN_MUQATTAAT

class SymbolicScout(BaseScout):
    """
    Symbolic and geometric pattern analysis of Muqattaat sequences.
    """
    
    name = "SymbolicScout"
    consumes_rasm = True
    consumes_tashkeel = False
    
    def analyze(self, state: ResearchState) -> list[Hypothesis]:
        """
        Analyze symbolic patterns and geometric relationships in Muqattaat.
        """
        hypotheses = []
        
        rasm_matrices = state.get("rasm_matrices", {})
        muqattaat_map = state.get("muqattaat_map", {})
        
        for surah_num in rasm_matrices:
            if surah_num not in muqattaat_map:
                continue
                
            muqattaat = muqattaat_map[surah_num]
            rasm_letters = rasm_matrices[surah_num]
            
            if not rasm_letters:
                continue
            
            # Analyze sequence length and letter uniqueness
            muqattaat_length = len(muqattaat)
            unique_letters = len(set(muqattaat))
            
            # Look for geometric patterns in letter positions
            muqattaat_letters = set(muqattaat)
            positions = []
            for i, letter in enumerate(rasm_letters[:1000]):  # Sample first 1000 letters
                if letter in muqattaat_letters:
                    positions.append(i)
            
            if len(positions) >= 3:
                # Calculate intervals between positions
                intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
                
                hypothesis = Hypothesis(
                    source_scout=self.name,
                    goal_link=f"Muqattaat {muqattaat} forms a {muqattaat_length}-letter symbolic sequence with {unique_letters} unique elements, creating geometric intervals averaging {avg_interval:.1f} positions in Surah {surah_num}, suggesting a spatial encoding of divine mathematical harmony.",
                    description=f"Symbolic analysis: {muqattaat_length} letters, {unique_letters} unique, avg interval {avg_interval:.1f}",
                    transformation_steps=3,
                    evidence_snippets=[
                        f"Sequence length: {muqattaat_length}",
                        f"Unique letters: {unique_letters}",
                        f"Position samples: {positions[:10]}",
                        f"Average interval: {avg_interval:.2f}",
                        f"Total positions found: {len(positions)}"
                    ],
                    surah_refs=[surah_num],
                    layer="rasm"
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
