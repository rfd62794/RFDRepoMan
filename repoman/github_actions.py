"""Scoped GitHub write actions."""
from __future__ import annotations

from typing import Any, Callable

from repoman.gate import CONSEQUENTIAL_ACTIONS, require_confirmation
from repoman.policy import authorize_merge


def _log(audit: Callable[[dict[str, object]], None] | None, action: str, repo: Any, **details: object) -> None:
    if audit:
        audit({"action": action, "repo": getattr(repo, "full_name", str(repo)), **details})


def create_pr(repo: Any, title: str, body: str, head: str, base: str, confirmed: bool = False) -> dict[str, object]:
    refusal = require_confirmation("create_pr", confirmed)
    if refusal:
        return refusal
    pr = repo.create_pull(title=title, body=body, head=head, base=base)
    return {"action": "create_pr", "number": pr.number}


def merge_pr(repo: Any, number: int, target_branch: str = "main", confirmed: bool = False, override_policy: bool = False, override_reason: str | None = None, ci_status: str | None = None, coverage: float | None = None, local_repo: str | None = None, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    refusal = require_confirmation("merge_pr", confirmed)
    if refusal:
        return refusal
    policy_result = authorize_merge(local_repo or ".", target_branch, ci_status, coverage, override_policy, override_reason, audit)
    if policy_result and "refused" in policy_result:
        return policy_result
    result = repo.get_pull(number).merge()
    return {"action": "merge_pr", "merged": bool(result.merged), "policy": policy_result}


def set_visibility(repo: Any, private: bool, confirmed: bool = False) -> dict[str, object]:
    refusal = require_confirmation("set_visibility", confirmed)
    if refusal:
        return refusal
    repo.edit(private=private)
    return {"action": "set_visibility", "private": private}


def close_pr(repo: Any, number: int, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    repo.get_pull(number).edit(state="closed")
    _log(audit, "close_pr", repo, number=number)
    return {"action": "close_pr", "number": number}


def add_pr_comment(repo: Any, number: int, body: str, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    repo.get_issue(number).create_comment(body)
    _log(audit, "add_pr_comment", repo, number=number)
    return {"action": "add_pr_comment", "number": number}


def request_pr_review(repo: Any, number: int, reviewers: list[str], audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    repo.get_pull(number).create_review_request(reviewers=reviewers)
    _log(audit, "request_pr_review", repo, number=number)
    return {"action": "request_pr_review", "number": number}


def create_fork(repo: Any, organization: str | None = None, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    fork = repo.create_fork(organization=organization)
    _log(audit, "create_fork", repo)
    return {"action": "create_fork", "full_name": fork.full_name}


def github_create_branch(repo: Any, branch: str, source_sha: str, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source_sha)
    _log(audit, "github_create_branch", repo, branch=branch)
    return {"action": "github_create_branch", "branch": branch}


def delete_remote_branch(repo: Any, branch: str, confirmed: bool = False) -> dict[str, object]:
    refusal = require_confirmation("delete_remote_branch", confirmed)
    if refusal:
        return refusal
    repo.get_git_ref(f"heads/{branch}").delete()
    return {"action": "delete_remote_branch", "branch": branch}


def create_issue(repo: Any, title: str, body: str = "", audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    issue = repo.create_issue(title=title, body=body)
    _log(audit, "create_issue", repo, number=issue.number)
    return {"action": "create_issue", "number": issue.number}


def close_issue(repo: Any, number: int, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    repo.get_issue(number).edit(state="closed")
    _log(audit, "close_issue", repo, number=number)
    return {"action": "close_issue", "number": number}
