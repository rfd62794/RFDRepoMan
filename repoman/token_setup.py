"""GitHub fine-grained personal-access-token setup URL generation."""
from __future__ import annotations

from urllib.parse import urlencode


TOKEN_SETUP_URL = "https://github.com/settings/personal-access-tokens/new"
DEFAULT_TOKEN_NAME = "RFDRepoMan"
DEFAULT_PERMISSIONS = {
    "contents": "write",
    "pull_requests": "write",
    "metadata": "read",
}


def generate_token_url(account_name: str, token_name: str = DEFAULT_TOKEN_NAME) -> str:
    if not account_name.strip():
        raise ValueError("account_name is required")
    return f"{TOKEN_SETUP_URL}?{urlencode({'name': token_name, 'target_name': account_name, **DEFAULT_PERMISSIONS})}"
