"""SQLite persistence layer for interview notes."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path

from models import InterviewNote, SearchFilters

DB_PATH = Path("data/interviews.db")
SCHEMA_PATH = Path("data/schema.sql")


class SQLiteStorage:
    """CRUD and search operations for interview notes."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize DB schema on first run."""
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(schema_sql)

    def add_note(self, note: InterviewNote) -> int:
        """Insert one note and return created id."""
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO interview_notes (
                    student_id, student_name, class_name, interview_date,
                    hope_1, hope_2, hope_3, status_study_life, guardian_comment,
                    guidance_todo, free_note, extracted_todo_md, extracted_tags,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    note.student_id,
                    note.student_name,
                    note.class_name,
                    note.interview_date.isoformat(),
                    note.hope_1,
                    note.hope_2,
                    note.hope_3,
                    note.status_study_life,
                    note.guardian_comment,
                    note.guidance_todo,
                    note.free_note,
                    note.extracted_todo_md,
                    note.extracted_tags,
                    now,
                    now,
                ),
            )
            return int(cursor.lastrowid)

    def get_note(self, note_id: int) -> InterviewNote | None:
        """Fetch one note by id."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM interview_notes WHERE id = ?", (note_id,)).fetchone()
        return self._row_to_model(row) if row else None

    def search_notes(self, filters: SearchFilters) -> list[InterviewNote]:
        """Search notes by name/class/date range/keyword."""
        clauses: list[str] = []
        params: list[str] = []
        if filters.student_name:
            clauses.append("student_name LIKE ?")
            params.append(f"%{filters.student_name}%")
        if filters.class_name:
            clauses.append("class_name = ?")
            params.append(filters.class_name)
        if filters.date_from:
            clauses.append("interview_date >= ?")
            params.append(filters.date_from.isoformat())
        if filters.date_to:
            clauses.append("interview_date <= ?")
            params.append(filters.date_to.isoformat())
        if filters.keyword:
            clauses.append(
                "(" + " OR ".join(
                    [
                        "status_study_life LIKE ?",
                        "guardian_comment LIKE ?",
                        "guidance_todo LIKE ?",
                        "free_note LIKE ?",
                    ]
                ) + ")"
            )
            params.extend([f"%{filters.keyword}%"] * 4)

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM interview_notes {where_clause} ORDER BY interview_date DESC, id DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_model(row) for row in rows]

    def list_classes(self) -> list[str]:
        """Return distinct class names."""
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT class_name FROM interview_notes ORDER BY class_name").fetchall()
        return [r[0] for r in rows]

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> InterviewNote:
        """Convert DB row to dataclass model."""
        return InterviewNote(
            id=row["id"],
            student_id=row["student_id"],
            student_name=row["student_name"],
            class_name=row["class_name"],
            interview_date=date.fromisoformat(row["interview_date"]),
            hope_1=row["hope_1"] or "",
            hope_2=row["hope_2"] or "",
            hope_3=row["hope_3"] or "",
            status_study_life=row["status_study_life"] or "",
            guardian_comment=row["guardian_comment"] or "",
            guidance_todo=row["guidance_todo"] or "",
            free_note=row["free_note"] or "",
            extracted_todo_md=row["extracted_todo_md"] or "",
            extracted_tags=row["extracted_tags"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
