import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.db import init_db
from backend.seed import seed_database
from backend.main import app


@pytest.fixture
def api(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("ACME_DB_PATH", str(db_path))
    monkeypatch.setenv("ACME_ADMIN_USER", "test-hr")
    monkeypatch.setenv("ACME_ADMIN_PASSWORD", "test-secret")
    init_db(db_path)
    seed_database(db_path, count=120)
    with TestClient(app) as client:
        client.auth = ("test-hr", "test-secret")
        yield client


def get_first(api):
    r = api.get("/api/employees?page_size=1")
    assert r.status_code == 200
    return r.json()["items"][0]
