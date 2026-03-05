# src/data/neon_db.py
import requests

class NeonDB:
    def __init__(self):
        self.api_url = "https://ep-rough-river-aedemse4.apirest.c-2.us-east-2.aws.neon.tech/neondb/rest/v1"
        # Dummy conn attribute to prevent errors in Synthesizer
        self.conn = None

    def get_rejected_hypotheses(self):
        response = requests.get(self.api_url + "/rejected_hypotheses")
        return response.json()

    def add_rejected_hypothesis(self, hypothesis):
        response = requests.post(self.api_url + "/rejected_hypotheses", json={"hypothesis": hypothesis})
        return response.json()
