"""MCP server exposing only named, scoped RepoMan tools."""
from __future__ import annotations

from fastmcp import FastMCP

from pathlib import Path
from typing import Any

from repoman.ci_status import check_branch_protection, get_latest_ci_status, list_workflow_runs, read_coverage_report
from repoman.git_actions import checkout, commit, create_branch, fetch, merge, pull, push
from repoman.github_actions import add_pr_comment, close_issue, close_pr, create_fork, create_issue, create_pr, delete_remote_branch, github_create_branch, merge_pr, request_pr_review, set_visibility
from repoman.github_planning import github_close_milestone, github_create_milestone, github_link_issue_to_milestone, github_update_project_status
from repoman.github_status import github_status, list_forks, list_prs, list_remote_branches
from repoman.phase_bridge import reconcile_phase
from repoman.state_reader import read_state
from repoman.status import repo_status
from repoman.self_verify import verify_floor, verify_git_clean, verify_manual_proof

mcp = FastMCP("RFDRepoMan")

@mcp.tool(name="repoman_fetch")
def repoman_fetch(repo: str | Path, remote: str = "origin") -> dict[str, str]:
    return fetch(repo, remote)

@mcp.tool(name="repoman_status")
def repoman_status(repo: str | Path, remote: str = "origin") -> dict[str, object]:
    return repo_status(repo, remote)

@mcp.tool(name="repoman_push")
def repoman_push(repo: str | Path, remote: str = "origin", branch: str = "main", confirmed: bool = False) -> dict[str, str]:
    return push(repo, remote, branch, confirmed)

@mcp.tool(name="repoman_pull")
def repoman_pull(repo: str | Path, remote: str = "origin", branch: str = "main") -> dict[str, str]:
    return pull(repo, remote, branch)

@mcp.tool(name="repoman_commit")
def repoman_commit(repo: str | Path, message: str) -> dict[str, str]:
    return commit(repo, message)

@mcp.tool(name="repoman_create_branch")
def repoman_create_branch(repo: str | Path, branch: str, start_point: str = "HEAD") -> dict[str, str]:
    return create_branch(repo, branch, start_point)

@mcp.tool(name="repoman_checkout")
def repoman_checkout(repo: str | Path, branch: str) -> dict[str, str]:
    return checkout(repo, branch)

@mcp.tool(name="repoman_merge")
def repoman_merge(repo: str | Path, branch: str, target_branch: str = "main", confirmed: bool = False, override_policy: bool = False, override_reason: str | None = None, ci_status: str | None = None, coverage: float | None = None, audit: Any = None) -> dict[str, object]:
    return merge(repo, branch, target_branch, confirmed, override_policy, override_reason, ci_status, coverage, audit)

@mcp.tool(name="github_create_pr")
def github_create_pr(repo: Any, title: str, body: str, head: str, base: str, confirmed: bool = False) -> dict[str, object]:
    return create_pr(repo, title, body, head, base, confirmed)

@mcp.tool(name="github_merge_pr")
def github_merge_pr(repo: Any, number: int, target_branch: str = "main", confirmed: bool = False, override_policy: bool = False, override_reason: str | None = None, ci_status: str | None = None, coverage: float | None = None, local_repo: str | None = None, audit: Any = None) -> dict[str, object]:
    return merge_pr(repo, number, target_branch, confirmed, override_policy, override_reason, ci_status, coverage, local_repo, audit)

@mcp.tool(name="github_close_pr")
def github_close_pr(repo: Any, number: int, audit: Any = None) -> dict[str, object]:
    return close_pr(repo, number, audit)

@mcp.tool(name="github_add_pr_comment")
def github_add_pr_comment(repo: Any, number: int, body: str, audit: Any = None) -> dict[str, object]:
    return add_pr_comment(repo, number, body, audit)

@mcp.tool(name="github_request_pr_review")
def github_request_pr_review(repo: Any, number: int, reviewers: list[str], audit: Any = None) -> dict[str, object]:
    return request_pr_review(repo, number, reviewers, audit)

@mcp.tool(name="github_create_fork")
def github_create_fork(repo: Any, organization: str | None = None, audit: Any = None) -> dict[str, object]:
    return create_fork(repo, organization, audit)

@mcp.tool(name="github_create_branch")
def github_create_branch_tool(repo: Any, branch: str, source_sha: str, audit: Any = None) -> dict[str, object]:
    return github_create_branch(repo, branch, source_sha, audit)

@mcp.tool(name="github_delete_remote_branch")
def github_delete_remote_branch(repo: Any, branch: str, confirmed: bool = False) -> dict[str, object]:
    return delete_remote_branch(repo, branch, confirmed)

@mcp.tool(name="github_set_visibility")
def github_set_visibility(repo: Any, private: bool, confirmed: bool = False) -> dict[str, object]:
    return set_visibility(repo, private, confirmed)

@mcp.tool(name="github_create_issue")
def github_create_issue(repo: Any, title: str, body: str = "", audit: Any = None) -> dict[str, object]:
    return create_issue(repo, title, body, audit)

@mcp.tool(name="github_close_issue")
def github_close_issue(repo: Any, number: int, audit: Any = None) -> dict[str, object]:
    return close_issue(repo, number, audit)

@mcp.tool(name="github_list_prs")
def github_list_prs(repo: Any, state: str = "open") -> list[dict[str, Any]]:
    return list_prs(repo, state)

@mcp.tool(name="github_list_forks")
def github_list_forks(repo: Any) -> list[dict[str, str]]:
    return list_forks(repo)

@mcp.tool(name="github_list_remote_branches")
def github_list_remote_branches(repo: Any) -> list[str]:
    return list_remote_branches(repo)

@mcp.tool(name="github_reconcile_status")
def github_reconcile_status(clients: dict[str, Any], root: str | None = None, include_pr_counts: bool = True, progress: Any = None) -> dict[str, Any]:
    return github_status(clients, root, include_pr_counts, progress)

@mcp.tool(name="github_create_milestone")
def github_create_milestone_tool(repo: Any, title: str, description: str = "", audit: Any = None) -> dict[str, object]:
    return github_create_milestone(repo, title, description, audit)

@mcp.tool(name="github_close_milestone")
def github_close_milestone_tool(repo: Any, number: int, audit: Any = None) -> dict[str, object]:
    return github_close_milestone(repo, number, audit)

@mcp.tool(name="github_link_issue_to_milestone")
def github_link_issue_to_milestone_tool(repo: Any, issue_number: int, milestone_number: int, audit: Any = None) -> dict[str, object]:
    return github_link_issue_to_milestone(repo, issue_number, milestone_number, audit)

@mcp.tool(name="github_update_project_status")
def github_update_project_status_tool(project: Any, item_id: str, status_field_id: str, status_option_id: str, audit: Any = None) -> dict[str, object]:
    return github_update_project_status(project, item_id, status_field_id, status_option_id, audit)

@mcp.tool(name="phase_bridge_check")
def phase_bridge_check(repo_path: str | Path, github_repo: Any) -> dict[str, object]:
    return reconcile_phase(repo_path, github_repo)

@mcp.tool(name="ci_list_workflow_runs")
def ci_list_workflow_runs(repo: Any) -> list[dict[str, object]]:
    return list_workflow_runs(repo)

@mcp.tool(name="ci_get_latest_status")
def ci_get_latest_status(repo: Any, branch: str = "main") -> dict[str, object]:
    return get_latest_ci_status(repo, branch)

@mcp.tool(name="ci_read_coverage")
def ci_read_coverage(repo: Any) -> dict[str, object]:
    return read_coverage_report(repo)

@mcp.tool(name="ci_check_branch_protection")
def ci_check_branch_protection(repo: Any, branch: str = "main") -> dict[str, object]:
    return check_branch_protection(repo, branch)

@mcp.tool(name="state_read")
def state_read(repo: str | Path) -> dict[str, Any]:
    return read_state(repo)

@mcp.tool(name="verify_floor")
def verify_floor_tool(repo: str | Path) -> dict[str, Any]:
    return verify_floor(repo)

@mcp.tool(name="verify_git_clean")
def verify_git_clean_tool(repo: str | Path) -> dict[str, Any]:
    return verify_git_clean(repo)

@mcp.tool(name="verify_manual_proof")
def verify_manual_proof_tool(repo: str | Path, scenario: str) -> dict[str, Any]:
    return verify_manual_proof(repo, scenario)

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
