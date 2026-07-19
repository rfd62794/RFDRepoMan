from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from repoman import self_verify


def _run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def test_verify_floor_returns_real_output(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "fixture"\nversion = "0.0.0"\nrequires-python = ">=3.12"\n\n[dependency-groups]\ndev = ["pytest>=9.1"]\n')
    _run("uv", "lock", cwd=tmp_path)
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_failure.py").write_text("def test_failure():\n    assert False\n")
    result = self_verify.verify_floor(tmp_path)
    assert result["return_code"] != 0
    assert "failed" in result["stdout"]
    assert result["parsed"] is True and result["counts"]["failed"] == 1


def test_verify_floor_unparseable_flagged(monkeypatch, tmp_path):
    monkeypatch.setattr(self_verify, "_run", lambda *args: subprocess.CompletedProcess(args, 0, "no pytest summary", ""))
    result = self_verify.verify_floor(tmp_path)
    assert result["parsed"] is False and result["counts"] is None


def test_verify_git_clean_detects_dirty(tmp_path):
    _run("git", "init", "--quiet", cwd=tmp_path)
    (tmp_path / "uncommitted.txt").write_text("dirty")
    result = self_verify.verify_git_clean(tmp_path)
    assert result["clean"] is False and "uncommitted.txt" in result["stdout"]


def test_verify_git_clean_detects_clean(tmp_path):
    _run("git", "init", "--quiet", cwd=tmp_path)
    result = self_verify.verify_git_clean(tmp_path)
    assert result["clean"] is True and result["stdout"] == ""


def test_verify_manual_proof_scenario_enum_closed(tmp_path):
    with pytest.raises(ValueError, match="Unknown verification scenario"):
        self_verify.verify_manual_proof(tmp_path, "arbitrary")


def test_verify_manual_proof_calls_real_functions(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(self_verify, "push", lambda repo, confirmed=False: calls.append((repo, confirmed)) or {"refused": "push requires confirmed=True"})
    result = self_verify.verify_manual_proof(tmp_path, "unconfirmed_push")
    assert calls == [(tmp_path, False)]
    assert result["result"]["refused"] == "push requires confirmed=True"
