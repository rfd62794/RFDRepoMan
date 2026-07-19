# RFDRepoMan — Phase 2 Directive: Public Release Hardening

*July 2026 | RFD IT Services Ltd.*

> **STOP:** Run pytest before touching any file. Must report 22 passing, 0 failing, 0 skipped (Phase 1 floor). If count differs, stop and report.
>
> Additionally: confirm all four Phase 1 manual-verification items (real-repo status, confirmed=True refusal, policy override, GitHub reconciliation status) are either complete with raw proof or explicitly logged as open before proceeding — Phase 2 does not paper over an unclosed Phase 1.

## Context

Phase 1 delivered a private, working tool. Phase 2 makes it safe to hand to a stranger, without adding capability — this phase touches configuration, documentation, and repo hygiene, not the action/gate/policy logic itself, which is locked by ADR-001 through ADR-003 and stays untouched.

Phase 2 delivers account-agnostic configuration, path-agnostic local scanning, a documented threat model, license selection, and pre-publish secret hygiene.

Out of scope: changes to gating, policy, or action logic; new git or GitHub capability; and Telegram or other communication layers.

## Scope Statement

| File | Status | Action |
|---|---|---|
| `repoman/config.py` | Modify | Replace hardcoded account-token names with `RFD_REPOMAN_ACCOUNTS` plus `RFD_REPOMAN_GH_TOKEN_{NAME}` per supplied account. |
| `repoman/discover.py` | Modify | Local repo root becomes required `RFD_REPOMAN_ROOT`; remove machine-specific defaults. |
| `.env.example` | New | Placeholder values only; document every required environment variable. |
| `.gitignore` | Modify | Confirm `.env` and local configuration are excluded. |
| `SECURITY.md` | New | Threat model covering push, merge, and branch deletion capability, and the limits of confirmation gates. |
| `LICENSE` | New | MIT, after confirming the license choice remains appropriate. |
| `docs/SECRETS_SCAN.md` | New | Full-history secret scan record with actual command output. |

Read-only: `repoman/gate.py`, `repoman/policy.py`, `repoman/git_actions.py`, `repoman/github_actions.py`, `repoman/github_planning.py`, `repoman/phase_bridge.py`, `repoman/ci_status.py`, and `repoman/hosts/*`. Do not modify them.

## Implementation Constraints

### `repoman/config.py`

No account name, organization name, or username appears anywhere in source. Account identity comes only from `RFD_REPOMAN_ACCOUNTS` at runtime.

### `repoman/discover.py`

No path resembling `C:\\Github\\` or another personal-directory convention remains in source, tests, or example configuration.

### Secret Scan

Run the scan against full commit history, not only the current tree. Record raw tool output before a visibility change.

## Test Anchors

| Test name | Target file | Behaviour |
|---|---|---|
| `test_config_no_hardcoded_account_names` | `config.py` | Static scan finds no known personal account strings. |
| `test_discover_requires_root_env_var` | `discover.py` | Missing `RFD_REPOMAN_ROOT` produces an explicit error without a default path. |
| `test_env_example_documents_all_required_vars` | `.env.example` | Every variable referenced in `config.py` has a placeholder entry. |

Target: 3 new, 25 total passing, 0 failing, 0 skipped.

## Completion Criteria

- [ ] Phase 1 floor remains 22/0/0 or higher before Phase 2 changes.
- [ ] All 3 new test anchors pass with raw pytest output.
- [ ] `SECURITY.md`, `LICENSE`, `.env.example`, and `docs/SECRETS_SCAN.md` contain substantive content.
- [ ] Full-history secret scan is run and raw output recorded in `docs/SECRETS_SCAN.md`.
- [ ] Fresh-clone verification uses test `RFD_REPOMAN_ACCOUNTS` and `RFD_REPOMAN_ROOT` values without references to actual accounts or paths.
- [ ] `docs/state/current.md` is updated with phase, floor, and visibility status.
