"""Environment-only GitHub configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass

ACCOUNTS_ENV_VAR = "RFD_REPOMAN_ACCOUNTS"
TOKEN_ENV_PREFIX = "RFD_REPOMAN_GH_TOKEN_"


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


def get_account_config(account: str) -> AccountConfig:
    if account not in configured_account_names():
        raise ValueError("Account is not configured")
    return AccountConfig(account=account, token=os.getenv(token_env_var(account)))


def configured_accounts() -> list[AccountConfig]:
    return [get_account_config(account) for account in configured_account_names()]


def safe_error(message: str) -> dict[str, str]:
    return {"error": message.replace("token", "credential")}
