# RFDRepoMan — Phase 8 Directive: MCP-Safe Client Construction

*July 2026 | Read fully before executing anything.*

## Context

MCP tools must not expose authenticated client objects as inputs. Phase 8 replaces the raw-client MCP boundary for reconciliation and phase-bridge checks with primitive-only wrappers that resolve configured credentials internally.

## Scope

| File | Action |
|---|---|
| `repoman/github_status.py` | Add bounded, per-account reconciliation client construction. |
| `repoman/phase_bridge.py` | Add bounded, named-repository phase bridge client construction. |
| `repoman/server.py` | Repoint the two MCP tools to safe wrappers. |
| `tests/test_phase8.py` | Test primitive signatures, explicit failures, isolation, timeout, and server binding. |
| `docs/directives/phase-8-mcp-safe-client-construction.md` | Preserve this directive. |

`repoman/config.py`, action modules, gates, and policies remain read-only.

## Requirements

Wrappers accept only account names, repository names, booleans, and paths. They resolve account tokens through `resolve_token`, create clients with explicit timeouts, isolate per-account failures, and return explicit credential or timeout errors. Raw functions remain available for internal callers.

## Test Anchors

- `test_reconcile_no_client_object_param`
- `test_reconcile_returns_explicit_error_no_credential`
- `test_reconcile_isolates_per_account_failure`
- `test_reconcile_has_explicit_timeout`
- `test_phase_bridge_by_name_no_object_param`
- `test_server_exposes_safe_wrappers_not_raw`

Target: 57 passing, 0 failing, 0 skipped.
