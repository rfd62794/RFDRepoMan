"""Opt-in policy enforcement for merge operations."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from repoman.state_reader import read_state


def declared_policy(repo: str | Path) -> dict[str, object]:
    fields = read_state(repo)["fields"]
    return {key: fields[key] for key in ("require_ci_pass", "min_coverage", "protected_branches") if key in fields}


def evaluate_merge_policy(repo: str | Path, target_branch: str, ci_status: str | None, coverage: float | None) -> list[str]:
    policy = declared_policy(repo)
    failures: list[str] = []
    if policy.get("require_ci_pass") is True and ci_status != "success":
        failures.append("require_ci_pass: latest CI is not green")
    threshold = policy.get("min_coverage")
    if isinstance(threshold, float) and (coverage is None or coverage < threshold):
        failures.append(f"min_coverage: {coverage if coverage is not None else 'unavailable'} is below {threshold}")
    protected = policy.get("protected_branches", [])
    if target_branch in protected and policy.get("require_ci_pass") is True and ci_status != "success":
        failures.append(f"protected_branches: {target_branch} requires green CI")
    return failures


def authorize_merge(repo: str | Path, target_branch: str, ci_status: str | None, coverage: float | None, override_policy: bool, override_reason: str | None, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object] | None:
    failures = evaluate_merge_policy(repo, target_branch, ci_status, coverage)
    if not failures:
        return None
    if not override_policy:
        return {"refused": "policy conditions failed", "policy_failures": failures}
    if not override_reason:
        return {"refused": "override_policy=True requires override_reason", "policy_failures": failures}
    event = {"action": "policy_override", "repo": str(repo), "policy_violated": failures, "reason": override_reason}
    if audit:
        audit(event)
    return {"override": event}
