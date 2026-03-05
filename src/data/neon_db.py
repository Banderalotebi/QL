# src/data/neon_db.py
import sqlite3

class NeonDB:
    def __init__(self):
        self.conn = sqlite3.connect("neon.db")
        self.cursor = self.conn.cursor()

    def get_rejected_hypotheses(self):
        self.cursor.execute("SELECT * FROM rejected_hypotheses")
        return self.cursor.fetchall()

    def add_rejected_hypothesis(self, hypothesis):
        self.cursor.execute("INSERT INTO rejected_hypotheses VALUES (?)", (hypothesis,))
        self.conn.commit()
