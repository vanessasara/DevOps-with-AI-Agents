import sqlite3
import os
from datetime import datetime

class PatternStore:
    def __init__(self, db_path: str = "data/pattern_memory.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    resolution TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_incident(self, pattern: str, resolution: str):
        """
        Store incident for future reference.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO incidents (pattern, resolution) VALUES (?, ?)",
                (pattern, resolution)
            )

    def get_context_for_agent(self, pattern: str) -> str:
        """
        Return similar past incidents based on simple pattern matching.
        In a real scenario, this would use vector search.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Simple keyword matching for demo purposes
            cursor = conn.execute(
                "SELECT pattern, resolution FROM incidents WHERE pattern LIKE ?",
                (f"%{pattern}%",)
            )
            matches = cursor.fetchall()
            
            if not matches:
                return ""
            
            context = "Past similar incidents:\n"
            for p, r in matches:
                context += f"- Pattern: {p}\n  Resolution: {r}\n"
            return context
