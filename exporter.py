"""Formatting helpers for markdown and print-friendly HTML outputs."""

from __future__ import annotations

from models import InterviewNote


def _todo_items(note: InterviewNote) -> list[str]:
    """Return ToDo list items from extracted markdown or free text."""
    source = note.extracted_todo_md or note.guidance_todo
    items: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        items.append(stripped.removeprefix("- "))
    return items


def to_markdown(note: InterviewNote) -> str:
    """Render one interview note as markdown text."""
    todo_md = "\n".join(f"- {item}" for item in _todo_items(note)) or "- （記載なし）"
    return f"""# 三者面談メモ

- 生徒ID: {note.student_id}
- 氏名: {note.student_name}
- クラス: {note.class_name}
- 面談日: {note.interview_date.isoformat()}
- タグ: {note.extracted_tags}

## 志望校
| 順位 | 学校名 |
|---|---|
| 第1志望 | {note.hope_1} |
| 第2志望 | {note.hope_2} |
| 第3志望 | {note.hope_3} |

## 現状（学習・生活）
{note.status_study_life or '（記載なし）'}

## 保護者コメント
{note.guardian_comment or '（記載なし）'}

## 指導方針／次回までのToDo
{todo_md}

## 自由メモ
{note.free_note or '（記載なし）'}
"""


def to_html(note: InterviewNote) -> str:
    """Render one interview note as print-friendly HTML."""
    todo_list = "".join(f"<li>{item}</li>" for item in _todo_items(note)) or "<li>（記載なし）</li>"
    return f"""<!doctype html>
<html lang='ja'>
<head>
<meta charset='utf-8'>
<title>三者面談メモ</title>
<style>
body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; margin: 24px; line-height: 1.7; color: #222; }}
h1 {{ border-bottom: 2px solid #777; padding-bottom: 8px; margin-bottom: 16px; }}
.meta {{ margin-bottom: 12px; }}
.meta span {{ display: inline-block; min-width: 240px; margin: 4px 0; }}
section {{ margin: 16px 0; }}
h2 {{ margin-bottom: 8px; border-left: 4px solid #777; padding-left: 8px; font-size: 1.1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
</style>
</head>
<body>
<h1>三者面談メモ</h1>
<div class="meta">
  <span><strong>生徒ID:</strong> {note.student_id}</span>
  <span><strong>氏名:</strong> {note.student_name}</span>
  <span><strong>クラス:</strong> {note.class_name}</span>
  <span><strong>面談日:</strong> {note.interview_date.isoformat()}</span>
</div>
<p><strong>タグ:</strong> {note.extracted_tags or 'なし'}</p>
<section>
  <h2>志望校</h2>
  <table>
    <tr><th>順位</th><th>学校名</th></tr>
    <tr><td>第1志望</td><td>{note.hope_1}</td></tr>
    <tr><td>第2志望</td><td>{note.hope_2}</td></tr>
    <tr><td>第3志望</td><td>{note.hope_3}</td></tr>
  </table>
</section>
<section><h2>現状（学習・生活）</h2><p>{note.status_study_life or '（記載なし）'}</p></section>
<section><h2>保護者コメント</h2><p>{note.guardian_comment or '（記載なし）'}</p></section>
<section><h2>指導方針／次回までのToDo</h2><ul>{todo_list}</ul></section>
<section><h2>自由メモ</h2><p>{note.free_note or '（記載なし）'}</p></section>
</body>
</html>"""
