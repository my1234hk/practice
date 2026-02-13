"""Data models for interview note application."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(slots=True)
class InterviewNote:
    """Represents one interview memo record."""

    student_id: str
    student_name: str
    class_name: str
    interview_date: date
    hope_1: str = ""
    hope_2: str = ""
    hope_3: str = ""
    status_study_life: str = ""
    guardian_comment: str = ""
    guidance_todo: str = ""
    free_note: str = ""
    extracted_todo_md: str = ""
    extracted_tags: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    id: int | None = None


@dataclass(slots=True)
class SearchFilters:
    """Search conditions used in the list screen."""

    student_name: str = ""
    class_name: str = ""
    date_from: date | None = None
    date_to: date | None = None
    keyword: str = ""
