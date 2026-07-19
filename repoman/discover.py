"""Read-only local repository discovery."""
from __future__ import annotations

from pathlib import Path


def discover_repos(root: str | Path = r"C:\Github") -> list[str]:
    base = Path(root)
    if not base.exists():
        return []
    return sorted(str(path.parent) for path in base.rglob(".git") if path.is_dir())
