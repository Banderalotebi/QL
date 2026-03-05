"""
src/data/muqattaat.py
─────────────────────
Canonical registry of the Muqattaat (الحروف المقطعة — Disjointed/Isolated Letters).

These 29 letter-sequences opening specific Surahs are the PRIMARY RESEARCH TARGET
of the entire system. Every agent's output is ultimately evaluated against
how much it illuminates the meaning of these sequences.

Sources: Classical tafsir + modern Quranic studies consensus on which Surahs
contain Muqattaat and what the letter sequences are.
"""

from __future__ import annotations
from dataclasses import dataclass

# ── Muqattaat Entry ───────────────────────────────────────────────────────────

@dataclass
class MuqattaatEntry:
    surah_number: int
    surah_name: str
    arabic_sequence: str           # Original Arabic isolated letters
    transliteration: str          # Standard Latin transliteration
    letter_names: list[str]       # Individual letter names (e.g. ["Alif", "Lam", "Mim"])
    abjad_values: list[int]       # Numerical value of each letter name
    unique_letters: list[str]     # De-duplicated letter set
    combination_length: int       # Number of letters in sequence
    group_id: str                 # Shared combination ID (e.g. "ALM" for Alif-Lam-Mim)


# ── The 29 Surahs with Muqattaat ──────────────────────────────────────────────
# Format: surah_num, name, arabic, translit, letter_names, abjad_values

MUQATTAAT_REGISTRY: list[MuqattaatEntry] = [
    MuqattaatEntry(2,  "Al-Baqarah",    "الم",    "ALM",   ["Alif","Lam","Mim"],    [1,30,40],  ["Alif","Lam","Mim"],  3, "ALM"),
    MuqattaatEntry(3,  "Ali-Imran",     "الم",    "ALM",   ["Alif","Lam","Mim"],    [1,30,40],  ["Alif","Lam","Mim"],  3, "ALM"),
    MuqattaatEntry(7,  "Al-Araf",       "المص",   "ALMS",  ["Alif","Lam","Mim","Sad"], [1,30,40,90], ["Alif","Lam","Mim","Sad"], 4, "ALMS"),
    MuqattaatEntry(10, "Yunus",         "الر",    "ALR",   ["Alif","Lam","Ra"],     [1,30,200], ["Alif","Lam","Ra"],   3, "ALR"),
    MuqattaatEntry(11, "Hud",           "الر",    "ALR",   ["Alif","Lam","Ra"],     [1,30,200], ["Alif","Lam","Ra"],   3, "ALR"),
    MuqattaatEntry(12, "Yusuf",         "الر",    "ALR",   ["Alif","Lam","Ra"],     [1,30,200], ["Alif","Lam","Ra"],   3, "ALR"),
    MuqattaatEntry(13, "Ar-Rad",        "المر",   "ALMR",  ["Alif","Lam","Mim","Ra"], [1,30,40,200], ["Alif","Lam","Mim","Ra"], 4, "ALMR"),
    MuqattaatEntry(14, "Ibrahim",       "الر",    "ALR",   ["Alif","Lam","Ra"],     [1,30,200], ["Alif","Lam","Ra"],   3, "ALR"),
    MuqattaatEntry(15, "Al-Hijr",       "الر",    "ALR",   ["Alif","Lam","Ra"],     [1,30,200], ["Alif","Lam","Ra"],   3, "ALR"),
    MuqattaatEntry(19, "Maryam",        "كهيعص",  "KHYAS", ["Kaf","Ha","Ya","Ain","Sad"], [20,5,10,70,90], ["Kaf","Ha","Ya","Ain","Sad"], 5, "KHYAS"),
    MuqattaatEntry(20, "Ta-Ha",         "طه",     "TH",    ["Ta","Ha"],             [9,5],      ["Ta","Ha"],           2, "TH"),
    MuqattaatEntry(26, "Ash-Shuara",    "طسم",    "TSM",   ["Ta","Sin","Mim"],      [9,60,40],  ["Ta","Sin","Mim"],    3, "TSM"),
    MuqattaatEntry(27, "An-Naml",       "طس",     "TS",    ["Ta","Sin"],            [9,60],     ["Ta","Sin"],          2, "TS"),
    MuqattaatEntry(28, "Al-Qasas",      "طسم",    "TSM",   ["Ta","Sin","Mim"],      [9,60,40],  ["Ta","Sin","Mim"],    3, "TSM"),
    MuqattaatEntry(29, "Al-Ankabut",    "الم",    "ALM",   ["Alif","Lam","Mim"],    [1,30,40],  ["Alif","Lam","Mim"],  3, "ALM"),
    MuqattaatEntry(30, "Ar-Rum",        "الم",    "ALM",   ["Alif","Lam","Mim"],    [1,30,40],  ["Alif","Lam","Mim"],  3, "ALM"),
    MuqattaatEntry(31, "Luqman",        "الم",    "ALM",   ["Alif","Lam","Mim"],    [1,30,40],  ["Alif","Lam","Mim"],  3, "ALM"),
    MuqattaatEntry(32, "As-Sajdah",     "الم",    "ALM",   ["Alif","Lam","Mim"],    [1,30,40],  ["Alif","Lam","Mim"],  3, "ALM"),
    MuqattaatEntry(36, "Ya-Sin",        "يس",     "YS",    ["Ya","Sin"],            [10,60],    ["Ya","Sin"],          2, "YS"),
    MuqattaatEntry(38, "Sad",           "ص",      "S",     ["Sad"],                 [90],       ["Sad"],               1, "S"),
    MuqattaatEntry(40, "Ghafir",        "حم",     "HM",    ["Ha","Mim"],            [8,40],     ["Ha","Mim"],          2, "HM"),
    MuqattaatEntry(41, "Fussilat",      "حم",     "HM",    ["Ha","Mim"],            [8,40],     ["Ha","Mim"],          2, "HM"),
    MuqattaatEntry(42, "Ash-Shura",     "حمعسق",  "HMASQ", ["Ha","Mim","Ain","Sin","Qaf"], [8,40,70,60,100], ["Ha","Mim","Ain","Sin","Qaf"], 5, "HMASQ"),
    MuqattaatEntry(43, "Az-Zukhruf",    "حم",     "HM",    ["Ha","Mim"],            [8,40],     ["Ha","Mim"],          2, "HM"),
    MuqattaatEntry(44, "Ad-Dukhan",     "حم",     "HM",    ["Ha","Mim"],            [8,40],     ["Ha","Mim"],          2, "HM"),
    MuqattaatEntry(45, "Al-Jathiyah",   "حم",     "HM",    ["Ha","Mim"],            [8,40],     ["Ha","Mim"],          2, "HM"),
    MuqattaatEntry(46, "Al-Ahqaf",      "حم",     "HM",    ["Ha","Mim"],            [8,40],     ["Ha","Mim"],          2, "HM"),
    MuqattaatEntry(50, "Qaf",           "ق",      "Q",     ["Qaf"],                 [100],      ["Qaf"],               1, "Q"),
    MuqattaatEntry(68, "Al-Qalam",      "ن",      "N",     ["Nun"],                 [50],       ["Nun"],               1, "N"),
]

# ── Helper lookups ─────────────────────────────────────────────────────────────

MUQATTAAT_SURAHS: set[int] = {e.surah_number for e in MUQATTAAT_REGISTRY}

BY_SURAH: dict[int, MuqattaatEntry] = {e.surah_number: e for e in MUQATTAAT_REGISTRY}

BY_GROUP: dict[str, list[MuqattaatEntry]] = {}
for _entry in MUQATTAAT_REGISTRY:
    BY_GROUP.setdefault(_entry.group_id, []).append(_entry)

# All 14 unique letters used across all Muqattaat
UNIQUE_LETTERS: set[str] = {
    letter
    for entry in MUQATTAAT_REGISTRY
    for letter in entry.unique_letters
}


def get_entry(surah_number: int) -> MuqattaatEntry | None:
    return BY_SURAH.get(surah_number)


def get_group(group_id: str) -> list[MuqattaatEntry]:
    return BY_GROUP.get(group_id, [])


def summary_stats() -> dict:
    """Quick statistical overview used by scouts."""
    return {
        "total_muqattaat_surahs": len(MUQATTAAT_SURAHS),
        "unique_letter_count": len(UNIQUE_LETTERS),
        "unique_combinations": len(BY_GROUP),
        "letters_used": sorted(UNIQUE_LETTERS),
        "group_frequencies": {
            gid: len(entries) for gid, entries in BY_GROUP.items()
        },
    }
