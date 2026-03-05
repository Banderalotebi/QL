# src/data/db_neon.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes a secure connection to the Neon PostgreSQL instance."""
    url = os.getenv("DATABASE_URL")
    # Neon often requires sslmode=require for remote connections
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

class NeonLabAPI:
    """
    Central API endpoints for all agents. 
    Allows 24/7 data access and event recording without local file overhead.
    """
    def __init__(self):
        self.conn = get_db_connection()
        self.conn.autocommit = True

    def record_hypothesis(self, hypothesis):
        """Saves agent findings to the cloud finding log for persistent memory."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload, score_boost)
                VALUES (%s, %s, %s, %s)
            """, (
                "example_ticket", 
                f"{hypothesis.source_scout} Discovery - Surah {hypothesis.surah_refs}",
                Json({
                    "scout": hypothesis.source_scout,
                    "goal": hypothesis.goal_link,
                    "description": hypothesis.description,
                    "evidence": hypothesis.evidence_snippets,
                    "status": "RAW",
                    "rejection_reason": None
                }),
                hypothesis.score
            ))
            conn.commit()
        except Exception as e:
            print(f"[DB Error]: {e}")
        finally:
            cur.close()
            conn.close()
