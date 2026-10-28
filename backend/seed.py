"""Deterministic synthetic HR dataset (no employee PII). Usage: python -m backend.seed"""
from pathlib import Path
import random
from backend.db import connect, db_path, init_db

FIRST = ("Olivia", "Noah", "Emma", "Liam", "Ava", "Lucas", "Mia", "Leo", "Sofia", "Mateo", "Elena", "Daniel", "Nora", "Alex", "Hana", "Milan", "Ivy", "Omar", "Zoe", "David")
LAST = ("Carter", "Miller", "Kovacs", "Johnson", "Schmidt", "Patel", "Nagy", "Dubois", "Garcia", "Smith", "Bauer", "Brown", "Novak", "Taylor", "Wilson")
DEPARTMENTS = ("Engineering", "Operations", "Product", "Finance", "Sales", "HR", "Customer Success", "Marketing")
# Country, ISO-like currency, annual salary range in currency units.
COUNTRIES = (("US", "USD", 58000, 210000), ("GB", "GBP", 36000, 150000),
             ("DE", "EUR", 42000, 170000), ("HU", "HUF", 7000000, 33000000),
             ("IN", "INR", 900000, 5400000), ("FR", "EUR", 36000, 150000),
             ("ES", "EUR", 29000, 125000), ("CA", "CAD", 56000, 190000),
             ("PL", "PLN", 75000, 420000))


def seed_database(path: Path | str | None = None, count: int = 10_000) -> int:
    if not 1 <= count <= 100_000:
        raise ValueError("count must be between 1 and 100,000")
    target = path or db_path()
    init_db(target)
    rng = random.Random(20261028)
    rows = []
    for index in range(1, count + 1):
        country, currency, low, high = COUNTRIES[(index - 1) % len(COUNTRIES)]
        name = f"{FIRST[rng.randrange(len(FIRST))]} {LAST[rng.randrange(len(LAST))]}"
        dep = DEPARTMENTS[rng.randrange(len(DEPARTMENTS))]
        amount_minor = rng.randrange(low, high + 1) * 100
        code = f"EMP-{index:05d}"
        rows.append((code, name, f"employee{index:05d}@example.invalid", dep, country, currency, amount_minor))
    with connect(target) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            before = conn.execute("SELECT count(*) FROM employees").fetchone()[0]
            conn.executemany("""
              INSERT OR IGNORE INTO employees (employee_code,full_name,email,department,country_code,currency,salary_minor)
              VALUES (?,?,?,?,?,?,?)
            """, rows)
            added = conn.execute("SELECT count(*) FROM employees").fetchone()[0] - before
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return added


if __name__ == "__main__":
    print(f"Added {seed_database()} synthetic employees")
