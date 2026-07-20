"""Environment-only GitHub configuration."""
from __future__ import annotations

import logging
import os
import re
import subprocess
from dataclasses import dataclass

ACCOUNTS_ENV_VAR = "RFD_REPOMAN_ACCOUNTS"
TOKEN_ENV_PREFIX = "RFD_REPOMAN_GH_TOKEN_"
GH_FALLBACK_ENV_VAR = "RFD_REPOMAN_ALLOW_GH_FALLBACK"
GH_SUBPROCESS_TIMEOUT_SECONDS = 5
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class AccountConfig:
    account: str
    token: str | None


def token_env_var(account: str) -> str:
    normalized = "".join(character if character.isalnum() else "_" for character in account.upper())
    if not normalized:
        raise ValueError("GitHub account name is required")
    return f"{TOKEN_ENV_PREFIX}{normalized}"


def configured_account_names() -> list[str]:
    raw_accounts = os.getenv(ACCOUNTS_ENV_VAR, "")
    return [account.strip() for account in raw_accounts.split(",") if account.strip()]


def _gh(command: list[str], timeout: float = GH_SUBPROCESS_TIMEOUT_SECONDS) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 1, "", "")


def _active_gh_account() -> str | None:
    result = _gh(["gh", "auth", "status", "--hostname", "github.com", "--active"], GH_SUBPROCESS_TIMEOUT_SECONDS)
    match = re.search(r"account\s+([^\s(]+)", f"{result.stdout}\n{result.stderr}", re.IGNORECASE)
    return match.group(1) if result.returncode == 0 and match else None


def resolve_token(account_name: str) -> tuple[str | None, str]:
    token = os.getenv(token_env_var(account_name))
    if token:
        return token, "env"
    if os.getenv(GH_FALLBACK_ENV_VAR, "").lower() != "true":
        return None, "none"
    active_account = _active_gh_account()
    if active_account is None:
        return None, "none"
    if active_account != account_name:
        return None, "gh_account_mismatch"
    result = _gh(["gh", "auth", "token", "--hostname", "github.com"], GH_SUBPROCESS_TIMEOUT_SECONDS)
    token = result.stdout.strip() if result.returncode == 0 else ""
    if not token:
        return None, "none"
    LOGGER.warning("Using explicit gh CLI credential fallback for account %s; credential scope may exceed RepoMan's declared minimum.", account_name)
    return token, "gh_fallback"


def get_account_config(account: str) -> AccountConfig:
    if account not in configured_account_names():
        raise ValueError("Account is not configured")
    token, _ = resolve_token(account)
    return AccountConfig(account=account, token=token)


def configured_accounts() -> list[AccountConfig]:
    return [get_account_config(account) for account in configured_account_names()]


def safe_error(message: str) -> dict[str, str]:
    return {"error": message.replace("token", "credential")}
