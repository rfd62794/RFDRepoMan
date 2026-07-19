"""GitHub milestones and Projects v2 mutations with auditing."""
from __future__ import annotations

from typing import Any, Callable


def _log(audit: Callable[[dict[str, object]], None] | None, action: str, repo: Any, **details: object) -> None:
    if audit:
        audit({"action": action, "repo": getattr(repo, "full_name", str(repo)), **details})


def list_milestones(repo: Any, state: str = "all") -> list[dict[str, object]]:
    return [{"number": item.number, "title": item.title, "state": item.state, "description": item.description} for item in repo.get_milestones(state=state)]


def github_create_milestone(repo: Any, title: str, description: str = "", audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    item = repo.create_milestone(title=title, description=description)
    _log(audit, "github_create_milestone", repo, number=item.number)
    return {"action": "github_create_milestone", "number": item.number}


def github_close_milestone(repo: Any, number: int, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    repo.get_milestone(number).edit(state="closed")
    _log(audit, "github_close_milestone", repo, number=number)
    return {"action": "github_close_milestone", "number": number}


def github_link_issue_to_milestone(repo: Any, issue_number: int, milestone_number: int, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    repo.get_issue(issue_number).edit(milestone=milestone_number)
    _log(audit, "github_link_issue_to_milestone", repo, issue=issue_number, milestone=milestone_number)
    return {"action": "github_link_issue_to_milestone", "issue": issue_number, "milestone": milestone_number}


def github_update_project_status(project: Any, item_id: str, status_field_id: str, status_option_id: str, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    project.update_item_field_value(item_id=item_id, field_id=status_field_id, value=status_option_id)
    _log(audit, "github_update_project_status", project, item_id=item_id, status=status_option_id)
    return {"action": "github_update_project_status", "item_id": item_id, "status": status_option_id}
