"""Read-only git status inspection."""
from __future__ import annotations

import subprocess
from pathlib import Path


def _git(repo: str | Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def repo_status(repo: str | Path, remote: str = "origin") -> dict[str, object]:
    _git(repo, "fetch", remote)
    branch = _git(repo, "branch", "--show-current")
    dirty = bool(_git(repo, "status", "--porcelain"))
    head = _git(repo, "log", "-1", "--format=%H%x00%aI%x00%s").split("\x00")
    upstream = _git(repo, "rev-parse", "--abbrev-ref", "@{upstream}")
    counts = _git(repo, "rev-list", "--left-right", "--count", f"HEAD...{upstream}").split()
    return {"repo": str(repo), "branch": branch, "dirty": dirty, "ahead": int(counts[0]), "behind": int(counts[1]), "last_commit": {"hash": head[0], "date": head[1], "message": head[2]}}
