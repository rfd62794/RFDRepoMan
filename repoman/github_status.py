"""Read-only GitHub queries and local/remote reconciliation."""
from __future__ import annotations

from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Any, Callable

from github import Github

from repoman.config import configured_accounts, resolve_token
from repoman.discover import discover_repos


def _repo_name(path: str) -> str:
    return Path(path).name.lower()


def reconcile_repos(local_repos: list[str], remote_repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    local = {_repo_name(repo): repo for repo in local_repos}
    remote = {str(repo["name"]).lower(): repo for repo in remote_repos}
    results: list[dict[str, Any]] = []
    for name in sorted(local.keys() | remote.keys()):
        results.append({"name": name, "location": "both" if name in local and name in remote else "local-only" if name in local else "remote-only", "local_path": local.get(name), "remote": remote.get(name)})
    return results


def list_account_repos(client: Any, include_pr_counts: bool = True) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for repo in client.get_user().get_repos():
        results.append({
            "name": repo.name,
            "full_name": repo.full_name,
            "visibility": getattr(repo, "visibility", "private"),
            "stars": repo.stargazers_count,
            "open_issues": repo.open_issues_count,
            "open_prs": repo.get_pulls(state="open").totalCount if include_pr_counts else "unavailable: public rate-limit-safe scan",
            "default_branch": repo.default_branch,
        })
    return results


def github_status(clients: dict[str, Any], root: str | None = None, include_pr_counts: bool = True, progress: Any = None) -> dict[str, Any]:
    local = discover_repos(root)
    accounts: dict[str, list[dict[str, Any]]] = {}
    for account, client in clients.items():
        if progress:
            progress(f"Scanning GitHub account: {account}")
        accounts[account] = reconcile_repos(local, list_account_repos(client, include_pr_counts))
        if progress:
            progress(f"Completed GitHub account: {account} ({len(accounts[account])} reconciled repositories)")
    return {"accounts": accounts, "configured_accounts": [item.account for item in configured_accounts()]}


NETWORK_TIMEOUT_SECONDS = 15


def _within_timeout(operation: Callable[[], Any], timeout: float = NETWORK_TIMEOUT_SECONDS) -> tuple[bool, Any]:
    results: Queue[tuple[bool, Any]] = Queue(maxsize=1)

    def run() -> None:
        try:
            results.put((True, operation()))
        except Exception as error:
            results.put((False, error))

    thread = Thread(target=run, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return False, TimeoutError("GitHub reconciliation timed out")
    return results.get()


def _github_client(token: str) -> Github:
    return Github(token, timeout=NETWORK_TIMEOUT_SECONDS, retry=None)


def reconcile_status_for_accounts(account_names: list[str], root: str | Path | None = None, include_pr_counts: bool = True) -> dict[str, Any]:
    accounts: dict[str, Any] = {}
    for account_name in account_names:
        token, _ = resolve_token(account_name)
        if not token:
            accounts[account_name] = {"error": "no_credential_available", "account": account_name}
            continue
        completed, result = _within_timeout(lambda: github_status({account_name: _github_client(token)}, root, include_pr_counts), NETWORK_TIMEOUT_SECONDS)
        if not completed:
            accounts[account_name] = {"error": "timeout" if isinstance(result, TimeoutError) else "reconciliation_failed", "account": account_name, "message": str(result)}
            continue
        accounts[account_name] = result["accounts"][account_name]
    return {"accounts": accounts, "configured_accounts": account_names}


def list_prs(repo: Any, state: str = "open") -> list[dict[str, Any]]:
    return [{"number": pr.number, "title": pr.title, "state": pr.state, "merged": pr.merged, "head": pr.head.ref, "base": pr.base.ref} for pr in repo.get_pulls(state=state)]


def list_forks(repo: Any) -> list[dict[str, str]]:
    return [{"full_name": fork.full_name, "owner": fork.owner.login} for fork in repo.get_forks()]


def list_remote_branches(repo: Any) -> list[str]:
    return [branch.name for branch in repo.get_branches()]
