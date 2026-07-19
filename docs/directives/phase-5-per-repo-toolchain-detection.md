# RFDRepoMan — Phase 5 Directive: Per-Repo Toolchain Detection

*July 2026 | Read fully before executing anything.*

> **STOP:** Confirm the floor in `docs/state/current.md` and run `uv run pytest` before touching any file.

## Context

`verify_floor` initially assumed `uv run pytest` for every repository. Repository toolchains are not uniform. Phase 5 adds file-based detection so verification reports unsupported or ambiguous repositories explicitly rather than guessing.

Deferred: execution of non-Python test suites such as `cargo test` and `npm test`.

## Scope

| File | Action |
|---|---|
| `repoman/toolchain.py` | Add file-based `detect_toolchain(repo)`. |
| `repoman/self_verify.py` | Restrict `verify_floor` execution to detected uv repositories. |
| `tests/test_phase5.py` | Add detection and unsupported-toolchain tests. |
| `docs/directives/phase-5-per-repo-toolchain-detection.md` | Preserve this directive. |

All other action, policy, and gate modules remain read-only.

## Requirements

`detect_toolchain` performs no execution and uses only files present in the supplied repository. It recognizes `Cargo.toml`, `pyproject.toml` with `uv.lock`, `pyproject.toml` alone, `requirements.txt`, `package.json`, and optional `.python-version` metadata.

`verify_floor` runs `uv run pytest -q` only where detection reports `uv`. Every other toolchain returns an explicit `unsupported_toolchain` result without executing a test command. Ambiguous Python repositories are never guessed as pip or uv.

## Test Anchors

- `test_detect_rust_toolchain`
- `test_detect_uv_toolchain`
- `test_detect_ambiguous_python`
- `test_detect_node_toolchain`
- `test_detect_no_toolchain`
- `test_verify_floor_skips_non_uv_explicitly`

Target: 42 passing, 0 failing, 0 skipped.

## Completion Criteria

- [ ] 42 tests pass with raw output.
- [ ] Detection runs against real repositories of at least three detected kinds.
- [ ] This directive exists in the repository.
- [ ] `docs/state/current.md` is updated.
