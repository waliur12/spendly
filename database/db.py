import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'spendly.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return user


def create_user(name, email, password):
    conn = get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, generate_password_hash(password)),
    )
    conn.commit()
    conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return user


def get_user_expenses(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, amount, category, date, description "
        "FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def get_user_expense_summary(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total, "
        "COALESCE(AVG(amount), 0) AS average FROM expenses WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row


def get_user_category_breakdown(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category, COUNT(*) AS count, SUM(amount) AS total "
        "FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def seed_db():
    conn = get_db()

    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        conn.close()
        return

    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    conn.commit()

    user_id = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()["id"]

    sample_expenses = [
        (user_id, 42.50,  "Food",          "2026-07-01", "Weekly groceries"),
        (user_id, 18.00,  "Transport",     "2026-07-02", "Monthly bus pass"),
        (user_id, 95.00,  "Bills",         "2026-07-03", "Internet bill"),
        (user_id, 30.00,  "Health",        "2026-07-04", "Pharmacy"),
        (user_id, 14.99,  "Entertainment", "2026-07-05", "Streaming subscription"),
        (user_id, 65.00,  "Shopping",      "2026-07-07", "New headphones"),
        (user_id, 20.00,  "Other",         "2026-07-08", "Birthday card & gift"),
        (user_id, 11.50,  "Food",          "2026-07-09", "Lunch out"),
    ]

    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses,
    )
    conn.commit()
    conn.close()
