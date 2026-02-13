"""Rule-based extraction helpers for todo bullets and tags."""

from __future__ import annotations

import re

TAG_KEYWORDS = (
    "欠席",
    "遅刻",
    "提出",
    "受験",
    "部活",
    "生活リズム",
    "スマホ",
    "睡眠",
)


def normalize_todo_to_markdown(todo_text: str) -> str:
    """Convert free-form todo text into markdown bullets."""
    if not todo_text.strip():
        return ""
    parts = re.split(r"[\n。]|\s*[・-]\s*|\s*\d+\.\s*", todo_text)
    items = [p.strip() for p in parts if p.strip()]
    return "\n".join(f"- {item}" for item in items)


def extract_tags(*texts: str) -> list[str]:
    """Extract unique tags from input texts by keyword matching."""
    merged = "\n".join(t for t in texts if t)
    found = sorted({tag for tag in TAG_KEYWORDS if tag in merged})
    return found
