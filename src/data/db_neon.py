import os
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv
from src.data.db import NeonLabAPI
import requests
import json

load_dotenv()

class NeonLabAPI:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.conn.autocommit = True
        self.api_url = "https://ep-rough-river-aedemse4.apirest.c-2.us-east-2.aws.neon.tech/neondb/rest/v1"
        self.auth_url = "https://ep-rough-river-aedemse4.neonauth.c-2.us-east-2.aws.neon.tech/neondb/auth"
        self.jwks_url = "https://ep-rough-river-aedemse4.neonauth.c-2.us-east-2.aws.neon.tech/neondb/auth/.well-known/jwks.json"

        # Load JWKS from URL
        response = requests.get(self.jwks_url)
        jwks = json.loads(response.text)
        self.keys = jwks['keys']

        # Authenticate with API
        self.auth_token = self.authenticate()

    def authenticate(self):
        # Get public key from JWKS
        public_key = self.get_public_key()

        # Create authentication payload
        payload = {
            "iss": "your_iss",
            "aud": "https://ep-rough-river-aedemse4.apirest.c-2.us-east-2.aws.neon.tech/neondb/rest/v1",
            "exp": 1643723905,
            "iat": 1643723905,
            "sub": "your_sub"
        }

        # Sign payload with private key
        signature = self.sign_payload(payload, public_key)

        # Create authentication request
        auth_request = {
            "grant_type": "client_credentials",
            "client_id": "your_client_id",
            "client_secret": "your_client_secret",
            "signature": signature
        }

        # Send authentication request to API
        response = requests.post(self.auth_url, json=auth_request)

        # Get authentication token from response
        auth_token = response.json()["access_token"]

        return auth_token

    def get_public_key(self):
        # Get public key from JWKS
        public_key = self.keys[0]["x"]
        return public_key

    def sign_payload(self, payload, public_key):
        # Sign payload with private key
        signature = self.private_key.sign(payload, public_key)
        return signature

    def push_surah_metadata(self, data_list):
        # Create authentication header
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        # Create payload
        payload = {
            "surah_id": data_list[0]["surah_id"],
            "surah_name": data_list[0]["surah_name"],
            "revelation_type": data_list[0]["revelation_type"],
            "has_muqattaat": data_list[0]["has_muqattaat"]
        }

        # Send request to API
        response = requests.post(self.api_url + "/surah_metadata", headers=headers, json=payload)

        # Get response from API
        response = response.json()

        return response

    def push_verses(self, surah_id, verses_list):
        # Create authentication header
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        # Create payload
        payload = {
            "surah_id": surah_id,
            "verses": verses_list
        }

        # Send request to API
        response = requests.post(self.api_url + "/verses", headers=headers, json=payload)

        # Get response from API
        response = response.json()

        return response

    def log_finding(self, ticket_id, title, payload):
        # Create authentication header
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        # Create payload
        payload = {
            "ticket_id": ticket_id,
            "title": title,
            "json_payload": payload
        }

        # Send request to API
        response = requests.post(self.api_url + "/findings", headers=headers, json=payload)

        # Get response from API
        response = response.json()

        return response
