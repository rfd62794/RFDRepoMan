from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from repoman.token_setup import DEFAULT_PERMISSIONS, TOKEN_SETUP_URL, generate_token_url


def test_generates_correct_base_url():
    assert generate_token_url("example-account").startswith(TOKEN_SETUP_URL)


def test_includes_account_and_default_scopes():
    parameters = parse_qs(urlparse(generate_token_url("example-account")).query)
    assert parameters["target_name"] == ["example-account"]
    assert parameters["name"] == ["RFDRepoMan"]
    for permission, value in DEFAULT_PERMISSIONS.items():
        assert parameters[permission] == [value]


def test_url_is_valid_query_string():
    url = generate_token_url("account with spaces", "RepoMan Token")
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.netloc == "github.com"
    assert parse_qs(parsed.query)["target_name"] == ["account with spaces"]
