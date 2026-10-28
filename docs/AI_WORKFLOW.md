# AI-assisted engineering record

**Process.** The assistant helped analyse the assessment, draft scope and acceptance criteria, reason about money/currency semantics, generate implementation scaffolding and tests, and suggest trade-offs. A human submitter must inspect every file, run the full system, review the security posture, and be able to explain the choices before claiming authorship of the submission.

**Initial prompt summary.** “Build an end-to-end salary management system for an HR manager of 10,000 employees. First write a one-page scope/non-goals; prioritise exact money values, auditability, currency-safe insights, deterministic tests and incremental Git commits. Use agentic AI intentionally and retain a reviewable evidence trail.”

**Review checkpoints.** Check for SQL injection (only bound parameters), float money errors (store cents), race conditions (transaction + version), inappropriate mixed-currency analytics (currency filter), exposed compensation data (authenticate APIs), unreproducible seed (fixed random generator), and misleading claims of cloud deployment (not automatic).

**Changes expected from reviewer.** Verify product assumptions with recruiter; verify UI in a browser; supply own remote deployment URL and real walk-through video; revisit backend stack for Java/Angular requirement. No AI transcript or tool logs should be misrepresented as a candidate's personal work.

**Disclosure for interview.** AI assisted with ideation and implementation; key choices—requirements, transaction boundaries, validation, analytics semantics, and architectural trade-offs—must be understood and validated by the submitting engineer.
