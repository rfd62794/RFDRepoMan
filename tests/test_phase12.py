from __future__ import annotations

import logging
import subprocess

from repoman import config, github_status


def test_discovery_uses_dedicated_timeout(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(github_status, "discover_repos", lambda root: [])
    monkeypatch.setattr(github_status, "_within_timeout", lambda operation, timeout: calls.append(timeout) or (True, operation()))
    github_status.reconcile_status_for_accounts([], tmp_path, global_budget_seconds=20)
    assert calls[0] == github_status.DISCOVERY_TIMEOUT_SECONDS
    assert github_status.DISCOVERY_TIMEOUT_SECONDS > github_status.NETWORK_TIMEOUT_SECONDS


def test_gh_failure_log_is_redacted(monkeypatch, caplog):
    monkeypatch.setattr(config.shutil, "which", lambda name: "C:/Program Files/GitHub CLI/gh.exe")
    monkeypatch.setattr(config.subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1, "token-output", "error gho_abcdefghijklmnopqrstuvwxyz0123456789"))
    with caplog.at_level(logging.WARNING, logger="repoman.config"):
        config._gh(["gh", "auth", "status"], 5)
    assert "token-output" not in caplog.text
    assert "abcdefghijklmnopqrstuvwxyz" not in caplog.text
    assert "return_code=1" in caplog.text


def test_gh_timeout_log_contains_no_token(monkeypatch, caplog):
    monkeypatch.setattr(config.shutil, "which", lambda name: "C:/Program Files/GitHub CLI/gh.exe")
    monkeypatch.setattr(config.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired(args[0], kwargs["timeout"])))
    with caplog.at_level(logging.WARNING, logger="repoman.config"):
        result = config._gh(["gh", "auth", "status"], 5)
    assert result.returncode == 1
    assert "timed out" in caplog.text
    assert "token" not in caplog.text.lower()
