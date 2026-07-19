from __future__ import annotations

from types import SimpleNamespace

from github import Github, GithubException

from repoman.config import configured_accounts
from repoman.github_status import github_status


def main() -> None:
    accounts = configured_accounts()
    clients = {
        account.account: SimpleNamespace(get_user=lambda account=account, api=Github(account.token, retry=None): api.get_user(account.account))
        for account in accounts
    }
    print("Starting public, rate-limit-safe GitHub reconciliation")
    try:
        print(github_status(clients, include_pr_counts=False, progress=print))
    except GithubException as error:
        print({"github_verification": "unavailable", "status": error.status, "message": "GitHub public API rate limit or request failure"})


if __name__ == "__main__":
    main()
