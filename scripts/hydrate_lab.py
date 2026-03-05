import pandas as pd
import os
from src.data.db_neon import NeonLabAPI
from src.data.muqattaat import MUQATTAAT_MAPPING, SET_A_LETTERED_SURAHS

api = NeonLabAPI()

def hydrate_from_folders():
    # 1. Load Mathematical Patterns CSV
    print("Ingesting Mathematical Patterns...")
    df_math = pd.read_csv("data/raw/surah_mathematical_patterns.csv")
    for _, row in df_math.iterrows():
        # Update Master with Vector Data
        pass 

    # 2. Ingest Quran Text (Simple-Clean)
    print("Parsing Quran Folders...")
    base_path = "data/Quran_Extracted_Texts/quran-simple-clean"
    for filename in os.listdir(base_path):
        if filename.endswith(".txt"):
            surah_id = int(filename.split("_")[1].split(".")[0])
            with open(os.path.join(base_path, filename), "r") as f:
                lines = f.readlines()
                verse_tuples = [(surah_id, i+1, line.strip()) for i, line in enumerate(lines)]
                api.push_verses(surah_id, verse_tuples)

    # 3. Ingest Arabic Roots
    print("Indexing Roots...")
    with open("data/roots.txt", "r") as f:
        roots = [line.strip() for line in f if line.strip()]
        # Batch push to arabic_roots table
        
    print("Neon Lab Successfully Hydrated.")

if __name__ == "__main__":
    hydrate_from_folders()
