"""Formatting helpers for markdown and print-friendly HTML outputs."""

from __future__ import annotations

from models import InterviewNote


def to_markdown(note: InterviewNote) -> str:
    """Render one interview note as markdown text."""
    return f"""# 三者面談メモ

- 生徒ID: {note.student_id}
- 氏名: {note.student_name}
- クラス: {note.class_name}
- 面談日: {note.interview_date.isoformat()}
- タグ: {note.extracted_tags}

## 志望
1. {note.hope_1}
2. {note.hope_2}
3. {note.hope_3}

## 現状（学習・生活）
{note.status_study_life}

## 保護者コメント
{note.guardian_comment}

## 指導方針／次回までのToDo
{note.extracted_todo_md or note.guidance_todo}

## 自由メモ
{note.free_note}
"""


def to_html(note: InterviewNote) -> str:
    """Render one interview note as print-friendly HTML."""
    todo_html = (note.extracted_todo_md or note.guidance_todo).replace("\n", "<br>")
    return f"""<!doctype html>
<html lang='ja'>
<head>
<meta charset='utf-8'>
<title>三者面談メモ</title>
<style>
body {{ font-family: sans-serif; margin: 24px; line-height: 1.6; }}
h1 {{ border-bottom: 1px solid #bbb; }}
section {{ margin-bottom: 16px; }}
</style>
</head>
<body>
<h1>三者面談メモ</h1>
<p><strong>生徒ID:</strong> {note.student_id} / <strong>氏名:</strong> {note.student_name} / <strong>クラス:</strong> {note.class_name} / <strong>面談日:</strong> {note.interview_date.isoformat()}</p>
<p><strong>タグ:</strong> {note.extracted_tags}</p>
<section><h2>志望</h2><ol><li>{note.hope_1}</li><li>{note.hope_2}</li><li>{note.hope_3}</li></ol></section>
<section><h2>現状（学習・生活）</h2><p>{note.status_study_life}</p></section>
<section><h2>保護者コメント</h2><p>{note.guardian_comment}</p></section>
<section><h2>指導方針／次回までのToDo</h2><p>{todo_html}</p></section>
<section><h2>自由メモ</h2><p>{note.free_note}</p></section>
</body>
</html>"""
