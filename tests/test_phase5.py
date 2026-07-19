from __future__ import annotations

from repoman import self_verify
from repoman.toolchain import detect_toolchain


def test_detect_rust_toolchain(tmp_path):
    (tmp_path / "Cargo.toml").write_text("[package]\nname = \"fixture\"\n")
    assert detect_toolchain(tmp_path)["toolchain"] == "rust"


def test_detect_uv_toolchain(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = \"fixture\"\n")
    (tmp_path / "uv.lock").write_text("version = 1\n")
    (tmp_path / ".python-version").write_text("3.12\n")
    result = detect_toolchain(tmp_path)
    assert result == {"toolchain": "uv", "python_version": "3.12"}


def test_detect_ambiguous_python(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = \"fixture\"\n")
    assert detect_toolchain(tmp_path)["toolchain"] == "python_ambiguous"


def test_detect_node_toolchain(tmp_path):
    (tmp_path / "package.json").write_text("{}\n")
    assert detect_toolchain(tmp_path)["toolchain"] == "node"


def test_detect_no_toolchain(tmp_path):
    assert detect_toolchain(tmp_path)["toolchain"] == "unknown"


def test_verify_floor_skips_non_uv_explicitly(monkeypatch, tmp_path):
    (tmp_path / "Cargo.toml").write_text("[package]\nname = \"fixture\"\n")
    monkeypatch.setattr(self_verify, "_run", lambda *args: (_ for _ in ()).throw(AssertionError("test command executed")))
    result = self_verify.verify_floor(tmp_path)
    assert result["status"] == "unsupported_toolchain"
    assert result["toolchain"]["toolchain"] == "rust"
    assert result["return_code"] is None
