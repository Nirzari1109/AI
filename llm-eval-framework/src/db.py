import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eval_results.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create the results table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eval_results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          TEXT NOT NULL,
            question_id     TEXT NOT NULL,
            question        TEXT NOT NULL,
            topic           TEXT NOT NULL,
            difficulty      TEXT NOT NULL,
            expected_answer TEXT NOT NULL,
            actual_answer   TEXT NOT NULL,
            routed_to       TEXT NOT NULL,
            faithfulness    REAL NOT NULL,
            relevance       REAL NOT NULL,
            latency_ms      REAL NOT NULL,
            timestamp       TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("DB initialised.")

def save_result(run_id, question_id, question, topic, difficulty,
                expected_answer, actual_answer, routed_to,
                faithfulness, relevance, latency_ms):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO eval_results
        (run_id, question_id, question, topic, difficulty,
         expected_answer, actual_answer, routed_to,
         faithfulness, relevance, latency_ms, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id, question_id, question, topic, difficulty,
        expected_answer, actual_answer, routed_to,
        faithfulness, relevance, latency_ms,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eval_results ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_results_by_run(run_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM eval_results WHERE run_id = ? ORDER BY timestamp",
        (run_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows