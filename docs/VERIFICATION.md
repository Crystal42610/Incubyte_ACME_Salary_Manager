# Verification notes — 28 October 2026

The application is an assessment-sized HR workspace, not a production payroll service. The data contains **10,000 synthetic employees**; it includes no real salary or personal information.

## What I verified

- `python -m backend.seed` inserted 10,000 records into a new local SQLite database.
- `python -m pytest -q` reported **24 passed**. Tests cover API authentication, salary validation, atomic edits and audit entries, stale-version conflicts, searching, filtering, currency-specific analytics, headers, and a 10k-record timing smoke check.
- `python -m compileall -q backend scripts` and `node --check frontend/app.js` completed successfully.
- The read-only `scripts/check_live.py` smoke check passed against the local synthetic-data server (not a public deployment).
- The full silent browser walkthrough exercised the local backend through sign-in, directory browsing, searching, filtering, sorting, a salary edit and its history, analytics in EUR/USD/HUF, and re-login to verify the saved change. The capture was automated at a readable, natural pace; it was not filmed from a public hosted site.

## What I could not verify in this environment

- The **React 19** production bundle and Docker frontend build. The npm registry was unavailable here; the full UI video therefore uses the previously working browser client with the same product flows and the updated API. After `npm install && npm run build`, check the current app in a real browser before treating the video as representative of the final release.
- A live **HTTPS deployment with a persistent disk**. `render.yaml` documents a deployment route, but only the candidate can connect a hosting account, configure a secret and verify the live URL and restart persistence.
- Whether Incubyte prefers **modern Angular / Java** for this role despite the assessment allowing React and an alternative backend. The implementation uses FastAPI/React and this must be explained, not passed off as Java/Angular.
- Remote GitHub Actions status after the latest changes. Recheck the **Actions** tab once the revision has been pushed.

## Reviewer notes

The core compensation safeguards are deliberate: salary amounts use integer minor units rather than binary floats, every actual edit needs a reason, the audit entry and new salary commit together, and a version mismatch returns HTTP 409. Analytics never add together different currencies. These decisions are explained in `DESIGN.md`; AI assistance and review responsibilities are stated in `AI_WORKFLOW.md`.

Before submitting, add the deployed URL to the root README, test all primary actions on it, confirm secrets remain private, and verify the exposed GitHub token was revoked.
