import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "content_scores.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_text TEXT NOT NULL,
                topic TEXT,
                grade_level INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER NOT NULL,
                difficulty TEXT,
                difficulty_score REAL,
                quality_score REAL,
                answer_text TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (content_id) REFERENCES content(id)
            );
        """)


def store_content_and_scores(problem_text: str, topic: str | None, grade_level: int | None,
                             difficulty: str, difficulty_score: float, quality_score: float,
                             answer_text: str):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO content (problem_text, topic, grade_level) VALUES (?, ?, ?)",
            (problem_text, topic, grade_level),
        )
        content_id = cur.lastrowid
        conn.execute(
            """INSERT INTO scores (content_id, difficulty, difficulty_score, quality_score, answer_text)
               VALUES (?, ?, ?, ?, ?)""",
            (content_id, difficulty, difficulty_score, quality_score, answer_text),
        )
    return content_id
