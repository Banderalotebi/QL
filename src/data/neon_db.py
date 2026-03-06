# src/data/neon_db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class NeonDB:
    """
    Database connection for Neon PostgreSQL with graceful degradation.
    """
    def __init__(self):
        self.url = os.getenv("DATABASE_URL")
        self.conn = None
        self.is_connected = False
        self.connect()

    def connect(self):
        """Attempt to connect to Neon PostgreSQL."""
        if not self.url:
            print("⚠️ DATABASE_URL not set - database operations disabled")
            return

        try:
            self.conn = psycopg2.connect(self.url, cursor_factory=RealDictCursor, connect_timeout=5)
            self.is_connected = True
            print("✅ Connected to Neon PostgreSQL")
        except psycopg2.OperationalError as e:
            print(f"⚠️ Failed to connect to Neon: {str(e)[:80]}")
            self.is_connected = False
        except Exception as e:
            print(f"⚠️ Database error: {str(e)[:80]}")
            self.is_connected = False

    def log_hypothesis(self, hypothesis, status="RAW", reason=None):
        """Log a hypothesis to the database."""
        if not self.is_connected or not self.conn:
            return False

        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload, score_boost)
                VALUES (%s, %s, %s, %s)
            """, (
                f"HYP_{datetime.now().timestamp()}",
                f"{hypothesis.source_scout} - {hypothesis.surah_refs}",
                Json({
                    "scout": hypothesis.source_scout,
                    "goal": hypothesis.goal_link,
                    "description": hypothesis.description,
                    "evidence": hypothesis.evidence_snippets,
                    "complexity": hypothesis.transformation_steps,
                    "status": status,
                    "reason": reason
                }),
                hypothesis.score
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"⚠️ Error logging hypothesis: {str(e)[:80]}")
            return False

    def get_rejected_hypotheses(self):
        """
        Get rejected hypotheses from database.
        """
        if not self.is_connected or not self.conn:
            return []

        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM c2_finding_log WHERE json_payload->>'status' = 'REJECTED' LIMIT 100")
            return cur.fetchall()
        except Exception as e:
            print(f"⚠️ Error retrieving hypotheses: {str(e)[:80]}")
            return []
        finally:
            cur.close()

    def close(self):
        """Close database connection safely."""
        if self.conn:
            self.conn.close()
            self.is_connected = False
