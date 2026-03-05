# src/data/db.py
import sqlite3
import requests

class NeonLabAPI:
    def __init__(self):
        self.conn = sqlite3.connect("neon.db")
        self.api_url = "https://ep-rough-river-aedemse4.apirest.c-2.us-east-2.aws.neon.tech/neondb/rest/v1"

    def record_hypothesis(self, hypothesis):
        response = requests.post(self.api_url + "/hypotheses", json={"hypothesis": hypothesis})
        return response.json()
