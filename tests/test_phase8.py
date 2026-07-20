from __future__ import annotations

import asyncio
import inspect
import time

from repoman import github_status, phase_bridge
from repoman.server import mcp


def test_reconcile_no_client_object_param():
    signature = inspect.signature(github_status.reconcile_status_for_accounts)
    assert tuple(signature.parameters) == ("account_names", "root", "include_pr_counts", "force_refresh", "per_account_budget_seconds", "global_budget_seconds")
    assert all(parameter.annotation is not object for parameter in signature.parameters.values())


def test_reconcile_returns_explicit_error_no_credential(monkeypatch, tmp_path):
    monkeypatch.setattr(github_status, "resolve_token", lambda account: (None, "none"))
    result = github_status.reconcile_status_for_accounts(["missing-account"], tmp_path)
    assert result["accounts"]["missing-account"] == {"error": "no_credential_available", "account": "missing-account"}


def test_reconcile_isolates_per_account_failure(monkeypatch, tmp_path):
    class Pages:
        def get_page(self, page): return [type("Repo", (), {"name": "repo", "full_name": "owner/repo", "visibility": "public", "stargazers_count": 0, "open_issues_count": 0, "default_branch": "main"})()] if page == 0 else []

    monkeypatch.setattr(github_status, "resolve_token", lambda account: (None, "none") if account == "missing" else ("token", "env"))
    monkeypatch.setattr(github_status, "_github_client", lambda token: type("Client", (), {"get_user": lambda self: type("User", (), {"get_repos": lambda self, per_page: Pages()})()})())
    monkeypatch.setattr(github_status, "begin_snapshot", lambda account: {"current": {}, "previous": {}})
    monkeypatch.setattr(github_status, "merge_live_repos", lambda account, cache, repos: cache)
    monkeypatch.setattr(github_status, "cached_repos", lambda cache: [])
    result = github_status.reconcile_status_for_accounts(["missing", "available"], tmp_path)
    assert result["accounts"]["missing"]["error"] == "no_credential_available"
    assert result["accounts"]["available"]["freshly_fetched"] == 1


def test_reconcile_has_explicit_timeout(monkeypatch, tmp_path):
    class Pages:
        def get_page(self, page):
            time.sleep(0.2)
            return []

    monkeypatch.setattr(github_status, "NETWORK_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(github_status, "resolve_token", lambda account: ("token", "env"))
    monkeypatch.setattr(github_status, "_github_client", lambda token: type("Client", (), {"get_user": lambda self: type("User", (), {"get_repos": lambda self, per_page: Pages()})()})())
    monkeypatch.setattr(github_status, "begin_snapshot", lambda account: {"current": {}, "previous": {}})
    monkeypatch.setattr(github_status, "cached_repos", lambda cache: [])
    started = time.monotonic()
    result = github_status.reconcile_status_for_accounts(["account"], tmp_path)
    assert time.monotonic() - started < 0.1
    assert result["accounts"]["account"]["truncated"] is True


def test_phase_bridge_by_name_no_object_param():
    signature = inspect.signature(phase_bridge.phase_bridge_check_by_name)
    assert tuple(signature.parameters) == ("repo_path", "github_repo_name", "account_name")
    assert all(parameter.annotation is not object for parameter in signature.parameters.values())


def test_server_exposes_safe_wrappers_not_raw():
    tools = asyncio.run(mcp.list_tools())
    reconcile_tool = next(tool for tool in tools if tool.name == "github_reconcile_status")
    bridge_tool = next(tool for tool in tools if tool.name == "phase_bridge_check")
    assert reconcile_tool.fn.__name__ == "github_reconcile_status"
    assert bridge_tool.fn.__name__ == "phase_bridge_check"
    assert reconcile_tool.fn.__globals__["reconcile_status_for_accounts"] is github_status.reconcile_status_for_accounts
    assert bridge_tool.fn.__globals__["phase_bridge_check_by_name"] is phase_bridge.phase_bridge_check_by_name
    assert "clients" not in inspect.signature(reconcile_tool.fn).parameters
    assert "github_repo" not in inspect.signature(bridge_tool.fn).parameters
