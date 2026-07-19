"""Shared confirmation gate for consequential operations."""
from __future__ import annotations

CONSEQUENTIAL_ACTIONS = frozenset({"push", "merge", "merge_pr", "create_pr", "set_visibility", "delete_remote_branch"})


def require_confirmation(action: str, confirmed: bool) -> dict[str, str] | None:
    if action not in CONSEQUENTIAL_ACTIONS:
        raise ValueError("Unknown consequential action")
    if not confirmed:
        return {"refused": f"{action} requires confirmed=True"}
    return None
