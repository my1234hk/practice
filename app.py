"""Streamlit application for managing parent-student-teacher interview notes."""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import streamlit as st

from exporter import to_html, to_markdown
from extractor import extract_tags, normalize_todo_to_markdown
from models import InterviewNote, SearchFilters
from storage import SQLiteStorage

st.set_page_config(page_title="三者面談メモ", layout="wide")


def validate_input(student_id: str, student_name: str, class_name: str) -> list[str]:
    """Validate required input fields and return error messages."""
    errors = []
    if not student_id.strip():
        errors.append("生徒ID（または出席番号）は必須です。")
    if not student_name.strip():
        errors.append("氏名は必須です。")
    if not class_name.strip():
        errors.append("クラスは必須です。")
    return errors


def render_form(storage: SQLiteStorage) -> None:
    """Render form page and handle insert action."""
    st.header("面談メモの追加")
    with st.form("note_form"):
        student_id = st.text_input("生徒ID（または出席番号）*")
        student_name = st.text_input("氏名*")
        class_name = st.text_input("クラス*")
        interview_date = st.date_input("面談日", value=date.today())
        hope_1 = st.text_input("志望1")
        hope_2 = st.text_input("志望2")
        hope_3 = st.text_input("志望3")
        status_study_life = st.text_area("現状（学習・生活）")
        guardian_comment = st.text_area("保護者コメント")
        guidance_todo = st.text_area("指導方針／次回までのToDo")
        free_note = st.text_area("自由メモ")
        submitted = st.form_submit_button("保存")

    if submitted:
        errors = validate_input(student_id, student_name, class_name)
        if errors:
            for error in errors:
                st.error(error)
            return

        try:
            todo_md = normalize_todo_to_markdown(guidance_todo)
            tags = ",".join(extract_tags(status_study_life, guardian_comment, guidance_todo, free_note))
            note = InterviewNote(
                student_id=student_id.strip(),
                student_name=student_name.strip(),
                class_name=class_name.strip(),
                interview_date=interview_date,
                hope_1=hope_1.strip(),
                hope_2=hope_2.strip(),
                hope_3=hope_3.strip(),
                status_study_life=status_study_life.strip(),
                guardian_comment=guardian_comment.strip(),
                guidance_todo=guidance_todo.strip(),
                free_note=free_note.strip(),
                extracted_todo_md=todo_md,
                extracted_tags=tags,
            )
            note_id = storage.add_note(note)
            st.toast(f"保存しました（ID: {note_id}）", icon="✅")
            st.success("面談メモを保存しました。")
        except Exception as exc:  # noqa: BLE001
            st.error(f"保存中にエラーが発生しました: {exc}")


def render_list(storage: SQLiteStorage) -> None:
    """Render list/search page and capture selected note id."""
    st.header("一覧・検索")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input("氏名（部分一致）")
    with col2:
        class_options = [""] + storage.list_classes()
        class_name = st.selectbox("クラス", class_options)
    with col3:
        date_from = st.date_input("開始日", value=None)
    with col4:
        date_to = st.date_input("終了日", value=None)
    keyword = st.text_input("キーワード（自由メモ含む）")

    options_col1, options_col2, options_col3 = st.columns([1, 1, 2])
    with options_col1:
        page_size = st.selectbox("表示件数", [10, 20, 50], index=0)
    with options_col2:
        page_no = st.number_input("ページ", min_value=1, step=1, value=1)
    with options_col3:
        st.caption("並び順: 面談日降順（新しい順）")

    filters = SearchFilters(
        student_name=name.strip(),
        class_name=class_name,
        date_from=date_from if isinstance(date_from, date) else None,
        date_to=date_to if isinstance(date_to, date) else None,
        keyword=keyword.strip(),
    )

    try:
        notes = storage.search_notes(filters)
    except Exception as exc:  # noqa: BLE001
        st.error(f"検索中にエラーが発生しました: {exc}")
        return

    csv_text = storage.export_all_as_csv()
    st.download_button(
        "全データCSVバックアップ",
        data=csv_text,
        file_name=f"interview_notes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        disabled=not bool(csv_text),
    )

    if not notes:
        st.info("該当データがありません。")
        return

    start = (int(page_no) - 1) * int(page_size)
    end = start + int(page_size)
    page_notes = notes[start:end]
    total_pages = max(1, (len(notes) + int(page_size) - 1) // int(page_size))
    st.caption(f"{len(notes)}件中 {start + 1}〜{min(end, len(notes))}件を表示（{int(page_no)}/{total_pages}ページ）")

    if not page_notes:
        st.warning("そのページにはデータがありません。ページ番号を戻してください。")
        return

    df = pd.DataFrame(
        [
            {
                "id": n.id,
                "面談日": n.interview_date.isoformat(),
                "氏名": n.student_name,
                "クラス": n.class_name,
                "志望1": n.hope_1,
                "タグ": n.extracted_tags,
            }
            for n in page_notes
        ]
    )
    st.dataframe(df.drop(columns=["id"]), use_container_width=True)

    selected_id = st.selectbox("詳細表示するID", [n.id for n in page_notes], index=0)
    if st.button("このIDを詳細表示", type="primary"):
        st.session_state["selected_note_id"] = selected_id
        st.session_state["page"] = "詳細"
        st.rerun()


def render_detail(storage: SQLiteStorage) -> None:
    """Render detail page with markdown/html exports."""
    st.header("1件詳細（配布・印刷向け）")
    note_id = st.session_state.get("selected_note_id")
    if not note_id:
        st.info("一覧画面からIDを選択してください。")
        return

    note = storage.get_note(int(note_id))
    if not note:
        st.error("対象データが見つかりません。")
        return

    st.markdown("---")
    st.subheader("三者面談メモ")
    st.caption(f"ID: {note.id}")

    meta_col1, meta_col2, meta_col3 = st.columns(3)
    meta_col1.markdown(f"**氏名**: {note.student_name}")
    meta_col2.markdown(f"**クラス**: {note.class_name}")
    meta_col3.markdown(f"**面談日**: {note.interview_date.isoformat()}")
    st.markdown(f"**生徒ID**: {note.student_id}  ")
    st.markdown(f"**抽出タグ**: {note.extracted_tags or 'なし'}")

    st.markdown("### 志望校")
    hopes_df = pd.DataFrame(
        [
            {"順位": "第1志望", "学校名": note.hope_1},
            {"順位": "第2志望", "学校名": note.hope_2},
            {"順位": "第3志望", "学校名": note.hope_3},
        ]
    )
    st.table(hopes_df)

    st.markdown("### 現状（学習・生活）")
    st.write(note.status_study_life or "（記載なし）")

    st.markdown("### 保護者コメント")
    st.write(note.guardian_comment or "（記載なし）")

    st.markdown("### 指導方針／次回までのToDo")
    st.markdown(note.extracted_todo_md or "- （記載なし）")

    st.markdown("### 自由メモ")
    st.write(note.free_note or "（記載なし）")

    markdown_text = to_markdown(note)
    html_text = to_html(note)

    st.download_button("Markdownをダウンロード", markdown_text, file_name=f"note_{note.id}.md")
    st.download_button("印刷向けHTMLをダウンロード", html_text, file_name=f"note_{note.id}.html")


def main() -> None:
    """Application entrypoint."""
    st.title("三者面談メモ管理アプリ（MVP）")
    storage = SQLiteStorage()
    page = st.sidebar.radio("画面", ["入力", "一覧・検索", "詳細"], key="page")

    if page == "入力":
        render_form(storage)
    elif page == "一覧・検索":
        render_list(storage)
    else:
        render_detail(storage)


if __name__ == "__main__":
    main()
