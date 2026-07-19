"""Read-only reconciliation of local state and GitHub milestones."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from repoman.github_planning import list_milestones
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
