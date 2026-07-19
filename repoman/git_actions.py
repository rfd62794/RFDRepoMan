"""Typed local git actions with no shell passthrough."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

from repoman.gate import CONSEQUENTIAL_ACTIONS, require_confirmation
from repoman.policy import authorize_merge


def _git(repo: str | Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def fetch(repo: str | Path, remote: str = "origin") -> dict[str, str]:
    _git(repo, "fetch", remote)
    return {"action": "fetch", "repo": str(repo), "remote": remote}


def pull(repo: str | Path, remote: str = "origin", branch: str = "main") -> dict[str, str]:
    _git(repo, "pull", "--ff-only", remote, branch)
    return {"action": "pull", "repo": str(repo), "branch": branch}


def commit(repo: str | Path, message: str) -> dict[str, str]:
    if not message.strip():
        raise ValueError("commit message is required")
    _git(repo, "commit", "-m", message)
    return {"action": "commit", "repo": str(repo)}


def push(repo: str | Path, remote: str = "origin", branch: str = "main", confirmed: bool = False) -> dict[str, str]:
    refusal = require_confirmation("push", confirmed)
    if refusal:
        return refusal
    _git(repo, "push", remote, branch)
    return {"action": "push", "repo": str(repo), "branch": branch}


def create_branch(repo: str | Path, branch: str, start_point: str = "HEAD") -> dict[str, str]:
    _git(repo, "branch", branch, start_point)
    return {"action": "create_branch", "repo": str(repo), "branch": branch}


def checkout(repo: str | Path, branch: str) -> dict[str, str]:
    _git(repo, "checkout", branch)
    return {"action": "checkout", "repo": str(repo), "branch": branch}


def merge(repo: str | Path, branch: str, target_branch: str = "main", confirmed: bool = False, override_policy: bool = False, override_reason: str | None = None, ci_status: str | None = None, coverage: float | None = None, audit: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    refusal = require_confirmation("merge", confirmed)
    if refusal:
        return refusal
    policy_result = authorize_merge(repo, target_branch, ci_status, coverage, override_policy, override_reason, audit)
    if policy_result and "refused" in policy_result:
        return policy_result
    _git(repo, "merge", "--no-ff", branch)
    return {"action": "merge", "repo": str(repo), "branch": branch, "policy": policy_result}
