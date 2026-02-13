CREATE TABLE IF NOT EXISTS interview_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    interview_date TEXT NOT NULL,
    hope_1 TEXT,
    hope_2 TEXT,
    hope_3 TEXT,
    status_study_life TEXT,
    guardian_comment TEXT,
    guidance_todo TEXT,
    free_note TEXT,
    extracted_todo_md TEXT,
    extracted_tags TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_interview_date ON interview_notes(interview_date);
CREATE INDEX IF NOT EXISTS idx_student_name ON interview_notes(student_name);
CREATE INDEX IF NOT EXISTS idx_class_name ON interview_notes(class_name);
