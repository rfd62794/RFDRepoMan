from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from repoman.git_actions import merge


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory)
        state = repo / "docs" / "state"
        state.mkdir(parents=True)
        (state / "current.md").write_text("require_ci_pass: true\n", encoding="utf-8")
        with patch("repoman.git_actions._git", return_value=""):
            print(merge(repo, "topic", confirmed=True, ci_status="failure"))
            print(merge(repo, "topic", confirmed=True, ci_status="failure", override_policy=True, override_reason="manual simulated CI exception"))


if __name__ == "__main__":
    main()
