# ADR-002: Force Push Is Not Exposed

## Status
Accepted

## Decision
No force-push or force-update parameter, function, or configuration exists in RFDRepoMan. Adding force behavior requires a superseding ADR.

## Consequences
Confirmation cannot enable force behavior. Callers must use a separate, intentionally designed system if a future superseding ADR authorizes one.
