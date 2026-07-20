"""Read-only reconciliation of local state and GitHub milestones."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from repoman.config import resolve_token
from repoman.github_planning import list_milestones
from repoman.github_status import NETWORK_TIMEOUT_SECONDS, _github_client, _within_timeout
from repoman.state_reader import read_state


def reconcile_phase(repo_path: str | Path, github_repo: Any) -> dict[str, object]:
    state = read_state(repo_path)
    milestones = list_milestones(github_repo)
    if not state["found"]:
        return {"drift": ["no local state data"], "state": state, "milestones": milestones}
    phase = state["fields"].get("phase")
    certified = state["fields"].get("certified_floor")
    match = next((item for item in milestones if item["title"] == phase), None)
    drift: list[str] = []
    if not match:
        drift.append("no matching milestone")
    elif certified and match["state"] != "closed":
        drift.append("local says certified but milestone is not closed")
    elif not certified and match["state"] == "closed":
        drift.append("milestone closed but no local certification")
    return {"drift": drift, "state": state, "milestone": match, "milestones": milestones}


def phase_bridge_check_by_name(repo_path: str | Path, github_repo_name: str, account_name: str) -> dict[str, object]:
    token, _ = resolve_token(account_name)
    if not token:
        return {"error": "no_credential_available", "account": account_name}
    completed, result = _within_timeout(lambda: reconcile_phase(repo_path, _github_client(token).get_repo(github_repo_name)), NETWORK_TIMEOUT_SECONDS)
    if not completed:
        return {"error": "timeout" if isinstance(result, TimeoutError) else "phase_bridge_failed", "account": account_name, "message": str(result)}
    return result
