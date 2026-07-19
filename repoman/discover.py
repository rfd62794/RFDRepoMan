"""Read-only local repository discovery."""
from __future__ import annotations

import os
from pathlib import Path


ROOT_ENV_VAR = "RFD_REPOMAN_ROOT"


def discover_repos(root: str | Path | None = None) -> list[str]:
    resolved_root = root or os.getenv(ROOT_ENV_VAR)
    if not resolved_root:
        raise RuntimeError(f"{ROOT_ENV_VAR} must be set or root must be supplied")
    base = Path(resolved_root)
    if not base.exists():
        return []
    return sorted(str(path.parent) for path in base.rglob(".git") if path.is_dir())
