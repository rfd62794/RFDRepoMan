from __future__ import annotations

from types import SimpleNamespace

from github import Github, GithubException

from repoman.github_status import github_status


def main() -> None:
    clients = {
        account: SimpleNamespace(get_user=lambda account=account: Github(retry=None).get_user(account))
        for account in ("rfd62794", "ConsumrBuzzy")
    }
    print("Starting public, rate-limit-safe GitHub reconciliation")
    try:
        print(github_status(clients, include_pr_counts=False, progress=print))
    except GithubException as error:
        print({"github_verification": "unavailable", "status": error.status, "message": "GitHub public API rate limit or request failure"})


if __name__ == "__main__":
    main()
