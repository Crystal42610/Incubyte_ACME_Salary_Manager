# ACME Salary Manager

A scoped HR salary-management MVP: searchable employee directory, salary editing with audit history and optimistic concurrency, and currency-safe analytics for **10,000 entirely synthetic employees**.

## Quick start (Python 3.11+)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ACME_ADMIN_USER=hr-admin
export ACME_ADMIN_PASSWORD='set-a-strong-password'
export ACME_DB_PATH=./acme.db
python -m backend.seed
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000 and sign in with the configured user/password. API docs: http://127.0.0.1:8000/docs. **Never use a real person's compensation data.**

```bash
pytest -q
```

## Container deployment

```bash
docker compose up --build -d
```

Provide `ACME_ADMIN_PASSWORD` in an `.env` file (see `.env.example`), bind TLS at the reverse proxy and use the persistent `salary_data` volume. For an external hosting provider, build with `Dockerfile`, provision a persistent `/data` mount, set `ACME_ADMIN_USER`, `ACME_ADMIN_PASSWORD`, `ACME_DB_PATH=/data/acme.db`, and enforce HTTPS. **A deployed URL is not included: deploying requires the candidate's cloud account and access.**

## Demo flow

1. Login as HR manager; verify the dashboard counts 10,000 seeded employees.
2. Search `EMP-00042`; filter a country, department, and navigate pages.
3. Open an employee, edit salary with a reason, and save. Review the audit log.
4. Switch the dashboard currency; compare departments or countries without mixing money units.
5. Submit a stale version to the API to demonstrate the 409 conflict response.

## Structure

- `docs/REQUIREMENTS.md` — one-page product framing and explicit non-goals (written before implementation)
- `docs/DESIGN.md` — architecture, safety, testing and trade-offs
- `docs/AI_WORKFLOW.md` — AI usage and human review checklist
- `backend/` — endpoints, SQL persistence, salary domain rules and deterministic seed
- `frontend/` — static React UI (vendored React runtime for a build-free demo)
- `tests/` — automated API, domain, concurrency and performance smoke tests

**Backend/frontend choice:** FastAPI + React falls under the brief's *alternative backend* and *ReactJS* allowances but is **not the preferred Java/Angular technology**; see `docs/DESIGN.md` before submitting for the Java/Angular role.

## Evidence

- `docs/ui-directory.png` and `docs/ui-insights.png`: captured UI states.
- `docs/ACME_Salary_Manager_Demo.mp4`: silent screen-recorded end-to-end walkthrough.
- `docs/DEMO_SCRIPT.md`: narration outline and verification evidence.
- `git log --oneline`: scope → red tests → backend → UI → release hardening.

**Current limitations:** No public deployment has been performed, browser runtime React 16 is outdated and must be updated before production use, and enterprise SSO/permissions are outside this scoped assessment. A local functional MVP is not equivalent to a production-ready salary system handling real compensation data.
