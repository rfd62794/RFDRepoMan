# ADR-002: Force Push Is Not Exposed

- **Status:** Accepted
- **Date:** 2026-07-19
- **Decision owners:** RFD IT Services Ltd.

## Context

A force push can rewrite remote history, discard references to unmerged work, and disrupt collaborators. A confirmation gate protects against accidental invocation of supported consequential actions, but it is not a sufficient control for an operation that can erase history.

## Decision

RFDRepoMan exposes no force-push, force-update, lease-force, or equivalent history-rewriting capability.

No force-related parameter may appear in the signature of a local git action, GitHub action, MCP tool, configuration option, or environment variable. `confirmed=True` cannot enable force behavior. The absence is structural, not a runtime condition.

## Consequences

- Callers cannot convert a normal push into a force push through an undocumented option or raw command path.
- Tests inspect action signatures to preserve this boundary.
- Push and branch operations remain constrained to their documented non-force behavior.
- A caller needing history rewriting must use a separate process outside RFDRepoMan's Phase 1 surface.

## Compliance

Review all action signatures and MCP tool schemas for force-related parameters and aliases. A future force operation requires a superseding ADR that defines scope, recovery expectations, confirmation design, audit requirements, and test anchors. It may not be added as a flag, configuration toggle, or hidden default.
