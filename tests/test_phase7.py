from __future__ import annotations

import logging
import subprocess

from repoman import config


def _result(args: list[str], stdout: str = "", stderr: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args, returncode, stdout, stderr)


def test_env_var_preferred_over_fallback(monkeypatch):
    monkeypatch.setenv(config.token_env_var("example-account"), "environment-token")
    monkeypatch.setenv(config.GH_FALLBACK_ENV_VAR, "true")
    monkeypatch.setattr(config, "_gh", lambda command: (_ for _ in ()).throw(AssertionError("gh invoked")))
    assert config.resolve_token("example-account") == ("environment-token", "env")


def test_fallback_disabled_by_default(monkeypatch):
    monkeypatch.delenv(config.token_env_var("example-account"), raising=False)
    monkeypatch.delenv(config.GH_FALLBACK_ENV_VAR, raising=False)
    monkeypatch.setattr(config, "_gh", lambda command: (_ for _ in ()).throw(AssertionError("gh invoked")))
    assert config.resolve_token("example-account") == (None, "none")


def test_fallback_used_when_explicitly_enabled(monkeypatch):
    monkeypatch.setenv(config.GH_FALLBACK_ENV_VAR, "true")
    monkeypatch.delenv(config.token_env_var("example-account"), raising=False)
    responses = iter((_result(["gh"], stderr="Logged in to github.com account example-account (keyring)\n"), _result(["gh"], stdout="fallback-token\n")))
    monkeypatch.setattr(config, "_gh", lambda command: next(responses))
    assert config.resolve_token("example-account") == ("fallback-token", "gh_fallback")


def test_fallback_rejects_account_mismatch(monkeypatch):
    monkeypatch.setenv(config.GH_FALLBACK_ENV_VAR, "true")
    monkeypatch.delenv(config.token_env_var("requested-account"), raising=False)
    calls = []
    monkeypatch.setattr(config, "_gh", lambda command: calls.append(command) or _result(command, stderr="Logged in to github.com account active-account (keyring)\n"))
    assert config.resolve_token("requested-account") == (None, "gh_account_mismatch")
    assert len(calls) == 1


def test_fallback_use_is_logged(monkeypatch, caplog):
    monkeypatch.setenv(config.GH_FALLBACK_ENV_VAR, "true")
    monkeypatch.delenv(config.token_env_var("example-account"), raising=False)
    responses = iter((_result(["gh"], stderr="account example-account\n"), _result(["gh"], stdout="fallback-token\n")))
    monkeypatch.setattr(config, "_gh", lambda command: next(responses))
    with caplog.at_level(logging.WARNING, logger="repoman.config"):
        config.resolve_token("example-account")
    assert "example-account" in caplog.text
    assert "scope may exceed" in caplog.text
    assert "fallback-token" not in caplog.text


def test_gh_invoked_with_fixed_args_only(monkeypatch):
    monkeypatch.setenv(config.GH_FALLBACK_ENV_VAR, "true")
    monkeypatch.delenv(config.token_env_var("example-account"), raising=False)
    commands = []
    responses = iter((_result(["gh"], stderr="account example-account\n"), _result(["gh"], stdout="fallback-token\n")))
    monkeypatch.setattr(config, "_gh", lambda command: commands.append(command) or next(responses))
    config.resolve_token("example-account")
    assert commands == [
        ["gh", "auth", "status", "--hostname", "github.com", "--active"],
        ["gh", "auth", "token", "--hostname", "github.com"],
    ]
