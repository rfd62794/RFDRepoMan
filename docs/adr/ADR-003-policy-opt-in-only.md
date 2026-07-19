# ADR-003: Policy Is Opt-In Only

- **Status:** Accepted
- **Date:** 2026-07-19
- **Decision owners:** RFD IT Services Ltd.

## Context

RFD projects have different quality requirements and maturity levels. A global policy chosen by RFDRepoMan would turn a reporting and execution service into a source of independent judgment. The service must enforce a project's declared standard without inventing a standard for projects that have not declared one.

## Decision

Policy enforcement is opt-in per repository through explicit fields in `docs/state/current.md`:

- `require_ci_pass`
- `min_coverage`
- `protected_branches`

If a state file or optional policy field is absent, RepoMan reports that absence and applies no policy gate. It does not infer values or silently choose global defaults.

For a declared policy, local `merge` and GitHub `merge_pr` evaluate the relevant conditions before mutation. `confirmed=True` only authorizes the consequential action; it does not bypass policy. A policy exception requires both `override_policy=True` and a non-empty `override_reason`. Every successful override is recorded with the repository, violated condition, and stated reason.

## Consequences

- Projects control whether and how RepoMan enforces CI, coverage, and branch protections.
- No policy declaration produces report-only behavior identical to any other undeclared repository.
- Overrides remain distinguishable from ordinary action confirmations in logs and returned results.
- RepoMan cannot silently lower a declared project standard.

## Compliance

Review merge paths to ensure they use `repoman/policy.py` before mutation. Do not introduce global policy defaults or combine `confirmed` and `override_policy` into one flag. Any change that imposes policy absent an explicit project declaration requires a superseding ADR.
