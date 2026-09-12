# Engineering Team Handbook & Operating Principles

Welcome to the DocuMind Engineering organization. This guide establishes our day-to-day engineering practices and development culture.

## 1. Code Review & Quality Standards
- Every Pull Request (PR) requires a minimum of **2 peer approvals** before merging to `main`.
- All automated continuous integration (CI) tests, security vulnerability scans, and linters must pass with zero errors.
- PR titles must follow Conventional Commits standard (e.g., `feat:`, `fix:`, `refactor:`, `docs:`).

## 2. Release & Deployment Cadence
- Deployments to the staging environment occur continuously upon merging to the default branch.
- Production releases are scheduled on **Tuesday and Thursday mornings at 10:00 AM EST** to maximize team availability.
- No production deployments are allowed on Fridays, weekends, or public holidays except for critical emergency security hotfixes.

## 3. Incident Management & On-Call
- P1 critical incidents require an on-call response time within **15 minutes**.
- A blameless post-mortem root cause analysis (RCA) must be published within **48 hours** of incident resolution.
- On-call rotations run weekly from Monday 9:00 AM EST to the following Monday 9:00 AM EST.
