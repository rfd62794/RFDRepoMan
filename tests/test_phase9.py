from __future__ import annotations

import time
from types import SimpleNamespace

from repoman import github_status, reconcile_cache


def _repo(name: str):
    return SimpleNamespace(name=name, full_name=f"owner/{name}", visibility="public", stargazers_count=0, open_issues_count=0, default_branch="main")


def _client(pages: list[list[object]]):
    class Repos:
        def get_page(self, page: int):
            return pages[page] if page < len(pages) else []

    return SimpleNamespace(get_user=lambda: SimpleNamespace(get_repos=lambda per_page: Repos()))


def _memory_cache(monkeypatch):
    cache = {"current": {}, "previous": {}}
    monkeypatch.setattr(github_status, "begin_snapshot", lambda account: cache)
    monkeypatch.setattr(github_status, "merge_live_repos", lambda account, cache, repos: cache["current"].update({repo["name"].lower(): {**repo, "fetched_at": "2026-01-01T00:00:00+00:00", "source": "live"} for repo in repos}) or cache)
    monkeypatch.setattr(github_status, "cached_repos", lambda cache: [{**repo, "source": "cached"} for repo in {**cache["previous"], **cache["current"]}.values()])
    return cache


def test_reconcile_paginates_large_account(monkeypatch, tmp_path):
    _memory_cache(monkeypatch)
    pages = [[_repo(f"repo-{index}") for index in range(100)], [_repo("repo-100")]]
    monkeypatch.setattr(github_status, "resolve_token", lambda account: ("token", "env"))
    monkeypatch.setattr(github_status, "_github_client", lambda token: _client(pages))
    result = github_status.reconcile_status_for_accounts(["account"], tmp_path, per_account_budget_seconds=1)
    assert result["accounts"]["account"]["freshly_fetched"] == 101
    assert len(result["accounts"]["account"]["repos"]) == 101


def test_reconcile_respects_per_account_budget(monkeypatch, tmp_path):
    _memory_cache(monkeypatch)
    monkeypatch.setattr(github_status, "resolve_token", lambda account: ("token", "env"))
    monkeypatch.setattr(github_status, "_github_client", lambda token: _client([[_repo("slow")]]))
    monkeypatch.setattr(github_status, "_repo_summary", lambda repo, counts: time.sleep(0.2) or {"name": repo.name})
    started = time.monotonic()
    result = github_status.reconcile_status_for_accounts(["account"], tmp_path, per_account_budget_seconds=0.01)
    assert time.monotonic() - started < 0.1
    assert result["accounts"]["account"]["truncated"] is True


def test_reconcile_backfills_from_cache_on_truncation(monkeypatch, tmp_path):
    cache = _memory_cache(monkeypatch)
    cache["previous"] = {"cached": {"name": "cached", "fetched_at": "2020-01-01T00:00:00+00:00", "source": "live"}}
    monkeypatch.setattr(github_status, "resolve_token", lambda account: ("token", "env"))
    monkeypatch.setattr(github_status, "_github_client", lambda token: _client([[_repo("live")]]))
    monkeypatch.setattr(github_status, "_repo_summary", lambda repo, counts: time.sleep(0.2) or {"name": repo.name})
    result = github_status.reconcile_status_for_accounts(["account"], tmp_path, per_account_budget_seconds=0.01)
    cached = next(item["remote"] for item in result["accounts"]["account"]["repos"] if item["name"] == "cached")
    assert cached["source"] == "cached" and cached["fetched_at"] == "2020-01-01T00:00:00+00:00"


def test_reconcile_pr_counts_default_false(monkeypatch, tmp_path):
    _memory_cache(monkeypatch)
    repo = _repo("repo")
    repo.get_pulls = lambda **kwargs: (_ for _ in ()).throw(AssertionError("PRs queried"))
    monkeypatch.setattr(github_status, "resolve_token", lambda account: ("token", "env"))
    monkeypatch.setattr(github_status, "_github_client", lambda token: _client([[repo]]))
    result = github_status.reconcile_status_for_accounts(["account"], tmp_path, per_account_budget_seconds=1)
    assert result["accounts"]["account"]["freshly_fetched"] == 1


def test_force_refresh_skips_cache_backfill(monkeypatch, tmp_path):
    cache = _memory_cache(monkeypatch)
    cache["previous"] = {"cached": {"name": "cached", "fetched_at": "2020-01-01T00:00:00+00:00", "source": "live"}}
    monkeypatch.setattr(github_status, "resolve_token", lambda account: ("token", "env"))
    monkeypatch.setattr(github_status, "_github_client", lambda token: _client([]))
    result = github_status.reconcile_status_for_accounts(["account"], tmp_path, force_refresh=True, per_account_budget_seconds=1)
    assert result["accounts"]["account"]["cache_backfilled"] == 0


def test_cache_history_bounded_to_two_snapshots(monkeypatch, tmp_path):
    monkeypatch.setattr(reconcile_cache, "CACHE_DIRECTORY", tmp_path)
    for name in ("first", "second", "third"):
        cache = reconcile_cache.begin_snapshot("account")
        reconcile_cache.merge_live_repos("account", cache, [{"name": name}])
    cache = reconcile_cache._read("account")
    assert set(cache) == {"current", "previous"}
    assert set(cache["current"]) == {"third"} and set(cache["previous"]) == {"second"}


def test_cache_never_hardcodes_freshness(monkeypatch, tmp_path):
    monkeypatch.setattr(reconcile_cache, "CACHE_DIRECTORY", tmp_path)
    cache = reconcile_cache.begin_snapshot("account")
    reconcile_cache.merge_live_repos("account", cache, [{"name": "first"}])
    cached = reconcile_cache.cached_repos(reconcile_cache._read("account"))
    assert cached[0]["fetched_at"]
    assert cached[0]["source"] == "cached"


def test_cache_file_gitignored():
    root = __import__("pathlib").Path(__file__).parents[1]
    assert ".repoman_cache/" in (root / ".gitignore").read_text(encoding="utf-8")
