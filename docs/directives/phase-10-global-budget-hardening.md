# RFDRepoMan — Phase 10 Directive: Global Budget & Pre-Loop Timeout Hardening

*July 2026 | Read fully before executing anything.*

## Context

Phase 10 bounds credential subprocesses, filesystem discovery at the reconciliation call site, and the entire multi-account reconciliation operation. It does not add process-level cancellation for in-flight HTTP work.

## Scope

| File | Action |
|---|---|
| `repoman/config.py` | Add explicit GitHub CLI subprocess timeout. |
| `repoman/github_status.py` | Bound discovery and apply an outer global budget. |
| `repoman/server.py` | Expose optional global budget. |
| `docs/adr/ADR-005-bounded-execution-layers.md` | Record timeout layers and limitation. |
| `tests/test_phase10.py` | Add hardening tests. |
| `docs/directives/phase-10-global-budget-hardening.md` | Preserve this directive. |

## Requirements

GitHub CLI calls use a five-second subprocess timeout. Reconciliation computes a default global budget of `per_account_budget_seconds * account_count + 15`, echoes the actual value in its result, and returns cached/truncated account results once exhausted. Local discovery is bounded at the reconciliation call site; direct discovery behavior is unchanged.

Target: 71 passing, 0 failing, 0 skipped.
