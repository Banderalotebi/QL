import os
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv

load_dotenv()

class NeonLabAPI:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.conn.autocommit = True

    def get_cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def push_surah_metadata(self, data_list):
        """Batch insert from surah names/numbers CSV."""
        query = """
            INSERT INTO surah_master (surah_id, surah_name, revelation_type, has_muqattaat)
            VALUES %s ON CONFLICT (surah_id) DO UPDATE SET surah_name = EXCLUDED.surah_name
        """
        with self.get_cursor() as cur:
            execute_values(cur, query, data_list)

    def push_verses(self, surah_id, verses_list):
        """verses_list: list of tuples (surah_id, verse_num, text_clean)"""
        query = "INSERT INTO verse_data (surah_id, verse_number, text_clean) VALUES %s"
        with self.get_cursor() as cur:
            execute_values(cur, query, verses_list)

    def log_finding(self, ticket_id, title, payload):
        """Saves an agent's discovery to the JSONB cloud storage."""
        with self.get_cursor() as cur:
            cur.execute(
                "INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload) VALUES (%s, %s, %s)",
                (ticket_id, title, psycopg2.extras.Json(payload))
            )
