# ADR-003: Policy Is Opt-In Only

## Status
Accepted

## Decision
RFDRepoMan enforces CI, coverage, and protected-branch policy only when the project explicitly declares it in `docs/state/current.md`.

## Consequences
No global default policy is silently applied. Absent policy fields remain explicit report-only absences. A declared policy override requires a separate reason in addition to consequential-action confirmation.
