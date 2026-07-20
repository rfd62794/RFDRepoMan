# ADR-004: GitHub CLI Credential Fallback Is Explicit Opt-In

- **Status:** Accepted
- **Date:** 2026-07-19
- **Decision owners:** Project Maintainers

## Context

RepoMan's environment-token configuration makes credential use explicit and supports the least privilege required by its named operations. GitHub CLI credentials can be more convenient but may carry broader scopes, including repository and workflow access. The CLI also exposes only its active account to `gh auth token`.

## Decision

RepoMan checks an account-specific environment token first. It may use the active GitHub CLI credential only when `RFD_REPOMAN_ALLOW_GH_FALLBACK=true` is explicitly set, the requested account matches the CLI's active account, and no environment token is available.

Every successful fallback is logged with the requested account and a warning that the credential may exceed RepoMan's minimum declared scope. Token values are never logged. A mismatch between the requested and active account returns no token; RepoMan never silently uses a different account's credential.

GitHub CLI calls use fixed argument lists only. No caller-controlled command or argument may be passed to the subprocess.

## Consequences

- Operators can deliberately use existing GitHub CLI credentials during onboarding or local work.
- Environment credentials remain preferred and visible configuration.
- Multi-account use requires the correct CLI account to be active or an environment token to be set.
- Fallback use remains auditable rather than becoming ambient default behavior.
