# RFDRepoMan — Phase 3 Directive: Full MCP Tool Surface Registration

*July 2026 | Read fully before executing anything.*

> **STOP:** Run `uv run pytest` before touching any file. Must report 25 passing, 0 failing, 0 skipped. If count differs, stop and report.

## Context

Phases 1 and 2 built and tested the git, GitHub, planning, CI-visibility, and policy surface, but `repoman/server.py` registers only three MCP tools. Phase 3 exposes every already-tested function with registration-only wrappers. It adds no action logic and does not change action tiers.

Deferred: new capabilities, changes to gating or logging tiers, and live credential configuration.

## Scope

| File | Action |
|---|---|
| `repoman/server.py` | Register all remaining tested functions. |
| `tests/test_phase3.py` | Verify registration completeness, passthrough signatures, dead-import regression, personal-identifier absence, and server tool count. |

Read-only: `repoman/gate.py`, `repoman/policy.py`, `repoman/git_actions.py`, `repoman/github_actions.py`, `repoman/github_planning.py`, `repoman/phase_bridge.py`, `repoman/ci_status.py`, `repoman/github_status.py`, `repoman/config.py`, `repoman/discover.py`, `repoman/state_reader.py`, `repoman/status.py`, and `repoman/hosts/*`.

## Registration Requirements

Each wrapper must pass its parameters to the tested function unchanged, preserving defaults and behavior.

- Local git: `repoman_merge`, `repoman_create_branch`, `repoman_checkout`, `repoman_pull`, `repoman_commit`
- GitHub actions: `github_create_pr`, `github_merge_pr`, `github_close_pr`, `github_add_pr_comment`, `github_request_pr_review`, `github_create_fork`, `github_create_branch`, `github_delete_remote_branch`, `github_set_visibility`, `github_create_issue`, `github_close_issue`
- GitHub reads: `github_list_prs`, `github_list_forks`, `github_list_remote_branches`, `github_reconcile_status`
- Planning: `github_create_milestone`, `github_close_milestone`, `github_link_issue_to_milestone`, `github_update_project_status`, `phase_bridge_check`
- CI: `ci_list_workflow_runs`, `ci_get_latest_status`, `ci_read_coverage`, `ci_check_branch_protection`
- State: `state_read`

Tool names must retain `git_`, `github_`, `ci_`, `state_`, or `repoman_` namespaces. The existing `create_pr` import must be registered as `github_create_pr`.

Replace Phase 2's account test with a literal scan for the two legacy account identifiers across `repoman/*.py` and `scripts/*.py`.

## Test Anchors

| Test | Behaviour |
|---|---|
| `test_all_tested_functions_registered` | Every listed tested function has a tool. |
| `test_tool_wrappers_pass_through_unchanged` | Wrapper signatures match selected underlying functions. |
| `test_create_pr_actually_registered` | `github_create_pr` is registered. |
| `test_no_personal_identifiers_in_source` | Legacy account identifiers do not occur under source or scripts. |
| `test_server_starts_with_full_tool_list` | Registered count matches the full expected list. |

Target: 30 passing, 0 failing, 0 skipped.

## Completion Criteria

- [ ] All 30 tests pass with raw pytest output.
- [ ] The server starts and prints the complete tool list with raw output.
- [ ] An unconfirmed live `repoman_merge` call against a scratch repository refuses with raw output.
- [ ] `docs/state/current.md` records the full MCP tool surface.
