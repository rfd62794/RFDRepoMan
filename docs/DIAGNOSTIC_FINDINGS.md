# Phase 11 Diagnostic Findings

## Scope Limitation

The first run used the configured stdio-equivalent command and explicit MCP environment values. It was not performed inside the already-running Claude Desktop stdio process. The second run used the normal terminal command from the same repository directory.

## Configured Stdio-Equivalent Launch

Command:

```powershell
$env:RFD_REPOMAN_ROOT='C:\Github'
$env:RFD_REPOMAN_ACCOUNTS='rfd62794,ConsumrBuzzy'
$env:RFD_REPOMAN_ALLOW_GH_FALLBACK='true'
& 'C:\Users\cheat\.local\bin\uv.exe' --directory 'C:\Github\RFDRepoMan' run python scripts\diagnose_subprocess_env.py
```

Raw observations:

```text
PATH: identical to normal-terminal run; includes C:\Program Files\GitHub CLI\ and C:\Users\cheat\.local\bin
GH_PATH: C:\Program Files\GitHub CLI\gh.EXE
CWD: C:\Github\RFDRepoMan
GH_STATUS_RETURN_CODE: 0
GH_STATUS_STDOUT: active account rfd62794; token scopes: gist, read:org, repo, workflow
GH_STATUS_STDERR: ''
GH_STATUS_SECONDS: 0.516
DEFENDER_BEFORE: {"Name":"MsMpEng","CPU":null,"WS":432807936}
DISCOVERED_GIT_DIRECTORIES: 40
DISCOVERY_SECONDS: 6.72
DEFENDER_AFTER: {"Name":"MsMpEng","CPU":null,"WS":430301184}
```

## Normal Terminal Launch

Command:

```powershell
uv run python scripts\diagnose_subprocess_env.py
```

Raw observations:

```text
PATH: identical to configured-stdio-equivalent run; includes C:\Program Files\GitHub CLI\ and C:\Users\cheat\.local\bin
GH_PATH: C:\Program Files\GitHub CLI\gh.EXE
CWD: C:\Github\RFDRepoMan
GH_STATUS_RETURN_CODE: 0
GH_STATUS_STDOUT: active account rfd62794; token scopes: gist, read:org, repo, workflow
GH_STATUS_STDERR: ''
GH_STATUS_SECONDS: 0.372
DEFENDER_BEFORE: {"Name":"MsMpEng","CPU":null,"WS":414756864}
DISCOVERED_GIT_DIRECTORIES: 40
DISCOVERY_SECONDS: 6.598
DEFENDER_AFTER: {"Name":"MsMpEng","CPU":null,"WS":421474304}
```

## Factual Comparison

- The observed `PATH`, `gh` resolution, working directory, active GitHub CLI account, and successful `gh auth status` result were the same in both launches.
- `gh auth status` completed in under one second in both launches.
- The real `C:\Github` walk found 40 `.git` directories and took 6.72 seconds in the configured-stdio-equivalent launch and 6.598 seconds in the normal terminal launch.
- The Defender process was visible in both snapshots, but its reported CPU value was `null`; this measurement does not establish Defender CPU use during discovery.
- These equivalent-launch measurements do not reproduce the live MCP credential failure. They also show that discovery consumes most of the 8-second request timeout in both measured contexts. The root cause inside the already-running Claude Desktop stdio process remains unconfirmed.
