"""Read-only CI and coverage inspection."""
from __future__ import annotations

from typing import Any


def list_workflow_runs(repo: Any) -> list[dict[str, object]]:
    return [{"name": run.name, "status": run.status, "conclusion": run.conclusion, "head_sha": run.head_sha, "created_at": str(run.created_at), "updated_at": str(run.updated_at)} for run in repo.get_workflow_runs()]


def get_latest_ci_status(repo: Any, branch: str = "main") -> dict[str, object]:
    runs = list(repo.get_workflow_runs(branch=branch))
    if not runs:
        return {"branch": branch, "status": "unavailable"}
    run = runs[0]
    return {"branch": branch, "status": run.conclusion or run.status, "head_sha": run.head_sha}


def read_coverage_report(repo: Any) -> dict[str, object]:
    try:
        content = repo.get_contents("coverage.json")
    except Exception:
        return {"found": False, "coverage": None}
    import json
    payload = json.loads(content.decoded_content.decode("utf-8"))
    return {"found": True, "coverage": payload.get("totals", {}).get("percent_covered")}


def check_branch_protection(repo: Any, branch: str = "main") -> dict[str, object]:
    try:
        protection = repo.get_branch(branch).get_protection()
    except Exception:
        return {"branch": branch, "protected": False}
    return {"branch": branch, "protected": True, "required_status_checks": bool(getattr(protection, "required_status_checks", None)), "required_reviews": bool(getattr(protection, "required_pull_request_reviews", None))}
