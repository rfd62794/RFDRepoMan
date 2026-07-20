from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path


def print_value(label: str, value: object) -> None:
    print(f"{label}: {value}")


print_value("PATH", os.environ.get("PATH"))
print_value("GH_PATH", shutil.which("gh"))
print_value("CWD", os.getcwd())

started = time.perf_counter()
try:
    gh_status = subprocess.run(
        ["gh", "auth", "status", "--hostname", "github.com", "--active"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    print_value("GH_STATUS_RETURN_CODE", gh_status.returncode)
    print_value("GH_STATUS_STDOUT", repr(gh_status.stdout))
    print_value("GH_STATUS_STDERR", repr(gh_status.stderr))
except subprocess.TimeoutExpired as error:
    print_value("GH_STATUS_TIMEOUT", repr(error))
print_value("GH_STATUS_SECONDS", round(time.perf_counter() - started, 3))

started = time.perf_counter()
try:
    defender = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "Get-Process MsMpEng -ErrorAction SilentlyContinue | Select-Object Name,CPU,WS | ConvertTo-Json -Compress"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    print_value("DEFENDER_BEFORE", defender.stdout.strip())
except subprocess.TimeoutExpired as error:
    print_value("DEFENDER_BEFORE_TIMEOUT", repr(error))

repos = list(Path(r"C:\Github").rglob(".git"))
print_value("DISCOVERED_GIT_DIRECTORIES", len(repos))
print_value("DISCOVERY_SECONDS", round(time.perf_counter() - started, 3))

try:
    defender = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "Get-Process MsMpEng -ErrorAction SilentlyContinue | Select-Object Name,CPU,WS | ConvertTo-Json -Compress"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    print_value("DEFENDER_AFTER", defender.stdout.strip())
except subprocess.TimeoutExpired as error:
    print_value("DEFENDER_AFTER_TIMEOUT", repr(error))
