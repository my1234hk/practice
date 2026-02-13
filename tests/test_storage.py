from datetime import date

from extractor import extract_tags, normalize_todo_to_markdown
from models import InterviewNote, SearchFilters
from storage import SQLiteStorage


def make_note(name: str, class_name: str, interview_date: date, memo: str) -> InterviewNote:
    """Create test note with normalized todo and tags."""
    todo = "提出物を出す。睡眠改善"
    return InterviewNote(
        student_id=f"id-{name}",
        student_name=name,
        class_name=class_name,
        interview_date=interview_date,
        status_study_life=memo,
        guardian_comment="保護者コメント",
        guidance_todo=todo,
        free_note=f"自由メモ:{memo}",
        extracted_todo_md=normalize_todo_to_markdown(todo),
        extracted_tags=",".join(extract_tags(memo, todo)),
    )


def test_add_get_search(tmp_path):
    db_path = tmp_path / "test.db"
    storage = SQLiteStorage(db_path=db_path)

    id1 = storage.add_note(make_note("山田", "3A", date(2026, 5, 1), "欠席がある"))
    storage.add_note(make_note("佐藤", "3B", date(2026, 5, 2), "部活と受験"))

    note = storage.get_note(id1)
    assert note is not None
    assert note.student_name == "山田"

    by_name = storage.search_notes(SearchFilters(student_name="山"))
    assert len(by_name) == 1

    by_class = storage.search_notes(SearchFilters(class_name="3B"))
    assert len(by_class) == 1

    by_date = storage.search_notes(SearchFilters(date_from=date(2026, 5, 2), date_to=date(2026, 5, 2)))
    assert len(by_date) == 1

    by_keyword = storage.search_notes(SearchFilters(keyword="受験"))
    assert len(by_keyword) == 1

    by_free_note_keyword = storage.search_notes(SearchFilters(keyword="自由メモ:部活"))
    assert len(by_free_note_keyword) == 1


def test_export_all_as_csv(tmp_path):
    storage = SQLiteStorage(db_path=tmp_path / "export.db")
    storage.add_note(make_note("田中", "2A", date(2026, 6, 1), "提出あり"))

    csv_text = storage.export_all_as_csv()
    assert "student_name" in csv_text
    assert "田中" in csv_text
