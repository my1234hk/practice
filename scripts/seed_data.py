"""Seed sample interview notes into local SQLite database."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage import SQLiteStorage


def seed() -> None:
    """Load sample SQL records if table is currently empty."""
    storage = SQLiteStorage()

    with sqlite3.connect(storage.db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM interview_notes").fetchone()[0]
        if count > 0:
            print("Seed skipped: records already exist.")
            return
        sql = (ROOT / "data/sample_data.sql").read_text(encoding="utf-8")
        conn.executescript(sql)
        print("Seed completed: sample records inserted.")


if __name__ == "__main__":
    seed()
