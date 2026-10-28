# Design decisions and trade-offs

## Architecture
Browser (React) → same-origin FastAPI REST endpoints → SQLite (WAL, indexed tables). A single container serves the UI and API. A separate seed script creates 10,000 fake employees. Read queries paginate or aggregate in the database; salary edits are atomic transactions.

## Stack choice
The brief explicitly permits **any backend framework** and **ReactJS** for the UI. Python/FastAPI + SQLite + React were chosen to minimise setup and prove a complete, tested end-to-end vertical slice quickly. The candidate applied for Java/Angular; Java/Spring Boot and modern Angular would better demonstrate that preferred stack, but the brief's wording “AngularJS for Java” is ambiguous (AngularJS 1.x versus modern Angular). **This implementation is not Java/Angular**. Confirm the acceptability of the permitted alternative before presenting this as a final role-specific submission.

## Data and correctness
Amounts are stored as integer minor units rather than floating point. The UI shows two decimals in a currency-localised label; no conversion is performed. Salary updates require a reason and expected version. A database transaction checks the version and writes the new value plus the audit event together. Stale updates return HTTP 409, so conflicting HR changes cannot overwrite one another unnoticed.

## Access and privacy
The demo uses environment-provided HTTP Basic credentials with constant-time comparison; the browser retains the credential only in React memory (refresh requires sign-in). Do not deploy with the local example password. Use TLS and private hosting; no real salary data. Before a genuine enterprise rollout use SSO/OIDC, RBAC, secret management, audit retention, structured logs, backups, monitoring, and privacy review. For demo purposes one admin user is a documented compromise, not production-grade enterprise IAM.

## Persistence and scale
SQLite and B-tree indexes are adequate for one 10,000-employee assessment instance. WAL improves concurrent reads; `BEGIN IMMEDIATE` serialises edits and ensures audit atomicity. On multiple replicas, migrate to PostgreSQL and use managed backups. Deploy with a persistent data volume; ephemeral container filesystem will lose edits after redeployment.

## UX and accessibility
Search/filter controls remain visible, loading/error/empty states are explicit, inline forms have labels, tables have headers, interaction uses native buttons/inputs, and status updates use `role=status`. Do not claim WCAG certification without audit. Dashboard uses tables/bars rather than ungrounded financial comparisons.

## Meaningful tests and measurement
Unit/service and API tests cover salary parsing, validation, authentication, search/pagination, analytics, history, idempotent seed and optimistic concurrency. Deterministic seeded records prevent flaky assertions. `tests/test_performance.py` provides a local timing smoke test on 10,000 rows; not a performance SLO or load test.

## Delivery plan and incremental commits
1. Freeze the one-page requirements and acceptance criteria.
2. Write representative tests first (red stage).
3. Implement transactional service/API and seeding (green stage).
4. Add the React interface and error handling.
5. Run tests, audit the result and document deployment/demo/AI use.

## Clarifications for Incubyte
Does “AngularJS for Java” mean AngularJS 1.x, or is current Angular acceptable? May the brief's explicit alternative backend/React provision be used for a Java/Angular opening? Is a single HR admin with synthetic data sufficient, or is SSO expected? Is local-currency salary analysis preferred to unspecified FX conversion? Can Hungary-based candidates apply to the Remote–India opening?

## Dependency/version note
The initial prototype used vendored React 16. The submission hardening change replaces it with pinned React 19.3.1 / React DOM 19.3.1 and an esbuild-generated local bundle. The bundle is produced during container build and by `npm run build` for local development. CI must pass and the candidate must run a browser smoke test before submission. `package-lock.json` should be generated and committed during candidate setup; unlike the Python tests, frontend package installation could not be verified inside the isolated assistance environment.

## Deployment
`render.yaml` describes a Render Docker web service using a paid persistent disk for SQLite. The container rejects well-known example passwords, runs without root privileges, and exposes a 2xx health endpoint. A deploy is only completed when the candidate connects their Render account, sets a unique secret and verifies the live URL. See `docs/DEPLOY_RENDER.md`.

## Demo auth UX
HTTP Basic errors no longer carry `WWW-Authenticate`, preventing the browser's native popup while retaining the application's own sign-in form. Credentials are stored in memory only, and HTTPS is mandatory on a public demo. Single-admin HTTP Basic authentication is still a documented limitation for real-world use.

## Final UI review note

A full browser walkthrough exposed an issue where returning after sign-out could retain the previous page and search context. The logout handler now clears employee data, filters, page, analytics selection and current record state, then returns to the directory on the next login. This is a small example of why reviewing the complete user journey matters alongside unit testing.

The directory also offers a nominal salary sort across multiple currencies. It sorts the stored numbers, not equivalent purchasing power or exchange-adjusted amounts; HR should not interpret it as a global compensation ranking. A future version should require a single-currency filter before allowing comparative salary sorting.
