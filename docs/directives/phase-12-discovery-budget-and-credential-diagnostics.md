# RFDRepoMan — Phase 12 Directive: Discovery Budget & Credential Diagnostics

*July 2026 | Read fully before executing anything.*

## Context

Measured discovery requires roughly 6.6–6.7 seconds and must not share the eight-second HTTP timeout. Live MCP credential fallback still fails despite equivalent-launch success, so this phase adds only secret-safe failure telemetry before changing credential behavior.

## Scope

| File | Action |
|---|---|
| `repoman/github_status.py` | Add a dedicated discovery timeout. |
| `repoman/config.py` | Log bounded, redacted GitHub CLI failure diagnostics. |
| `tests/test_phase12.py` | Test timeout separation and safe diagnostics. |
| `docs/directives/phase-12-discovery-budget-and-credential-diagnostics.md` | Preserve this directive. |

## Requirements

Discovery receives a 15-second timeout while retaining the global cap. Credential logs include only fixed command identity, executable resolution, return code or timeout, and redacted/truncated stderr. They never include command output or token values.
