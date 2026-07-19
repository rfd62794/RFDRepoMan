# ADR-001: No Shell Passthrough

- **Status:** Accepted
- **Date:** 2026-07-19
- **Decision owners:** RFD IT Services Ltd.

## Context

RFDRepoMan is an MCP server for reporting repository state and executing an intentionally small set of named git and GitHub operations. A generic command runner would allow callers to bypass typed parameters, action confirmation, policy checks, audit logging, and host-specific capability boundaries.

## Decision

RFDRepoMan will never expose a generic shell, command, script, subprocess, or arbitrary argument passthrough tool.

Every executable capability must be represented by a named function with typed, scoped parameters. Local git operations belong in `repoman/git_actions.py`; GitHub operations belong in their explicitly separated modules. Each new operation must declare its confirmation tier and, where applicable, use the shared gate and policy layers.

No function may accept a raw command string. No tool may concatenate caller-controlled text into an executable command. No MCP resource, prompt, or alternate transport may provide an equivalent escape hatch.

## Consequences

- New actions require a deliberate API addition rather than caller-supplied shell syntax.
- Tests can verify each operation's action, parameter shape, confirmation requirement, and policy interaction.
- RFDRepoMan remains a bounded executor rather than a general remote-code-execution surface.
- Operations that are not explicitly implemented remain unavailable.

## Compliance

Review changes for raw command parameters, generic subprocess wrappers, and tool names that imply arbitrary execution. Any proposal to add a generic execution surface requires a superseding ADR; it cannot be enabled by configuration, environment variable, feature flag, or confirmation argument.
