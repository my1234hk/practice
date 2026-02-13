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

## 使い方（MVP）
1. **入力**: 面談メモを登録（必須: 生徒ID/氏名/クラス）
2. **一覧・検索**:
   - 氏名の部分一致
   - クラス絞り込み
   - 面談日（期間指定）
   - キーワード（自由メモを含む全文対象）
3. 一覧は **面談日降順（デフォルト）** で表示
4. 一覧で表示件数とページを指定して必要データだけ確認
5. 詳細画面で配布・印刷向けの整形表示を確認し、Markdown/HTMLを出力
6. 一覧画面の **全データCSVバックアップ** でDB全件をCSV出力

## データの保存先
- SQLite DB: `data/interviews.db`
- スキーマ: `data/schema.sql`
- サンプルSQL: `data/sample_data.sql`

## サンプルデータ投入
簡単なデモデータ（3件）を投入できます。

```bash
python seed.py
```

または

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
1. `python seed.py` を実行してデモデータを投入
2. `streamlit run app.py` で起動する
3. 一覧・検索で以下を確認
   - 氏名部分一致（例: `山`）
   - クラス絞り込み（例: `3年B組`）
   - 期間指定（開始日/終了日）
   - キーワード検索（例: `受験`, `スマホ`）
4. 一覧の表示件数とページを変更し、表示範囲が変わることを確認
5. 一覧の **全データCSVバックアップ** ボタンからCSVが落とせることを確認
6. 詳細画面で以下を確認
   - 見出しとメタ情報表示
   - 志望校が表形式で整列
   - ToDoが箇条書き
   - Markdown/HTMLダウンロード

## テスト実行
```bash
pytest -q
```
