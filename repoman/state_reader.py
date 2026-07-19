"""Parser for explicit project state declarations."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

FIELDS = ("phase", "certified_floor", "what_is_next", "require_ci_pass", "min_coverage", "protected_branches")


def _value(text: str, name: str) -> str | None:
    match = re.search(rf"(?mi)^\s*{re.escape(name)}\s*:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else None


def read_state(repo: str | Path) -> dict[str, Any]:
    path = Path(repo) / "docs" / "state" / "current.md"
    if not path.is_file():
        return {"found": False, "path": str(path), "missing": list(FIELDS), "fields": {}}
    text = path.read_text(encoding="utf-8")
    fields: dict[str, Any] = {}
    missing: list[str] = []
    for name in FIELDS:
        raw = _value(text, name)
        if raw is None:
            missing.append(name)
            continue
        if name == "require_ci_pass":
            if raw.lower() not in {"true", "false"}:
                raise ValueError("require_ci_pass must be true or false")
            fields[name] = raw.lower() == "true"
        elif name == "min_coverage":
            value = float(raw)
            if not 0 <= value <= 100:
                raise ValueError("min_coverage must be between 0 and 100")
            fields[name] = value
        elif name == "protected_branches":
            fields[name] = [item.strip() for item in raw.strip("[]").split(",") if item.strip()]
        else:
            fields[name] = raw
    return {"found": True, "path": str(path), "missing": missing, "fields": fields}
