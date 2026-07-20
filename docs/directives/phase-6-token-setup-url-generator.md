# RFDRepoMan — Phase 6 Directive: Token Setup URL Generator

*July 2026 | Read fully before executing anything.*

## Context

This phase provides a pure onboarding utility that generates a GitHub fine-grained personal-access-token creation URL prefilled with RepoMan's required permissions. It makes no network calls, changes no state, and requires no confirmation.

## Scope

| File | Action |
|---|---|
| `repoman/token_setup.py` | Add `generate_token_url(account_name, token_name="RFDRepoMan")`. |
| `repoman/server.py` | Register `generate_token_setup_url`. |
| `tests/test_phase6.py` | Test URL base, parameters, and query validity. |
| `docs/directives/phase-6-token-setup-url-generator.md` | Preserve this directive. |
| `docs/TOKEN_SETUP.md` | Document use and permissions. |

All other files remain read-only except the Phase state record.

## Requirements

Default permissions are constants: `contents=write`, `pull_requests=write`, and `metadata=read`. `account_name` is required; permissions are not caller-configurable. The utility only returns a URL.

## Completion Criteria

- [ ] 45 tests pass with raw output.
- [ ] A generated URL is manually opened and confirmed to prefill the expected GitHub token form.
- [ ] `docs/TOKEN_SETUP.md` and this directive exist.
- [ ] `docs/state/current.md` is updated.
