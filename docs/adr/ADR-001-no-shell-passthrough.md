# ADR-001: No Shell Passthrough

## Status
Accepted

## Decision
RFDRepoMan exposes only typed, named, scoped operations. It will never expose a generic shell command tool for local git, GitHub, or any future host integration.

## Consequences
Every new operation must have an explicit function signature and test coverage. Arbitrary command execution is outside this service's authority.
