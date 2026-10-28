"""Informational smoke checks, not load testing or performance SLOs."""
from time import perf_counter
from backend.db import init_db
from backend.seed import seed_database
from backend import service


def test_directory_and_analytics_on_10k_rows(tmp_path, monkeypatch):
    db = tmp_path / "perf.sqlite3"
    monkeypatch.setenv("ACME_DB_PATH", str(db))
    init_db(db)
    assert seed_database(db, count=10_000) == 10_000
    start = perf_counter()
    result = service.directory(q="EMP-07777", page_size=25)
    directory_ms = (perf_counter() - start) * 1000
    start = perf_counter()
    stats = service.analytics("EUR")
    analytics_ms = (perf_counter() - start) * 1000
    assert result["total"] == 1
    assert result["items"][0]["employee_code"] == "EMP-07777"
    assert stats["headcount"] > 1000
    # Deliberately no brittle timing assertions: capture locally and judge with a profiler.
    print(f"10k records: filtered directory {directory_ms:.1f}ms; EUR analytics {analytics_ms:.1f}ms")
