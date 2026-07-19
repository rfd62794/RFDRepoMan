"""MCP server exposing only named, scoped RepoMan tools."""
from __future__ import annotations

from fastmcp import FastMCP

from repoman.git_actions import fetch, push
from repoman.github_actions import create_pr
from repoman.status import repo_status

mcp = FastMCP("RFDRepoMan")

@mcp.tool(name="repoman_fetch")
def repoman_fetch(repo: str, remote: str = "origin") -> dict[str, str]:
    return fetch(repo, remote)

@mcp.tool(name="repoman_status")
def repoman_status(repo: str, remote: str = "origin") -> dict[str, object]:
    return repo_status(repo, remote)

@mcp.tool(name="repoman_push")
def repoman_push(repo: str, remote: str = "origin", branch: str = "main", confirmed: bool = False) -> dict[str, str]:
    return push(repo, remote, branch, confirmed)

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
