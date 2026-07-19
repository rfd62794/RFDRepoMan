from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from repoman import ci_status, discover, gate, git_actions, github_actions, github_planning, github_status, phase_bridge, policy, state_reader, status
from repoman.hosts.bitbucket_stub import BitbucketStatus
from repoman.hosts.gitlab_stub import GitLabStatus


class Calls:
    def __init__(self): self.items = []
    def __call__(self, *args, **kwargs): self.items.append((args, kwargs)); return ""


def test_discover_finds_git_repos(tmp_path):
    (tmp_path / "one" / ".git").mkdir(parents=True)
    (tmp_path / "plain").mkdir()
    assert discover.discover_repos(tmp_path) == [str(tmp_path / "one")]


def test_status_never_calls_pull_or_merge(monkeypatch):
    calls = Calls()
    monkeypatch.setattr(status, "_git", calls)
    calls.items = []
    def fake(repo, *args):
        calls.items.append(args)
        return {("branch", "--show-current"): "main", ("status", "--porcelain"): "", ("log", "-1", "--format=%H%x00%aI%x00%s"): "h\x00d\x00m", ("rev-parse", "--abbrev-ref", "@{upstream}"): "origin/main", ("rev-list", "--left-right", "--count", "HEAD...origin/main"): "0 0"}.get(args, "")
    monkeypatch.setattr(status, "_git", fake)
    status.repo_status("x")
    assert all("pull" not in call and "merge" not in call for call in calls.items)


def test_state_reader_missing_file_explicit(tmp_path):
    result = state_reader.read_state(tmp_path)
    assert result["found"] is False and "phase" in result["missing"]


def test_state_reader_missing_policy_fields_explicit(tmp_path):
    path = tmp_path / "docs" / "state"; path.mkdir(parents=True)
    (path / "current.md").write_text("phase: P1\ncertified_floor: none\nwhat_is_next: tests\n")
    result = state_reader.read_state(tmp_path)
    assert set(result["missing"]) >= {"require_ci_pass", "min_coverage", "protected_branches"}


def test_git_actions_reject_raw_shell_input():
    assert "command" not in inspect.signature(git_actions.fetch).parameters
    assert "command" not in inspect.signature(git_actions.push).parameters


def test_git_push_requires_confirmed_flag(monkeypatch):
    monkeypatch.setattr(git_actions, "_git", lambda *a: pytest.fail("git executed"))
    assert "refused" in git_actions.push("x")


def test_git_merge_requires_confirmed_flag(monkeypatch):
    monkeypatch.setattr(git_actions, "_git", lambda *a: pytest.fail("git executed"))
    assert "refused" in git_actions.merge("x", "topic")


def test_force_push_not_exposed():
    for func in (git_actions.push, git_actions.merge):
        assert "force" not in inspect.signature(func).parameters


def test_github_status_reconciles_local_and_remote():
    rows = github_status.reconcile_repos(["C:/Github/Local"], [{"name": "Local"}, {"name": "Remote"}])
    assert {row["location"] for row in rows} == {"both", "remote-only"}


def test_github_status_is_read_only():
    source = inspect.getsource(github_status)
    assert ".edit(" not in source and ".create_" not in source and ".delete(" not in source

def test_github_write_actions_require_confirmed():
    actions = (
        (github_actions.create_pr, (SimpleNamespace(), "t", "b", "h", "main")),
        (github_actions.merge_pr, (SimpleNamespace(), 1)),
        (github_actions.set_visibility, (SimpleNamespace(), True)),
        (github_actions.delete_remote_branch, (SimpleNamespace(), "topic")),
    )
    for func, args in actions:
        assert "refused" in func(*args)


def test_github_low_consequence_actions_logged_not_gated():
    events = []
    issue = SimpleNamespace(create_comment=lambda body: None, edit=lambda **kw: None)
    pr = SimpleNamespace(edit=lambda **kw: None, create_review_request=lambda **kw: None)
    repo = SimpleNamespace(full_name="o/r", get_issue=lambda _: issue, get_pull=lambda _: pr, create_fork=lambda organization=None: SimpleNamespace(full_name="f/r"), create_git_ref=lambda **kw: None)
    github_actions.close_pr(repo, 1, events.append)
    github_actions.add_pr_comment(repo, 1, "x", events.append)
    github_actions.create_fork(repo, audit=events.append)
    github_actions.github_create_branch(repo, "topic", "abc", events.append)
    assert len(events) == 4


def test_gate_registry_shared_by_both_domains():
    assert git_actions.CONSEQUENTIAL_ACTIONS is gate.CONSEQUENTIAL_ACTIONS
    assert github_actions.CONSEQUENTIAL_ACTIONS is gate.CONSEQUENTIAL_ACTIONS


def test_token_never_in_output(monkeypatch):
    monkeypatch.setenv("RFD_REPOMAN_GH_TOKEN_RFD62794", "secret-token-value")
    assert "secret-token-value" not in str(__import__("repoman.config", fromlist=["*"]).safe_error("token failed"))


def test_stubs_raise_not_implemented():
    for stub in (GitLabStatus(), BitbucketStatus()):
        for method in (stub.list_account_repos, stub.list_prs, stub.list_forks, stub.list_remote_branches):
            with pytest.raises(NotImplementedError): method(None)


def test_planning_actions_logged_ungated():
    events = []
    repo = SimpleNamespace(full_name="o/r", create_milestone=lambda **kw: SimpleNamespace(number=2))
    result = github_planning.github_create_milestone(repo, "P1", audit=events.append)
    assert result["number"] == 2 and events[0]["action"] == "github_create_milestone"


def test_phase_bridge_reports_drift_only(tmp_path):
    path = tmp_path / "docs" / "state"; path.mkdir(parents=True)
    (path / "current.md").write_text("phase: P1\ncertified_floor: 22 passing\nwhat_is_next: done\n")
    repo = SimpleNamespace(get_milestones=lambda state="all": [])
    result = phase_bridge.reconcile_phase(tmp_path, repo)
    assert result["drift"] == ["no matching milestone"]


def test_ci_status_read_only():
    source = inspect.getsource(ci_status)
    assert ".edit(" not in source and ".create_" not in source and ".delete(" not in source


def _policy_repo(tmp_path, content):
    folder = tmp_path / "docs" / "state"; folder.mkdir(parents=True)
    (folder / "current.md").write_text(content)
    return tmp_path


def test_policy_no_declaration_no_enforcement(tmp_path):
    repo = _policy_repo(tmp_path, "phase: P1\ncertified_floor: none\nwhat_is_next: work\n")
    assert policy.evaluate_merge_policy(repo, "main", "failure", 0) == []


def test_policy_blocks_on_ci_fail(tmp_path):
    repo = _policy_repo(tmp_path, "require_ci_pass: true\n")
    assert "refused" in policy.authorize_merge(repo, "main", "failure", None, False, None)


def test_policy_blocks_below_min_coverage(tmp_path):
    repo = _policy_repo(tmp_path, "min_coverage: 90\n")
    assert "min_coverage" in policy.evaluate_merge_policy(repo, "main", "success", 80)[0]


def test_override_requires_separate_flag_and_reason(tmp_path):
    repo = _policy_repo(tmp_path, "require_ci_pass: true\n")
    missing_reason = policy.authorize_merge(repo, "main", "failure", None, True, None)
    events = []
    result = policy.authorize_merge(repo, "main", "failure", None, True, "approved exception", events.append)
    assert "override_reason" in missing_reason["refused"]
    assert result["override"]["reason"] == "approved exception" and events
