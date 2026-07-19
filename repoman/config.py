"""Environment-only GitHub configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass

ACCOUNT_ENV_VARS = {
    "rfd62794": "RFD_REPOMAN_GH_TOKEN_RFD62794",
    "ConsumrBuzzy": "RFD_REPOMAN_GH_TOKEN_CONSUMRBUZZY",
}


@dataclass(frozen=True)
class AccountConfig:
    account: str
    token: str | None


def get_account_config(account: str) -> AccountConfig:
    if account not in ACCOUNT_ENV_VARS:
        raise ValueError("Unknown GitHub account")
    return AccountConfig(account=account, token=os.getenv(ACCOUNT_ENV_VARS[account]))


def configured_accounts() -> list[AccountConfig]:
    return [get_account_config(account) for account in ACCOUNT_ENV_VARS]


def safe_error(message: str) -> dict[str, str]:
    return {"error": message.replace("token", "credential")}
