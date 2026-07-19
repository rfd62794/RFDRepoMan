"""File-based repository toolchain detection."""
from __future__ import annotations

from pathlib import Path


def detect_toolchain(repo: str | Path) -> dict[str, str | None]:
    root = Path(repo)
    python_version_path = root / ".python-version"
    python_version = python_version_path.read_text(encoding="utf-8").strip() if python_version_path.is_file() else None
    if (root / "Cargo.toml").is_file():
        toolchain = "rust"
    elif (root / "pyproject.toml").is_file() and (root / "uv.lock").is_file():
        toolchain = "uv"
    elif (root / "pyproject.toml").is_file():
        toolchain = "python_ambiguous"
    elif (root / "requirements.txt").is_file():
        toolchain = "pip"
    elif (root / "package.json").is_file():
        toolchain = "node"
    else:
        toolchain = "unknown"
    return {"toolchain": toolchain, "python_version": python_version}
