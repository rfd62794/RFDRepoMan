# RFDRepoMan — Phase 7 Directive: Optional `gh` CLI Credential Fallback

*July 2026 | Read fully before executing anything.*

## Context

Environment-variable tokens remain the default credential source. This phase adds an explicit, logged fallback to the active GitHub CLI credential only when `RFD_REPOMAN_ALLOW_GH_FALLBACK=true` is set and the CLI active account matches the requested account.

## Scope

| File | Action |
|---|---|
| `repoman/config.py` | Add opt-in credential resolution. |
| `docs/adr/ADR-004-gh-fallback-explicit-opt-in.md` | Record the credential-scope tradeoff. |
| `tests/test_phase7.py` | Test precedence, opt-in, account matching, logging, and fixed subprocess arguments. |
| `docs/directives/phase-7-gh-cli-credential-fallback.md` | Preserve this directive. |

All action, gate, policy, and server modules remain read-only.

## Requirements

`resolve_token(account_name)` returns `(token, source)`. Environment values always win. Without an explicit fallback flag, no GitHub CLI command is executed. The fallback verifies the active GitHub CLI account before retrieving its token; an account mismatch returns `gh_account_mismatch`. Every successful fallback logs the account and elevated-scope warning without logging the token.

GitHub CLI subprocess calls use fixed argument lists only.

## Test Anchors

- `test_env_var_preferred_over_fallback`
- `test_fallback_disabled_by_default`
- `test_fallback_used_when_explicitly_enabled`
- `test_fallback_rejects_account_mismatch`
- `test_fallback_use_is_logged`
- `test_gh_invoked_with_fixed_args_only`

Target: 51 passing, 0 failing, 0 skipped.
