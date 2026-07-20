# RFDRepoMan — Phase 9 Directive: Bounded Reconciliation, Pagination & Local Cache

*July 2026 | Read fully before executing anything.*

## Context

Reconciliation must return predictably for large accounts. This phase adds per-account budgets, page-based fetching, and a gitignored two-snapshot local cache so partial scans preserve completed work.

## Scope

| File | Action |
|---|---|
| `repoman/github_status.py` | Add bounded paginated reconciliation and cache fallback. |
| `repoman/reconcile_cache.py` | Add two-snapshot runtime cache. |
| `repoman/server.py` | Expose bounded reconciliation defaults. |
| `.gitignore` | Exclude runtime cache. |
| `tests/test_phase9.py` | Add budget, cache, and pagination tests. |
| `docs/directives/phase-9-bounded-reconciliation-pagination-cache.md` | Preserve this directive. |

## Requirements

The MCP reconciliation default disables PR-count expansion, uses a 25-second per-account budget, and allows explicit force refresh. Cache data is stored under `.repoman_cache/`, is never committed, and retains only current and previous snapshots.

A daemon-thread timeout returns control to the caller but does not cancel underlying HTTP work. This accepted limitation is recorded in project state.

Target: 65 passing, 0 failing, 0 skipped.
