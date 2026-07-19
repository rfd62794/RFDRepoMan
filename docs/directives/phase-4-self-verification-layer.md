# RFDRepoMan — Phase 4 Directive: Self-Verification Layer

*July 2026 | Read fully before executing anything.*

> **STOP:** Run `uv run pytest` before touching any file. Must report 30 passing, 0 failing, 0 skipped. If count differs, stop and report.

## Context

Phase 4 adds mechanical self-verification tools so repository checks can be run repeatably. The tools report raw facts; they do not judge whether a phase is complete.

Standing convention: every directive is saved in `docs/directives/` as `phase-N-short-title.md` as part of its own completion criteria.

## Scope

| File | Action |
|---|---|
| `repoman/self_verify.py` | Add `verify_floor`, `verify_git_clean`, and `verify_manual_proof`. |
| `repoman/server.py` | Register the three tools with passthrough-only wrappers. |
| `tests/test_phase4.py` | Verify real subprocess output and closed scenario handling. |
| `docs/directives/phase-4-self-verification-layer.md` | Preserve this directive. |

All Phase 1–3 files other than `repoman/server.py` are read-only.

## Requirements

### `verify_floor(repo)`

Run `uv run pytest -q` in the target repository. Return raw stdout, return code, and pytest summary counts. If output cannot be parsed, return `parsed: false` and do not estimate counts.

### `verify_git_clean(repo)`

Run `git status --short` every time. Return raw output, return code, and `clean` based only on output emptiness.

### `verify_manual_proof(repo, scenario)`

Support only `unconfirmed_push`, `unconfirmed_merge`, and `policy_override_cycle`. Call real existing actions with confirmation withheld where applicable, returning their actual results. Reject unknown scenarios.

## Test Anchors

- `test_verify_floor_returns_real_output`
- `test_verify_floor_unparseable_flagged`
- `test_verify_git_clean_detects_dirty`
- `test_verify_git_clean_detects_clean`
- `test_verify_manual_proof_scenario_enum_closed`
- `test_verify_manual_proof_calls_real_functions`

Target: 36 passing, 0 failing, 0 skipped.

## Completion Criteria

- [ ] 36 tests pass with raw output.
- [ ] `verify_git_clean` runs against this repository with raw output.
- [ ] `verify_floor` runs against this repository with raw output matching 36 tests.
- [ ] This directive exists in the repository.
- [ ] `docs/state/current.md` records Phase 4 and self-verification availability.
