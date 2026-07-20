# GitHub Token Setup

`generate_token_setup_url` creates a GitHub fine-grained personal-access-token setup URL for an operator-supplied account. It makes no network request and does not store or return credentials.

The URL pre-fills these permissions:

- `contents=write` for the named repository content actions.
- `pull_requests=write` for pull-request creation and merge actions.
- `metadata=read` for repository metadata reads.

Open the generated URL while signed into the intended GitHub account. Review the owner, repository selection, expiration, and permissions before creating a token. Store the resulting credential only in the operator's local environment; do not add it to source control.

Example using a placeholder account:

```text
https://github.com/settings/personal-access-tokens/new?name=RFDRepoMan&target_name=example-account&contents=write&pull_requests=write&metadata=read
```
