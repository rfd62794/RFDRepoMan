# ADR-005: Bounded Reconciliation Execution Layers

- **Status:** Accepted
- **Date:** 2026-07-19
- **Decision owners:** Project Maintainers

## Decision

Reconciliation applies layered bounds:

- GitHub CLI credential subprocesses: 5 seconds.
- GitHub request timeout: 8 seconds.
- Per-account reconciliation budget: 25 seconds by default.
- Global reconciliation budget: `per_account_budget_seconds * account_count + 15` by default.
- Local repository discovery: bounded at the reconciliation call site by the remaining global budget and request timeout.

When a budget is exhausted, reconciliation returns cache-backed or truncated account data instead of waiting indefinitely. The applied global budget is included in the result.

## Known Limitation

The daemon-thread timeout mechanism returns control to the caller but cannot cancel an HTTP operation already executing in its daemon thread. This is an accepted limitation; request, account, and global budgets reduce exposure but do not provide full cancellation.
