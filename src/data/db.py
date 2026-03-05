# src/data/db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv
from src.core.state import Hypothesis

load_dotenv()

def get_db_connection():
    """Establishes a secure connection to the Neon PostgreSQL instance."""
    url = os.getenv("DATABASE_URL")
    # Neon often requires sslmode=require for remote connections
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def record_hypothesis(run_id: str, hyp: Hypothesis, status: str = "RAW", reason: str = None):
    """Saves agent findings to the cloud finding log for persistent memory."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload, score_boost)
            VALUES (%s, %s, %s, %s)
        """, (
            run_id, 
            f"{hyp.source_scout} Discovery - Surah {hyp.surah_refs}",
            Json({
                "scout": hyp.source_scout,
                "goal": hyp.goal_link,
                "description": hyp.description,
                "evidence": hyp.evidence_snippets,
                "status": status,
                "rejection_reason": reason
            }),
            hyp.score
        ))
        conn.commit()
    except Exception as e:
        print(f"[DB Error]: {e}")
    finally:
        cur.close()
        conn.close()

class NeonLabAPI:
    """
    Central API endpoints for all agents. 
    Allows 24/7 data access and event recording without local file overhead.
    """
    def __init__(self):
        self.conn = get_db_connection()
        self.conn.autocommit = True

    def open_ticket(self, run_id: str, role: str, pattern: str):
        """Domain 2: Event API - Agents 'clock in' to start research."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO c2_research_ticket (ticket_id, agent_role, target_pattern, status)
                VALUES (%s, %s, %s, 'Executing')
                ON CONFLICT (ticket_id) DO UPDATE SET status = 'Executing'
            """, (run_id, role, pattern))

    def get_surah_context(self, surah_id: int):
        """Domain 1: Corpus Data - Fetches metadata and clean text for an agent."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT m.*, STRING_AGG(v.text_clean, ' ' ORDER BY v.verse_number) as content
                FROM surah_master m
                JOIN verse_data v ON m.surah_id = v.surah_id
                WHERE m.surah_id = %s
                GROUP BY m.surah_id
            """, (surah_id,))
            return cur.fetchone()

    def update_flow_matrix(self, from_l: str, to_l: str, weight: float):
        """Updates the Rigid Flow Matrix based on frequency discoveries."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO rigid_flow_matrix (from_letter, to_letter, probability_weight)
                VALUES (%s, %s, %s)
                ON CONFLICT DO UPDATE SET probability_weight = EXCLUDED.probability_weight
            """, (from_l, to_l, weight))

def init_db_schema():
    """Initializes the multi-domain schema in Neon."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Domain 1: Cryptographic Corpus
    cur.execute("""
        CREATE TABLE IF NOT EXISTS surah_master (
            surah_id INT PRIMARY KEY, surah_name VARCHAR(100), total_verses INT,
            has_muqattaat BOOLEAN, vector_magnitude FLOAT, checksum_cluster_id INT
        );
        CREATE TABLE IF NOT EXISTS muqattaat_prefix (
            prefix_id SERIAL PRIMARY KEY, surah_id INT REFERENCES surah_master(surah_id),
            letters_sequence VARCHAR(20), abjad_weight INT, anchor_verse_index INT, saturation_percentage FLOAT
        );
        CREATE TABLE IF NOT EXISTS verse_data (
            verse_id SERIAL PRIMARY KEY, surah_id INT REFERENCES surah_master(surah_id),
            verse_number INT, text_uthmani TEXT, text_clean TEXT, is_anchor_flare BOOLEAN, prefix_density_ratio FLOAT
        );
        CREATE TABLE IF NOT EXISTS rigid_flow_matrix (
            transition_id SERIAL PRIMARY KEY, from_letter CHAR(1), to_letter CHAR(1),
            probability_weight FLOAT, is_forbidden BOOLEAN
        );
        
        -- Domain 2: Command & Control (C2)
        CREATE TABLE IF NOT EXISTS c2_research_ticket (
            ticket_id VARCHAR(50) PRIMARY KEY, agent_role VARCHAR(50),
            target_pattern TEXT, status VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS c2_finding_log (
            log_id SERIAL PRIMARY KEY, ticket_id VARCHAR(50), discovery_title VARCHAR(200),
            json_payload JSONB, score_boost FLOAT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Neon Lab Schema Initialized.")
