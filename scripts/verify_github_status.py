from __future__ import annotations

from types import SimpleNamespace

from github import Github

from repoman.github_status import github_status


def main() -> None:
    clients = {
        account: SimpleNamespace(get_user=lambda account=account: Github().get_user(account))
        for account in ("rfd62794", "ConsumrBuzzy")
    }
    print(github_status(clients))


if __name__ == "__main__":
    main()
