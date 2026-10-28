"""SQLite access and schema. Connection scope is one API request/operation."""
from contextlib import contextmanager
from pathlib import Path
import os
import sqlite3


def db_path() -> Path:
    return Path(os.getenv("ACME_DB_PATH", "./acme.db"))


@contextmanager
def connect(path: Path | str | None = None):
    target = Path(path) if path is not None else db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(target), timeout=10, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    try:
        yield connection
    finally:
        connection.close()


def init_db(path: Path | str | None = None):
    with connect(path) as conn:
        conn.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_code TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                department TEXT NOT NULL,
                country_code TEXT NOT NULL,
                currency TEXT NOT NULL,
                salary_minor INTEGER NOT NULL CHECK (salary_minor > 0),
                version INTEGER NOT NULL DEFAULT 0 CHECK (version >= 0),
                updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE IF NOT EXISTS salary_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL REFERENCES employees(id),
                old_salary_minor INTEGER NOT NULL,
                new_salary_minor INTEGER NOT NULL,
                currency TEXT NOT NULL,
                reason TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE INDEX IF NOT EXISTS idx_emp_filters ON employees(country_code,department,employee_code);
            CREATE INDEX IF NOT EXISTS idx_emp_currency ON employees(currency,country_code,department);
            CREATE INDEX IF NOT EXISTS idx_emp_name ON employees(full_name);
            CREATE INDEX IF NOT EXISTS idx_changes_employee ON salary_changes(employee_id,id DESC);
        """)
