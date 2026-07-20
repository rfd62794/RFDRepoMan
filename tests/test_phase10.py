from __future__ import annotations

import subprocess
import time

from repoman import config, github_status


def _cache(monkeypatch):
    monkeypatch.setattr(github_status, "begin_snapshot", lambda account: {"current": {}, "previous": {}})
    monkeypatch.setattr(github_status, "cached_repos", lambda cache: [])


def test_gh_subprocess_has_explicit_timeout(monkeypatch):
    calls = []
    monkeypatch.setattr(config.subprocess, "run", lambda *args, **kwargs: calls.append(kwargs) or subprocess.CompletedProcess(args[0], 1, "", ""))
    config._gh(["gh", "auth", "status"], 3)
    assert calls[0]["timeout"] == 3


def test_gh_timeout_returns_none_not_exception(monkeypatch):
    monkeypatch.setenv(config.GH_FALLBACK_ENV_VAR, "true")
    monkeypatch.delenv(config.token_env_var("account"), raising=False)
    monkeypatch.setattr(config.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired(args[0], kwargs["timeout"])))
    assert config.resolve_token("account") == (None, "none")


def test_discover_repos_bounded_in_reconciliation(monkeypatch, tmp_path):
    _cache(monkeypatch)
    monkeypatch.setattr(github_status, "discover_repos", lambda root: time.sleep(0.2) or [])
    started = time.monotonic()
    result = github_status.reconcile_status_for_accounts([], tmp_path, global_budget_seconds=0.01)
    assert time.monotonic() - started < 0.1
    assert result["discovery_timed_out"] is True


def test_global_budget_caps_total_runtime(monkeypatch, tmp_path):
    _cache(monkeypatch)
    monkeypatch.setattr(github_status, "discover_repos", lambda root: [])
    monkeypatch.setattr(github_status, "resolve_token", lambda account: time.sleep(0.02) or ("token", "env"))
    started = time.monotonic()
    result = github_status.reconcile_status_for_accounts(["one", "two"], tmp_path, global_budget_seconds=0.01)
    assert time.monotonic() - started < 0.1
    assert result["accounts"]["two"]["truncated"] is True


def test_global_budget_echoed_in_result(monkeypatch, tmp_path):
    _cache(monkeypatch)
    monkeypatch.setattr(github_status, "discover_repos", lambda root: [])
    result = github_status.reconcile_status_for_accounts([], tmp_path, global_budget_seconds=12)
    assert result["global_budget_seconds"] == 12


def test_default_global_budget_scales_with_account_count(monkeypatch, tmp_path):
    _cache(monkeypatch)
    monkeypatch.setattr(github_status, "discover_repos", lambda root: [])
    result = github_status.reconcile_status_for_accounts(["one", "two", "three"], tmp_path, per_account_budget_seconds=2)
    assert result["global_budget_seconds"] == 21
