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
The offline React demo bundles React 16.0.0 because that was the only verified locally available runtime in the isolated build environment. It supports the class-component UI and was browser-tested, but **React 16 is outdated and should not be considered a production-ready dependency choice**. For a production submission, migrate to a maintained React version with Vite and pinned dependencies, or obtain clarification and implement modern Angular with the Java backend. This technical-debt caveat is intentional and must not be concealed.
