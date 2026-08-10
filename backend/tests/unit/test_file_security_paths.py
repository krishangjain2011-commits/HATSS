"""Tests for scan-path guardrails that run on every platform."""

from pathlib import Path

import pytest

from app.services.file_security import UnsafeScanDirectoryError, validate_scan_directory


def test_scan_directory_allows_a_specific_existing_directory(tmp_path: Path) -> None:
    selected_directory = tmp_path / "Documents"
    selected_directory.mkdir()

    assert validate_scan_directory(str(selected_directory)) == selected_directory.resolve()


def test_scan_directory_rejects_a_relative_path() -> None:
    with pytest.raises(UnsafeScanDirectoryError, match="absolute"):
        validate_scan_directory("Documents")


def test_scan_directory_rejects_a_drive_or_filesystem_root() -> None:
    with pytest.raises(UnsafeScanDirectoryError, match="drive root"):
        validate_scan_directory(Path.cwd().anchor)


def test_scan_directory_rejects_a_protected_system_directory(tmp_path: Path) -> None:
    system_directory = tmp_path / "Windows"
    system_directory.mkdir()
    selected_directory = system_directory / "System32"
    selected_directory.mkdir()

    with pytest.raises(UnsafeScanDirectoryError, match="Windows and program"):
        validate_scan_directory(str(selected_directory), protected_roots=[system_directory])
