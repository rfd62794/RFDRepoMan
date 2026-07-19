# RFDRepoMan — Phase 1 Directive: Repo State, Git/GitHub Executor & Policy Layer

*July 2026 | Project Maintainers | Read fully before executing anything.*

> **STOP:** This is a new repo. No existing test floor. Create the repo structure first. Report it before writing any code.

## 0. Context

RFDRepoMan is a standalone MCP server — a "dumb" tool by design. It holds no independent judgment: it reports facts and executes named, scoped actions on request. It never decides when to act; that decision belongs to the authorized operator, who confirms anything consequential. Where a project has declared its own quality bar, RepoMan mechanically enforces that project's stated policy and does not invent standards of its own.

This phase delivers:

- Full local repo discovery and status across everything under `<repo-root>`.
- Reconciliation against the `docs/state/current.md` phase/floor convention.
- GitHub account integration across operator-configured accounts, covering repos, issues, PRs, forks, branches, milestones, and Projects v2.
- Full git and GitHub action execution with one shared gate for consequential actions.
- Read-only CI status and coverage visibility.
- Per-project, opt-in policy enforcement with a separately flagged override path.

Deferred: Telegram or other communication integration; autonomous or scheduled invocation; force push; GitLab/Bitbucket support beyond stubs; enforcement beyond explicitly declared project policy; one-time GitHub Milestone backfill; and raw/generic shell execution.

## 1. Scope Statement

| File | Status | Action |
|---|---|---|
| `repoman/discover.py` | New | Scan `<repo-root>` for `.git` directories. |
| `repoman/status.py` | New | Branch, clean/dirty, fetched ahead/behind, and latest commit data. |
| `repoman/state_reader.py` | New | Read phase, certified floor, next work, and optional policy fields from `docs/state/current.md`. |
| `repoman/git_actions.py` | New | Typed local actions: fetch, fast-forward-only pull, commit, push, branch create, checkout, and merge. |
| `repoman/github_status.py` | New | Read-only GitHub repo reconciliation, PRs, forks, and remote branches. |
| `repoman/github_actions.py` | New | Named GitHub write actions. |
| `repoman/github_planning.py` | New | Milestones, Projects v2 status reads/updates, and issue-to-milestone links. |
| `repoman/phase_bridge.py` | New | Report local-state versus milestone drift without resolving it. |
| `repoman/ci_status.py` | New | Read-only workflow, coverage, and branch-protection status. |
| `repoman/policy.py` | New | Read and enforce explicit opt-in project policy; provide policy override path. |
| `repoman/gate.py` | New | Shared `CONSEQUENTIAL_ACTIONS` registry. |
| `repoman/config.py` | New | Read only the two named GitHub-token environment variables; never leak tokens. |
| `repoman/hosts/gitlab_stub.py` | New | Interface-shaped stub; every method raises `NotImplementedError`. |
| `repoman/hosts/bitbucket_stub.py` | New | Interface-shaped stub; every method raises `NotImplementedError`. |
| `docs/adr/ADR-001-no-shell-passthrough.md` | New | Lock the no-shell rule. |
| `docs/adr/ADR-002-force-push-not-exposed.md` | New | Lock structural absence of force operations. |
| `docs/adr/ADR-003-policy-opt-in-only.md` | New | Lock opt-in-only enforcement. |
| `docs/state/current.md` | New | Standard state file for RFDRepoMan. |

## 2. Implementation Requirements

### `repoman/discover.py`

Scan only. Perform no filesystem writes.

### `repoman/status.py`

Fetch only for comparison. A status check must never pull or merge under any path.

### `repoman/state_reader.py`

Parse `phase`, `certified_floor`, and `what_is_next`, plus optional `require_ci_pass` (boolean), `min_coverage` (0–100 float), and `protected_branches` (branch-name list). Missing files and missing optional fields must be explicit. Nothing is inferred or silently defaulted.

### `repoman/git_actions.py`

Every action takes typed, scoped parameters. No action accepts a raw command string. `push` and `merge` require `confirmed=True`; no code path sets it automatically. No force parameter exists in function signatures. Before a merge, consult `policy.py`.

### `repoman/github_status.py`

Iterate both configured accounts. Report visibility, stars, open issue/PR count, and default branch. Provide read-only `list_prs`, `list_forks`, and `list_remote_branches`. This module has no write-capable calls.

### `repoman/github_actions.py`

| Action | Tier | Requirement |
|---|---|---|
| `create_pr` | Gated | Requires `confirmed=True`. |
| `merge_pr` | Gated | Requires `confirmed=True`; consult policy. |
| `set_visibility` | Gated | Requires `confirmed=True`. |
| `close_pr` | Logged, ungated | Reversible. |
| `add_pr_comment` | Logged, ungated | Communication only. |
| `request_pr_review` | Logged, ungated | Communication only. |
| `create_fork` | Logged, ungated | Additive. |
| `github_create_branch` | Logged, ungated | Explicitly namespaced remote branch creation. |
| `delete_remote_branch` | Gated | Requires `confirmed=True`. |
| `create_issue` / `close_issue` | Logged, ungated | Named, scoped operations. |

No raw command input is permitted.

### `repoman/github_planning.py`

Milestone creation, closing, listing, and issue linking are logged but ungated. Projects v2 status moves are logged but ungated. Every such action must have an audit entry.

### `repoman/phase_bridge.py`

Compare local state with GitHub milestones. Report local-certified/no-matching-closed-milestone, closed-milestone/no-local-certification, and absent data on either side. Never create, close, or modify a milestone to resolve drift.

### `repoman/ci_status.py`

Provide read-only workflow-run history, latest `main` CI status, published coverage, and branch-protection status. Do not modify CI or protection.

### `repoman/policy.py`

No declared policy means no enforcement. For declared policy, local `merge` and GitHub `merge_pr` refuse when declared CI or coverage conditions fail. Override requires `override_policy=True` and a non-empty `override_reason`, separate from `confirmed=True`. Record every successful override with repository, policy violated, and reason.

### `repoman/gate.py`

The sole shared consequential-action registry is:

```python
CONSEQUENTIAL_ACTIONS = {"push", "merge", "merge_pr", "create_pr", "set_visibility", "delete_remote_branch"}
```

Both local git and GitHub action modules import this registry.

### Host Stubs

GitLab and Bitbucket stubs match the GitHub status interface shape. Every method raises `NotImplementedError`; no partial host implementation is acceptable.

### `repoman/config.py`

Read tokens exclusively from account-specific environment variables. Never hardcode, log, return, or include a token or partial token in error output.

## 3. Test Anchors

| Test name | Target | Behaviour |
|---|---|---|
| `test_discover_finds_git_repos` | `discover.py` | Return only directories containing `.git`. |
| `test_status_never_calls_pull_or_merge` | `status.py` | Invoke only fetch/read operations. |
| `test_state_reader_missing_file_explicit` | `state_reader.py` | Missing state is explicit. |
| `test_state_reader_missing_policy_fields_explicit` | `state_reader.py` | Missing policy fields are explicit. |
| `test_git_actions_reject_raw_shell_input` | `git_actions.py` | Raw command input is structurally absent. |
| `test_git_push_requires_confirmed_flag` | `git_actions.py` | Unconfirmed push refuses without mutation. |
| `test_git_merge_requires_confirmed_flag` | `git_actions.py` | Unconfirmed merge refuses without mutation. |
| `test_force_push_not_exposed` | `git_actions.py` | No force parameter path exists. |
| `test_github_status_reconciles_local_and_remote` | `github_status.py` | Correct remote-only/local-only/both flags. |
| `test_github_status_is_read_only` | `github_status.py` | No write-capable call. |
| `test_github_write_actions_require_confirmed` | `github_actions.py` | Gated writes refuse unconfirmed calls. |
| `test_github_low_consequence_actions_logged_not_gated` | `github_actions.py` | Logged ungated actions run and audit. |
| `test_gate_registry_shared_by_both_domains` | `gate.py` | Both action domains import the same set. |
| `test_token_never_in_output` | `config.py` | Token values never appear in output. |
| `test_stubs_raise_not_implemented` | `hosts/*_stub.py` | Every stub method raises. |
| `test_planning_actions_logged_ungated` | `github_planning.py` | Planning writes audit without confirmation. |
| `test_phase_bridge_reports_drift_only` | `phase_bridge.py` | Drift reports without milestone mutation. |
| `test_ci_status_read_only` | `ci_status.py` | No write-capable call. |
| `test_policy_no_declaration_no_enforcement` | `policy.py` | Absent policy causes no gate. |
| `test_policy_blocks_on_ci_fail` | `policy.py` | Declared CI policy blocks red CI. |
| `test_policy_blocks_below_min_coverage` | `policy.py` | Declared coverage floor blocks lower coverage. |
| `test_override_requires_separate_flag_and_reason` | `policy.py` | Confirmation alone cannot bypass; a reason is required. |
| `test_override_logged` | `policy.py` | Successful override records policy and reason. |

Target: 22 passing, 0 failing, 0 skipped. Mock real git and GitHub calls in tests.

## 4. Completion Criteria

- [ ] Structure is created and reported before implementation.
- [ ] 22 anchored tests pass with raw pytest output.
- [ ] ADR-001, ADR-002, and ADR-003 exist and are locked.
- [ ] A real `repoman_fetch` plus status check has raw output.
- [ ] GitHub reconciliation against both accounts has raw output.
- [ ] Unconfirmed `repoman_push` and `github_create_pr` both refuse with raw output.
- [ ] A declared-policy red-CI merge refuses without override and succeeds with explicit override/reason, with raw output.
- [ ] `docs/state/current.md` is updated as the final step.

## 5. Quick Reference

| Fact | Value |
|---|---|
| Local scope | Everything under `<repo-root>` |
| GitHub accounts | Operator-configured accounts |
| Interface | MCP only |
| Judgment location | Authorized operators, never RepoMan |
| Gated | `push`, `merge`, `merge_pr`, `create_pr`, `set_visibility`, `delete_remote_branch` |
| Logged, ungated | PR comments/reviews/closure, forks, remote branch creation, issues, milestones, and Projects status actions |
| Policy | Per-project opt-in through `current.md`; silence means report-only |
| Policy override | Separate `override_policy=True` with mandatory `override_reason` |
| Never exposed | Force push and raw shell passthrough |
| Stubbed only | GitLab and Bitbucket |

*Project Maintainers | RFDRepoMan Phase 1 | Spec first. Test floor always real. No judgment in the tool — only in authorized operators.*
