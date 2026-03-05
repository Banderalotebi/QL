# src/data/db_neon.py
import psycopg2
import json
import requests

class NeonLabAPI:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.conn.autocommit = True
        self.api_url = "https://ep-rough-river-aedemse4.apirest.c-2.us-east-2.aws.neon.tech/neondb/"
        self.auth_url = "https://ep-rough-river-aedemse4.neonauth.c-2.us-east-2.aws.neon.tech/neond"
        self.jwks_url = "https://ep-rough-river-aedemse4.neonauth.c-2.us-east-2.aws.neon.tech/neond"

    def get_public_key(self):
        # Load JWKS from URL
        response = requests.get(self.jwks_url)
        jwks = json.loads(response.text)
        self.keys = jwks['keys']

    def sign_payload(self, payload, public_key):
        # ... rest of the code ...

    def record_hypothesis(self, hypothesis):
        # Add the function body here
        pass

    def get_verse_math(self, surah_id: int):
        """Returns prefix density ratios for all verses in a Surah."""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT verse_number, prefix_density_ratio 
                FROM verse_data WHERE surah_id = %s ORDER BY verse_number
            """, (surah_id,))
            return cur.fetchall()

    def fetch_septenary_cluster(self):
        """Returns Surahs belonging to the mathematical '7' cluster."""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM surah_master WHERE checksum_cluster_id = 7")
            return cur.fetchall()

    def create_ticket(self, ticket_id, role, pattern):
        # ... rest of the code ...

    def log_finding(self, ticket_id, title, payload, score):
        # ... rest of the code ...

    def push_verses(self, surah_id, verse_tuples):
        # ... rest of the code ...

    def log_discovery(self, ticket_id: str, title: str, payload: dict, score: float):
        """Saves a discovery and closes the ticket."""
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload, score_boost)
                VALUES (%s, %s, %s, %s)
            """, (ticket_id, title, Json(payload), score))
            cur.execute("UPDATE c2_research_ticket SET status = 'Completed' WHERE ticket_id = %s", (ticket_id,))
        print(f"✅ Discovery Logged: {title} (Ticket: {ticket_id})")
