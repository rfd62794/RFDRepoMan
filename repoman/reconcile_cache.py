"""Gitignored, two-snapshot cache for bounded GitHub reconciliation."""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CACHE_DIRECTORY = Path(__file__).parents[1] / ".repoman_cache"


def _cache_path(account_name: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", account_name)
    return CACHE_DIRECTORY / f"{safe_name}.json"


def _read(account_name: str) -> dict[str, Any]:
    path = _cache_path(account_name)
    if not path.is_file():
        return {"current": {}, "previous": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def begin_snapshot(account_name: str) -> dict[str, Any]:
    cache = _read(account_name)
    return {"current": {}, "previous": cache.get("current", {})}


def write_snapshot(account_name: str, cache: dict[str, Any]) -> None:
    CACHE_DIRECTORY.mkdir(exist_ok=True)
    _cache_path(account_name).write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def merge_live_repos(account_name: str, cache: dict[str, Any], repos: list[dict[str, Any]]) -> dict[str, Any]:
    fetched_at = datetime.now(UTC).isoformat()
    for repo in repos:
        cache["current"][repo["name"].lower()] = {**repo, "fetched_at": fetched_at, "source": "live"}
    write_snapshot(account_name, cache)
    return cache


def cached_repos(cache: dict[str, Any]) -> list[dict[str, Any]]:
    merged = {**cache.get("previous", {}), **cache.get("current", {})}
    return [{**repo, "source": "cached"} for repo in merged.values()]
