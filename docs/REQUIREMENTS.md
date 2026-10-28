# ACME Salary Manager — one-page product requirements (v1)

**Persona and problem.** A single authorised HR manager needs to replace unwieldy spreadsheets holding compensation for approximately 10,000 employees in multiple countries. The manager must safely maintain salaries and answer practical questions about how the organisation pays staff.

**Goal and measures of success.** In under a minute, HR can find an employee, update salary with a mandatory explanation, and inspect the previous amount. HR can explore headcount and salary distributions without exporting spreadsheets. The application remains responsive for 10,000 records using server-side pagination, filtering, and aggregation.

**In scope — MVP**
1. **Protected HR access** using a single environment-configured administrator (demonstration only; no public employee access).
2. **Employee directory:** 10,000 realistic synthetic employees seeded through a repeatable script; search by name, code or email; filter by country, department; paginate and sort.
3. **Compensation editing:** display exact salary and ISO currency; edit amount with positive-value validation and a mandatory reason; prohibit silent currency changes; avoid lost updates using a record-version check.
4. **Audit trail:** persist who changed each salary, before/after values and an UTC timestamp; show history per employee.
5. **Pay insights:** headcount, mean, median, min/max and department/country breakouts **for a selected currency only**; never add together money in different currencies.
6. **Quality:** accessible, responsive web UI; documented REST API; deterministic seed, fast automated tests, deployment configuration, and a reproducible demo.

**Explicit non-goals and why.** Payroll runs, tax, benefits and salary approvals introduce compliance/workflow complexity not needed to validate HR salary management. Foreign-exchange conversion would require agreed rates and date semantics; misleading global totals are worse than currency-level reporting. Bulk Excel imports, SSO, granular permissions and employee deletion are important production follow-ups but require specification of source schemas, identity provider, authorisation rules and retention policies. Historical analytics are not inferred from the one current snapshot; the audit records future edits only.

**Acceptance examples.** Searching “EMP-00042” finds one record; 10,000 seed runs do not duplicate rows; editing salary creates exactly one audit record; a stale version returns HTTP 409; negative or over-precision amounts are rejected; no salary endpoints are available without authorisation; analytics only group one currency at a time. No real employee data is stored in the demonstration.

**Assumptions to validate with stakeholders.** One HR administrator is sufficient for the assessment; salary is annual gross base compensation; employee country and currency are fixed in the MVP; analytics use active employees and current salary, not historical payroll figures.
