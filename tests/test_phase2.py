from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from repoman import config, discover


PROJECT_ROOT = Path(__file__).parents[1]


def test_config_no_hardcoded_account_names():
    source = inspect.getsource(config).lower()
    assert "rfd62794" not in source
    assert "consumrbuzzy" not in source


def test_discover_requires_root_env_var(monkeypatch):
    monkeypatch.delenv(discover.ROOT_ENV_VAR, raising=False)
    with pytest.raises(RuntimeError, match=discover.ROOT_ENV_VAR):
        discover.discover_repos()


def test_env_example_documents_all_required_vars():
    entries = {
        line.split("=", 1)[0]
        for line in (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    assert {config.ACCOUNTS_ENV_VAR, config.TOKEN_ENV_PREFIX + "EXAMPLE_ACCOUNT", discover.ROOT_ENV_VAR} <= entries
