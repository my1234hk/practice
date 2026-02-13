# 三者面談メモ管理アプリ（MVP）

三者面談メモを **入力しやすく**・**後で探しやすく**・**配布用に整形しやすく** する、ローカル実行向けのStreamlitアプリです。

## 動作環境
- Python 3.11+
- ローカルPC（外部API不要）

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動手順
```bash
streamlit run app.py
```

ブラウザで表示されたURL（通常 `http://localhost:8501`）を開いて利用してください。

## 使い方（MVP）
1. **入力** タブで面談メモを登録
2. **一覧・検索** タブで氏名/クラス/日付/キーワード検索
3. 検索結果のIDを選び **詳細** タブで整形表示
4. 詳細画面からMarkdown/HTMLをダウンロード

## データの保存先
- SQLite DB: `data/interviews.db`
- サンプルSQL: `data/sample_data.sql`

## サンプルデータ投入
初期デモ用の3件データを投入できます。

```bash
python scripts/seed_data.py
```

> 既存データが1件以上ある場合は重複投入を防ぐためスキップされます。

## 保存スキーマ（`interview_notes`）
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `student_id` TEXT NOT NULL
- `student_name` TEXT NOT NULL
- `class_name` TEXT NOT NULL
- `interview_date` TEXT NOT NULL (YYYY-MM-DD)
- `hope_1` TEXT
- `hope_2` TEXT
- `hope_3` TEXT
- `status_study_life` TEXT
- `guardian_comment` TEXT
- `guidance_todo` TEXT
- `free_note` TEXT
- `extracted_todo_md` TEXT
- `extracted_tags` TEXT
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

## 最低限の手動テスト手順
1. `streamlit run app.py` で画面起動する
2. 入力画面で必須項目を空にして保存し、バリデーションエラーが出ることを確認
3. 必須項目を入力して保存し、成功メッセージが出ることを確認
4. 一覧・検索で氏名部分一致/クラス/日付/キーワードが機能することを確認
5. 詳細でToDo箇条書き・抽出タグが表示されることを確認
6. 詳細画面のMarkdown/HTMLダウンロードが可能なことを確認

## テスト実行
```bash
pytest -q
```
