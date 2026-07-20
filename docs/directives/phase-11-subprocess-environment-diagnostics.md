# RFDRepoMan — Phase 11 Directive: Subprocess Environment Diagnostics

*July 2026 | Read fully before executing anything.*

## Context

Live Claude Desktop MCP calls differ from direct terminal behavior for GitHub CLI fallback and repository discovery. This phase observes the configured stdio-equivalent launch and normal terminal launch without changing production behavior.

## Scope

| File | Action |
|---|---|
| `scripts/diagnose_subprocess_env.py` | Add an observation-only diagnostic script. |
| `docs/DIAGNOSTIC_FINDINGS.md` | Record raw outputs and factual comparison. |
| `docs/directives/phase-11-subprocess-environment-diagnostics.md` | Preserve this directive. |

No production module is modified.

## Limitation

The configured stdio-equivalent launch uses the same `uv --directory` command and explicit MCP environment values, but cannot introspect the already-running Claude Desktop stdio process. Findings must retain that distinction.
