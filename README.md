# ACME Salary Manager

An assessment-scale, end-to-end salary management application for an HR manager of an organisation with **10,000 synthetic employees**. It includes a searchable directory, salary editing with an audit trail and conflict detection, and salary analytics that never add together different currencies.

**Live demo:** Pending candidate deployment. Follow [Render deployment instructions](docs/DEPLOY_RENDER.md) and replace this line with the HTTPS URL after verifying it.

## Assessment evidence

- [One-page requirements and non-goals](docs/REQUIREMENTS.md) — committed before implementation.
- [Architecture](docs/ARCHITECTURE.md), [design choices / limitations](docs/DESIGN.md), [AI-assisted work record](docs/AI_WORKFLOW.md).
- [Full silent walkthrough](docs/ACME_Salary_Manager_Demo.mp4) of the working local HR application: sign-in, 10k directory, pagination, search and filters, salary change and audit, pay insights across currencies, and sign-in again to confirm the edit persisted. Screenshots are in `docs/`. The recording exercises the updated backend against the earlier working browser client; the React 19 build must still be checked after installing npm packages.
- [Verification notes](docs/VERIFICATION.md) and [submission checklist](docs/SUBMISSION_CHECKLIST.md) — what passed locally and what still needs the candidate’s final check.

## Tech stack and rationale

- API: Python 3.12, FastAPI, parameterised SQLite queries with WAL and indexed access.
- UI: React **19.3.1**, locally bundled with esbuild 0.28.2 (no browser CDN dependency).
- Testing: pytest API/service/10k performance smoke checks; GitHub Actions builds the frontend and Docker image.
- Hosting: single Docker service with a persistent volume, HTTPS via a hosting proxy.

The brief allows an alternative backend and React. **This is not the preferred Java/Angular stack for the role.** Please clarify this choice with Incubyte before claiming it meets their role-specific expectations.

## Run locally (Windows CMD, Python 3.11+ and Node.js 22+)

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
npm install
npm run build
set ACME_ADMIN_USER=hr-admin
set ACME_ADMIN_PASSWORD=choose-a-unique-private-password
set ACME_DB_PATH=acme.db
python -m backend.seed
python -m pytest -q
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Visit http://127.0.0.1:8000 and sign in on the page. The admin password comes from your environment variable, **not from the repository**. If you run Docker, use a `.env` file with your unique credentials, and run `docker compose up --build -d` (ports are local-only by default).

`npm install` should generate `package-lock.json`; commit the lockfile with this project. Check the production bundle in the browser after installing the packages. The isolated assessment build environment could run the Python tests but could not download the React dependencies.

## Walkthrough

The approximately 3-minute-39-second silent video shows the complete HR journey at a natural pace, followed by a short walkthrough of the actual product requirements, design trade-offs, verification results and AI-assisted workflow. It starts with administrator sign-in, checks a 10,000-person directory, goes through pagination and filters, edits `EMP-00042` with a reason, reopens the audit entry, looks at empty search results, compares currency-specific analytics, and signs out and back in to check persistence.

For a quick hands-on review, search `EMP-00042`, make a change with a reason, and inspect that employee’s change history. For a concurrency check, repeat an update with a stale `expected_version`; the API returns `409` rather than overwriting the current record.

The recording is a **local synthetic-data demonstration**, not evidence of a public deployment. Its UI was captured from the previously working client against the hardened backend while npm package access was unavailable. The application still needs the maintained React 19 bundle and live HTTPS deployment verified.

## Verify a deployed instance

After deployment, use the read-only smoke check (it does not modify salary data). On Windows CMD, set `ACME_DEMO_URL`, `ACME_ADMIN_USER` and `ACME_ADMIN_PASSWORD` in your current terminal, then run:

```cmd
python scripts/check_live.py
```

The script checks the health endpoint, HR credentials, 10,000-employee seed, employee search and EUR/USD/HUF analytics. It refuses to send credentials to non-HTTPS hosts, except local loopback for development. Then manually check salary edit/audit and redeploy persistence in your browser.

## Production limitations

The product has one admin identity, HTTP Basic credentials sent over HTTPS, SQLite single-instance storage, and synthetic data only. A real multi-country compensation system would need SSO, granular RBAC, compliance and privacy review, backup/restore, logging, and a managed relational database. This assessment implementation is not a production payroll platform.

**Never commit `.env`, tokens, or real employee salary records.**
