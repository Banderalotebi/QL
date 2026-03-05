# src/data/db.py
import requests
import json

class NeonLabAPI:
    def __init__(self):
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

    def record_hypothesis(self, hypothesis):
        # Create authentication header
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        # Create hypothesis payload
        payload = {
            "hypothesis": hypothesis
        }

        # Send hypothesis request to API
        response = requests.post(self.api_url + "/hypotheses", headers=headers, json=payload)

        # Get response from API
        response = response.json()

        return response
