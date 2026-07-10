# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (activate venv first)
pip install -r requirements.txt

# Run the Flask dev server (once app.py exists)
flask run

# Run all tests
pytest

# Run a single test
pytest tests/test_file.py::test_function_name
```

## Architecture

Spendly is a Flask expense-tracker app using SQLite (no ORM). It is built incrementally as a tutorial — not all files exist yet.

**`database/db.py`** — the data access layer, three functions:
- `get_db()` — opens `spendly.db` with `sqlite3.Row` factory and `PRAGMA foreign_keys = ON`
- `init_db()` — creates tables with `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — inserts sample users and expenses for development

**Database schema** (two tables):
- `users(id, name, email, password_hash, created_at)` — passwords hashed via `werkzeug.security`
- `expenses(id, user_id → users.id CASCADE, amount, category, description, date, created_at)`

**Templates** live in `templates/` and extend `base.html`. Auth routes (`/register`, `/login`) are rendered server-side via Jinja2.

**`app.py`** (not yet created) will be the Flask application entry point that wires routes to templates and calls `init_db()` on startup.
