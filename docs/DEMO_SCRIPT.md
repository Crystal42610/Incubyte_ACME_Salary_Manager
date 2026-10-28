# Video demo and engineering walkthrough

`ACME_Salary_Manager_Demo.mp4` is a short **silent screen-recorded demo** of the implemented user flows. The recording uses synthetic employee data and calls the running backend; the browser and backend were exercised together during its capture. A public hosting URL is not implied.

## Suggested 45–60 second narrated walkthrough for the candidate

1. **The problem.** "ACME has salary spreadsheets for 10,000 employees. This is a scoped HR workspace to replace the most error-prone day-to-day work."
2. **Directory.** "The application seeds 10,000 synthetic employees. I use indexed data, server-side pagination, filters and a search over name, employee ID and email."
3. **Salary edit.** "Every compensation change requires a reason. The backend stores amounts as integer minor units, writes the new salary and audit event in one transaction, and rejects stale versions rather than silently losing an update."
4. **Insights.** "The dashboard calculates average, median and department/country groups, but only within one currency; mixed-currency global averages without FX assumptions would be misleading."
5. **Trade-offs.** "I intentionally excluded payroll and currency conversion. The code is structured so a future import pipeline, SSO/RBAC and PostgreSQL migration can be added without rewriting the core domain."
6. **AI and tests.** "I used AI for requirements analysis, scaffolding and checks, then validated the critical rules with deterministic unit and API tests. I preserved the incremental commits and documented how the tool was used."

## Checks actually performed in this workspace

- `pytest -q`: 22 passing tests (including the 10,000-record local timing smoke test).
- `node --check frontend/app.js`: JavaScript syntax valid.
- Browser interaction smoke test: sign-in → 20 employee rows → search EMP-00042 → edit → audit history → Pay insights (4 summary cards). No JavaScript runtime errors were observed.
- Screenshots: `ui-directory.png`, `ui-insights.png`.

## Remaining candidate-owned steps

- Review all generated code and requirements in a local IDE; decide if the allowed Python/React stack is acceptable for the Java/Angular role.
- Push the repository and preserve its commit history. Confirm CI passes in the remote Git host.
- Deploy with a managed persistent volume and TLS; set a strong secret and do not expose a public demo with real PII.
- Record a voice-narrated walkthrough (or use the supplied silent video if accepted); include a working URL and repository link in the recruiter reply.
