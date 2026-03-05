# src/data/muqattaat.py

# 1. The Numerical Distribution & Categorized Lists
SET_A_LETTERED_SURAHS = [
    2, 3, 7, 10, 11, 12, 13, 14, 15, 19, 20, 26, 27, 28, 
    29, 30, 31, 32, 36, 38, 40, 41, 42, 43, 44, 45, 46, 50, 68
]

# Set B is every other Surah (85 total)
SET_B_NON_LETTERED_SURAHS = [s for s in range(1, 115) if s not in SET_A_LETTERED_SURAHS]

# 2. The Positional Architecture
MUQATTAAT_ZONE = (2, 68)  # The block where all letters are concentrated
LITERAL_ZONE = (69, 114)  # The final block devoid of disjointed letters

# 3. Length and Structure (Meccan vs. Medinan Filter)
# Out of the 29 in Set A, only 2 are Medinan. The rest are Meccan.
MEDINAN_MUQATTAAT = [2, 3] # Al-Baqarah, Ali 'Imran
MECCAN_MUQATTAAT = [s for s in SET_A_LETTERED_SURAHS if s not in MEDINAN_MUQATTAAT]

# Detailed mapping of exactly which letters open which Surah in Set A
MUQATTAAT_MAPPING = {
    2: "الم",    # Alif Lam Mim
    3: "الم",    # Alif Lam Mim
    7: "المص",   # Alif Lam Mim Sad
    10: "الر",   # Alif Lam Ra
    11: "الر",   # Alif Lam Ra
    12: "الر",   # Alif Lam Ra
    13: "المر",  # Alif Lam Mim Ra
    14: "الر",   # Alif Lam Ra
    15: "الر",   # Alif Lam Ra
    19: "كهيعص", # Kaf Ha Ya Ain Sad
    20: "طه",    # Ta Ha
    26: "طسم",   # Ta Sin Mim
    27: "طس",    # Ta Sin
    28: "طسم",   # Ta Sin Mim
    29: "الم",    # Alif Lam Mim
    30: "الم",    # Alif Lam Mim
    31: "الم",    # Alif Lam Mim
    32: "الم",    # Alif Lam Mim
    36: "يس",    # Ya Sin
    38: "ص",     # Sad
    40: "حم",    # Ha Mim
    41: "حم",    # Ha Mim
    42: "حم عسق", # Ha Mim, Ain Sin Qaf
    43: "حم",    # Ha Mim
    44: "حم",    # Ha Mim
    45: "حم",    # Ha Mim
    46: "حم",    # Ha Mim
    50: "ق",     # Qaf
    68: "ن"      # Nun
}

# The 14 unique combinations
UNIQUE_COMBINATIONS = list(set(MUQATTAAT_MAPPING.values()))

# The 13 unique letters used in the cipher (Out of 28 Arabic letters)
LETTERS_USED = ["ا", "ل", "م", "ص", "ر", "ك", "ه", "ي", "ع", "ط", "س", "ح", "ق", "ن"]
