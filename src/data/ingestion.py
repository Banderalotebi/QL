from src.data.db import get_db_connection

def load_surah_text(surah_number: int, script_type: str = "quran-simple-clean") -> str:
    """Load text from Neon DB (Primary) or Local File (Fallback)."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT content FROM quran_texts WHERE surah_id = %s AND script_type = %s LIMIT 1",
            (surah_number, script_type)
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return row['content']
    except Exception as e:
        print(f"[DB Warning]: {e}. Falling back to local files.")
    
    # ... existing local file loading logic here ...
