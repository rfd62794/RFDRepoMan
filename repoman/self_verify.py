"""Bounded, fact-reporting verification helpers."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from repoman.git_actions import merge, push
from repoman.policy import authorize_merge
from repoman.toolchain import detect_toolchain


SCENARIOS = {"unconfirmed_push", "unconfirmed_merge", "policy_override_cycle"}


def _run(repo: str | Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=repo, capture_output=True, text=True, check=False)


def _pytest_counts(output: str) -> dict[str, int] | None:
    summary = re.search(r"(?:=+\s*)?(?P<counts>(?:\d+\s+(?:passed|failed|skipped)(?:,\s*)?)+)(?:\s+in\s+\d+(?:\.\d+)?s)?\s*=*", output)
    if not summary:
        return None
    counts = {name: 0 for name in ("passed", "failed", "skipped")}
    for amount, name in re.findall(r"(\d+)\s+(passed|failed|skipped)", summary.group("counts")):
        counts[name] = int(amount)
    return counts


def verify_floor(repo: str | Path) -> dict[str, Any]:
    detection = detect_toolchain(repo)
    if detection["toolchain"] != "uv":
        return {"toolchain": detection, "status": "unsupported_toolchain", "stdout": "", "stderr": "", "return_code": None, "parsed": False, "counts": None}
    result = _run(repo, "uv", "run", "pytest", "-q")
    output = result.stdout
    counts = _pytest_counts(output)
    return {"toolchain": detection, "stdout": output, "stderr": result.stderr, "return_code": result.returncode, "parsed": counts is not None, "counts": counts}


def verify_git_clean(repo: str | Path) -> dict[str, Any]:
    result = _run(repo, "git", "status", "--short")
    return {"stdout": result.stdout, "stderr": result.stderr, "return_code": result.returncode, "clean": result.stdout == ""}


def verify_manual_proof(repo: str | Path, scenario: str) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown verification scenario: {scenario}")
    if scenario == "unconfirmed_push":
        return {"scenario": scenario, "result": push(repo, confirmed=False)}
    if scenario == "unconfirmed_merge":
        return {"scenario": scenario, "result": merge(repo, "verification-topic", confirmed=False)}
    with tempfile.TemporaryDirectory() as directory:
        policy_repo = Path(directory)
        state_directory = policy_repo / "docs" / "state"
        state_directory.mkdir(parents=True)
        (state_directory / "current.md").write_text("require_ci_pass: true\n", encoding="utf-8")
        refused = authorize_merge(policy_repo, "main", "failure", None, False, None)
        overridden = authorize_merge(policy_repo, "main", "failure", None, True, "self-verification scenario")
    return {"scenario": scenario, "refused": refused, "overridden": overridden}
