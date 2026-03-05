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
        # ... rest of the code ...
