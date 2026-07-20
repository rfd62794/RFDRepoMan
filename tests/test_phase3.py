from __future__ import annotations

import asyncio
import inspect
from pathlib import Path

from repoman import git_actions, github_actions, github_planning, github_status
from repoman.ci_status import check_branch_protection, get_latest_ci_status, list_workflow_runs, read_coverage_report
from repoman.phase_bridge import reconcile_phase
from repoman.server import (
    ci_check_branch_protection,
    ci_get_latest_status,
    ci_list_workflow_runs,
    ci_read_coverage,
    github_create_pr,
    mcp,
    repoman_checkout,
    repoman_commit,
    repoman_fetch,
    repoman_pull,
    repoman_push,
)
from repoman.state_reader import read_state
from repoman.status import repo_status
from repoman.self_verify import verify_floor, verify_git_clean, verify_manual_proof
from repoman.token_setup import generate_token_url


EXPECTED_TOOLS = {
    "repoman_fetch", "repoman_status", "repoman_push", "repoman_pull", "repoman_commit", "repoman_create_branch", "repoman_checkout", "repoman_merge",
    "github_create_pr", "github_merge_pr", "github_close_pr", "github_add_pr_comment", "github_request_pr_review", "github_create_fork", "github_create_branch", "github_delete_remote_branch", "github_set_visibility", "github_create_issue", "github_close_issue",
    "github_list_prs", "github_list_forks", "github_list_remote_branches", "github_reconcile_status",
    "github_create_milestone", "github_close_milestone", "github_link_issue_to_milestone", "github_update_project_status", "phase_bridge_check",
    "ci_list_workflow_runs", "ci_get_latest_status", "ci_read_coverage", "ci_check_branch_protection", "state_read",
    "verify_floor", "verify_git_clean", "verify_manual_proof", "generate_token_setup_url",
}


def tool_names() -> set[str]:
    return {tool.name for tool in asyncio.run(mcp.list_tools())}


def test_all_tested_functions_registered():
    tested_functions = {
        git_actions.fetch, git_actions.pull, git_actions.commit, git_actions.push, git_actions.create_branch, git_actions.checkout, git_actions.merge,
        github_actions.create_pr, github_actions.merge_pr, github_actions.close_pr, github_actions.add_pr_comment, github_actions.request_pr_review, github_actions.create_fork, github_actions.github_create_branch, github_actions.delete_remote_branch, github_actions.set_visibility, github_actions.create_issue, github_actions.close_issue,
        github_status.list_prs, github_status.list_forks, github_status.list_remote_branches, github_status.github_status,
        github_planning.github_create_milestone, github_planning.github_close_milestone, github_planning.github_link_issue_to_milestone, github_planning.github_update_project_status,
        reconcile_phase, list_workflow_runs, get_latest_ci_status, read_coverage_report, check_branch_protection, read_state, repo_status,
        verify_floor, verify_git_clean, verify_manual_proof, generate_token_url,
    }
    assert len(tested_functions) == len(EXPECTED_TOOLS)
    assert EXPECTED_TOOLS <= tool_names()


def test_tool_wrappers_pass_through_unchanged():
    pairs = (
        (repoman_fetch, git_actions.fetch),
        (repoman_pull, git_actions.pull),
        (repoman_commit, git_actions.commit),
        (repoman_push, git_actions.push),
        (repoman_checkout, git_actions.checkout),
        (github_create_pr, github_actions.create_pr),
        (ci_list_workflow_runs, list_workflow_runs),
        (ci_get_latest_status, get_latest_ci_status),
        (ci_read_coverage, read_coverage_report),
        (ci_check_branch_protection, check_branch_protection),
    )
    for wrapper, underlying in pairs:
        assert inspect.signature(wrapper) == inspect.signature(underlying)


def test_create_pr_actually_registered():
    assert "github_create_pr" in tool_names()


def test_no_personal_identifiers_in_source():
    root = Path(__file__).parents[1]
    source_files = [* (root / "repoman").glob("*.py"), * (root / "scripts").glob("*.py")]
    identifiers = ("rfd" + "62794", "consumr" + "buzzy")
    for source_file in source_files:
        content = source_file.read_text(encoding="utf-8").lower()
        assert all(identifier not in content for identifier in identifiers)


def test_server_starts_with_full_tool_list():
    assert tool_names() == EXPECTED_TOOLS
