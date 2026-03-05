# src/data/db.py
import psycopg2
import json
import requests
import os  # I added this line to import the os module

class NeonLabAPI:
    def __init__(self):
        self.api_url = "https://ep-rough-river-aedemse4.apirest.c-2.us-east-2.aws.neon.tech/neondb/"
        self.auth_url = "https://ep-rough-river-aedemse4.neonauth.c-2.us-east-2.aws.neon.tech/neondb/"
        self.jwks_url = "https://ep-rough-river-aedemse4.neonauth.c-2.us-east-2.aws.neon.tech/neondb/"
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        
        self.conn.autocommit = True  # I added this line back in

    def get_public_key(self):
        # Load JWKS from URL
        response = requests.get(self.jwks_url)
        jwks = json.loads(response.text)
        self.keys = jwks['keys']

    def sign_payload(self, payload, public_key):
        # ... rest of the code ...

        # I added this line to fix the indentation error
        return payload
