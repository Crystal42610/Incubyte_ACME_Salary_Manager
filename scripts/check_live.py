"""Read-only smoke test for a deployed synthetic-data ACME Salary Manager."""
import base64
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def main():
    base = os.getenv("ACME_DEMO_URL", "").rstrip("/")
    user = os.getenv("ACME_ADMIN_USER", "")
    password = os.getenv("ACME_ADMIN_PASSWORD", "")
    parsed = urlparse(base)
    local = parsed.hostname in {"localhost", "127.0.0.1"}
    if not base or not user or not password:
        sys.exit("Set ACME_DEMO_URL, ACME_ADMIN_USER and ACME_ADMIN_PASSWORD first.")
    if parsed.scheme != "https" and not (local and parsed.scheme == "http"):
        sys.exit("Refusing to send credentials except over HTTPS or local loopback HTTP.")

    auth = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")

    def get(path, authenticated=True):
        headers = {"Accept": "application/json"}
        if authenticated:
            headers["Authorization"] = f"Basic {auth}"
        with urlopen(Request(f"{base}{path}", headers=headers), timeout=15) as response:
            return json.load(response)

    try:
        assert get("/api/health", False)["status"] == "ok"
        assert get("/api/me")["role"] == "HR Manager"
        meta = get("/api/meta")
        assert meta["total"] == 10_000, f"Expected 10,000 records, got {meta['total']}"
        employee = get("/api/employees?q=" + quote("EMP-00042"))
        assert employee["total"] == 1
        assert employee["items"][0]["employee_code"] == "EMP-00042"
        for currency in ("EUR", "USD", "HUF"):
            info = get("/api/analytics?currency=" + currency)
            assert info["currency"] == currency
            assert info["headcount"] == sum(group["headcount"] for group in info["by_department"])
        print(f"PASS: health, HR access, 10,000 employees, search, and EUR/USD/HUF analytics at {base}")
        print("Read-only check; no salary information was changed.")
    except (AssertionError, HTTPError, URLError, ValueError) as exc:
        sys.exit(f"FAIL: {exc}")


if __name__ == "__main__":
    main()
