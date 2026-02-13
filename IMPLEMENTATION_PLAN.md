# MVP実装計画: 三者面談メモ管理アプリ

## 0. 背景・目的
- 三者面談メモを「入力しやすく」「後で探しやすく」「配布しやすく」管理するローカルアプリを作る。
- 教員PC上で単独利用でき、ブラウザUIから直感的に操作できることを優先する。
- 初期MVPでは、運用上の負担が少ない構成を採用し、将来のLLM要約やPDF化に拡張しやすい設計にする。

## 1. 採用技術（MVP提案）
- **UI**: Streamlit
  - 理由: フォーム・一覧・詳細画面を少ないコードで実装しやすい。
  - `streamlit run app.py` で起動可能という要件に合う。
- **永続化**: **SQLiteを第一候補**（CSVはエクスポート用途）
  - SQLiteをMVPで推奨する理由:
    - 氏名/クラス/日付/キーワード検索をSQLで安定実装しやすい。
    - 文字列検索・将来の複数テーブル化・更新処理に強い。
    - 単一ファイル運用（`data/interviews.db`）で配布が容易。
  - CSVを主DBにしない理由:
    - 更新・検索条件の増加に伴い実装複雑化しやすい。
    - 同時更新や型の扱いが曖昧になりやすい。

## 2. GitHub Issue風 要件整理

### 2-1. 機能要件（MVP）
- [ ] 面談メモの追加（フォーム入力）
- [ ] 一覧表示
- [ ] 検索・絞り込み
  - [ ] 氏名
  - [ ] クラス
  - [ ] 面談日（単日/期間）
  - [ ] キーワード（自由メモ・現状・保護者コメント・ToDo対象）
- [ ] 1件詳細表示（見やすい整形レイアウト）
- [ ] エクスポート
  - [ ] 印刷しやすいHTML表示
  - [ ] Markdown出力（ファイル保存または画面コピー）
- [ ] ルールベース要点抽出
  - [ ] ToDo欄の箇条書き正規化
  - [ ] 重要語タグ付け（例: 欠席/遅刻/提出/受験/部活/生活リズム など）

### 2-2. 非機能要件（MVP）
- [ ] ローカルPCのみで動作（外部API不要）
- [ ] 日本語入力を前提（UTF-8）
- [ ] データファイルの場所がREADMEで明確
- [ ] 初回起動時にDB自動作成
- [ ] 例データ投入で即デモ可能

### 2-3. 将来拡張（設計のみ）
- [ ] LLM要約・要点抽出モジュールを差し替え可能な構造
- [ ] PDFエクスポート（HTML→PDF変換等）
- [ ] ユーザー認証・アクセス制御（将来）

## 3. 画面設計（Streamlit想定）

### 3-1. 画面A: 面談メモ入力
- 入力項目:
  - 生徒ID（または出席番号）
  - 氏名
  - クラス
  - 面談日
  - 志望1〜3
  - 現状（学習・生活）
  - 保護者コメント
  - 指導方針／次回までのToDo
  - 自由メモ
- 補助UI:
  - [保存] ボタン
  - バリデーションエラー表示（必須項目）
  - 保存成功トースト

### 3-2. 画面B: 一覧・検索
- フィルタ:
  - 氏名（部分一致）
  - クラス（選択）
  - 面談日（期間）
  - キーワード（全文対象）
- 結果表示:
  - テーブル（面談日、氏名、クラス、志望1、タグ）
  - 行選択で詳細へ

### 3-3. 画面C: 1件詳細（整形ビュー）
- 見出し:
  - 氏名・クラス・面談日
- セクション:
  - 志望
  - 現状（学習・生活）
  - 保護者コメント
  - 指導方針／ToDo（箇条書き整形）
  - 自由メモ
  - ルールベース抽出タグ
- 操作:
  - Markdown出力
  - 印刷向けHTML表示

## 4. データ構造（SQLite）

### 4-1. テーブル案: `interview_notes`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `student_id` TEXT NOT NULL
- `student_name` TEXT NOT NULL
- `class_name` TEXT NOT NULL
- `interview_date` TEXT NOT NULL（ISO: YYYY-MM-DD）
- `hope_1` TEXT
- `hope_2` TEXT
- `hope_3` TEXT
- `status_study_life` TEXT
- `guardian_comment` TEXT
- `guidance_todo` TEXT
- `free_note` TEXT
- `extracted_todo_md` TEXT（ルールベース整形結果）
- `extracted_tags` TEXT（CSV形式 or JSON文字列）
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

### 4-2. インデックス案（検索高速化）
- `idx_interview_date` on `interview_date`
- `idx_student_name` on `student_name`
- `idx_class_name` on `class_name`

### 4-3. サンプルデータ
- 最低3件（学年・クラス・課題タイプが異なる）
- 初期投入方法:
  - `data/sample_data.sql` を初回セットアップ時に実行
  - または `python scripts/seed_data.py`

## 5. ルールベース要点抽出（MVP）
- ToDo整形:
  - 改行・句点・記号（`・`,`-`,`1.`）を分割して箇条書き化
- タグ抽出:
  - キーワード辞書マッチ（例: `欠席`, `遅刻`, `提出`, `受験`, `スマホ`, `睡眠`）
  - 重複排除し、重要度順（辞書順）で保存
- 将来拡張のため、抽出関数を `services/summarizer.py` に分離

## 6. 想定ファイル構成（MVP）
- `app.py`（Streamlitエントリポイント）
- `README.md`（起動方法・保存先・使い方）
- `requirements.txt`
- `data/`
  - `interviews.db`（実行時作成）
  - `sample_data.sql`
- `db/`
  - `schema.sql`
  - `repository.py`（CRUD + 検索）
- `services/`
  - `extractor.py`（ルールベース要点抽出）
  - `exporter.py`（Markdown/HTML整形）
- `ui/`
  - `form_view.py`
  - `list_view.py`
  - `detail_view.py`
- `scripts/`
  - `seed_data.py`
- `tests/`
  - `test_extractor.py`
  - `test_repository.py`

## 7. 実装ステップ（作業分解）
1. [ ] プロジェクト初期化（requirements, README雛形）
2. [ ] DBスキーマ作成 + 初回起動時マイグレーション処理
3. [ ] Repository層（追加・一覧・検索・1件取得）
4. [ ] ルールベース抽出（ToDo整形、タグ付け）
5. [ ] Streamlit入力画面実装（追加）
6. [ ] Streamlit一覧検索画面実装
7. [ ] Streamlit詳細画面 + Markdown/HTML出力
8. [ ] サンプルデータ投入スクリプト
9. [ ] テスト実装・実行
10. [ ] README最終化

## 8. MVP範囲（In/Out）

### In Scope
- ローカル実行
- Streamlit UI
- SQLite保存
- 追加/一覧検索/詳細/Markdown・印刷向けHTML
- ルールベース要点抽出
- 例データ投入

### Out of Scope（MVP外）
- PDF生成の自動化
- LLM API連携による要約
- 複数ユーザー同時利用と認証
- クラウド同期

## 9. テスト観点

### 9-1. 単体テスト
- `extractor.py`
  - ToDoテキストが期待どおり箇条書き化される
  - キーワードからタグ抽出できる
- `repository.py`
  - 追加→取得の整合性
  - 氏名/クラス/日付/キーワード検索の条件一致

### 9-2. 結合テスト（手動）
- 画面Aで登録した内容が画面Bに表示される
- 画面Bの絞り込み結果から画面Cへ遷移できる
- 画面CのMarkdown/HTML出力が意図どおり整形される

### 9-3. 受け入れ確認
- `streamlit run app.py` で起動できる
- READMEどおりに初期セットアップできる
- サンプルデータで検索デモが成立する

## 10. Definition of Done（MVP）
- [ ] 上記4機能（追加/一覧検索/詳細/出力）が動作
- [ ] SQLiteファイルが所定位置に作成される
- [ ] READMEに起動手順・保存先・サンプルデータ投入手順を記載
- [ ] 主要ロジックに最低限のテストがある
- [ ] 手動確認チェックリストを満たす
