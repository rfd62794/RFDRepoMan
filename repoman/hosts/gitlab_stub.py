"""Unimplemented GitLab status interface."""
from __future__ import annotations

class GitLabStatus:
    def list_account_repos(self, client: object) -> list[dict[str, object]]:
        raise NotImplementedError
    def list_prs(self, repo: object, state: str = "open") -> list[dict[str, object]]:
        raise NotImplementedError
    def list_forks(self, repo: object) -> list[dict[str, object]]:
        raise NotImplementedError
    def list_remote_branches(self, repo: object) -> list[str]:
        raise NotImplementedError
