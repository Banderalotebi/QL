# src/data/muqattaat.py

# 1. The Numerical Distribution & Categorized Lists
SET_A_LETTERED_SURAHS = [
    2, 3, 7, 10, 11, 12, 13, 14, 15, 19, 20, 26, 27, 28, 
    29, 30, 31, 32, 36, 38, 40, 41, 42, 43, 44, 45, 46, 50, 68
]

# Compatibility Alias for main.py
MUQATTAAT_SURAHS = SET_A_LETTERED_SURAHS

# Set B is every other Surah (85 total)
SET_B_NON_LETTERED_SURAHS = [s for s in range(1, 115) if s not in SET_A_LETTERED_SURAHS]

# 2. The Positional Architecture
MUQATTAAT_ZONE = (2, 68)  
LITERAL_ZONE = (69, 114)  

# 3. Length and Structure (Meccan vs. Medinan Filter)
MEDINAN_MUQATTAAT = [2, 3] 
MECCAN_MUQATTAAT = [s for s in SET_A_LETTERED_SURAHS if s not in MEDINAN_MUQATTAAT]

# Mapping
MUQATTAAT_MAPPING = {
    2: "الم", 3: "الم", 7: "المص", 10: "الر", 11: "الر", 12: "الر", 
    13: "المر", 14: "الر", 15: "الر", 19: "كهيعص", 20: "طه", 
    26: "طسم", 27: "طس", 28: "طسم", 29: "الم", 30: "الم", 
    31: "الم", 32: "الم", 36: "يس", 38: "ص", 40: "حم", 
    41: "حم", 42: "حم عسق", 43: "حم", 44: "حم", 45: "حم", 
    46: "حم", 50: "ق", 68: "ن"
}

UNIQUE_COMBINATIONS = list(set(MUQATTAAT_MAPPING.values()))
LETTERS_USED = ["ا", "ل", "م", "ص", "ر", "ك", "ه", "ي", "ع", "ط", "س", "ح", "ق", "ن"]

# Restore this function for main.py UI
def summary_stats():
    return {
        "total_surahs": 114,
        "muqattaat_count": len(SET_A_LETTERED_SURAHS),
        "unique_letters": 13,
        "unique_combinations": 14,
        "letters": ["Ain", "Alif", "Ha", "Kaf", "Lam", "Mim", "Nun", "Qaf", "Ra", "Sad", "Sin", "Ta", "Ya"]
    }
