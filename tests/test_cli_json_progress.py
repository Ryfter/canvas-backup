"""Tests for --json-progress flag in the `archive` CLI subcommand."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from canvas_download.archive import ArchiveResult


def _mock_config(tmp_path: Path) -> MagicMock:
    cfg = MagicMock()
    cfg.canvas.base_url = "https://canvas.example.com"
    cfg.canvas.token.return_value = "tok"
    cfg.archive.root = tmp_path
    cfg.archive.year = "2025"
    cfg.archive.semester = "Spring"
    cfg.archive.download_workers = 4
    return cfg


def test_json_progress_emits_complete_line(capsys, tmp_path: Path) -> None:
    """--json-progress makes the final stdout line a JSON completion event."""
    fake_path = tmp_path / "2025" / "Spring" / "TEST101"
    fake_result = ArchiveResult(archive_path=fake_path, report={})

    with (
        patch("canvas_download.cli.load_config", return_value=_mock_config(tmp_path)),
        patch("canvas_download.cli.CanvasClient"),
        patch("canvas_download.cli.CourseArchiver") as mock_cls,
    ):
        mock_cls.return_value.archive_course.return_value = fake_result
        from canvas_download.cli import main

        rc = main(["archive", "--course-id", "12345", "--json-progress"])

    assert rc == 0
    lines = [line for line in capsys.readouterr().out.strip().splitlines() if line.strip()]
    assert lines, "Expected at least the complete line on stdout"

    complete = json.loads(lines[-1])
    assert complete["type"] == "complete"
    assert complete["courseId"] == "12345"
    assert complete["archivePath"] == str(fake_path)


def test_json_progress_callback_encodes_messages_as_json(capsys, tmp_path: Path) -> None:
    """Progress messages emitted by the archiver are JSON-encoded when --json-progress is set."""
    fake_path = tmp_path / "2025" / "Spring" / "TEST101"
    fake_result = ArchiveResult(archive_path=fake_path, report={})

    def simulating_archiver(client: object, archive_config: object, progress=None) -> MagicMock:
        def do_archive(course_id: str, shell_name: str | None = None) -> ArchiveResult:
            if progress:
                progress("[Canvas] Loading course")
                progress("[Canvas] Downloading pages")
            return fake_result

        inst = MagicMock()
        inst.archive_course.side_effect = do_archive
        return inst

    with (
        patch("canvas_download.cli.load_config", return_value=_mock_config(tmp_path)),
        patch("canvas_download.cli.CanvasClient"),
        patch("canvas_download.cli.CourseArchiver", side_effect=simulating_archiver),
    ):
        from canvas_download.cli import main

        rc = main(["archive", "--course-id", "12345", "--json-progress"])

    assert rc == 0
    lines = [line for line in capsys.readouterr().out.strip().splitlines() if line.strip()]
    # 2 progress lines + 1 complete line
    assert len(lines) >= 3, f"Expected ≥3 lines, got {len(lines)}: {lines}"

    for line in lines[:-1]:
        event = json.loads(line)
        assert event["type"] == "progress", f"Expected progress, got: {event}"
        assert "message" in event

    complete = json.loads(lines[-1])
    assert complete["type"] == "complete"
    assert complete["courseId"] == "12345"
    assert complete["archivePath"] == str(fake_path)


def test_plain_mode_keeps_human_readable(capsys, tmp_path: Path) -> None:
    """Without --json-progress the output stays human-readable (original behaviour preserved)."""
    fake_path = tmp_path / "2025" / "Spring" / "TEST101"
    fake_result = ArchiveResult(archive_path=fake_path, report={})

    with (
        patch("canvas_download.cli.load_config", return_value=_mock_config(tmp_path)),
        patch("canvas_download.cli.CanvasClient"),
        patch("canvas_download.cli.CourseArchiver") as mock_cls,
    ):
        mock_cls.return_value.archive_course.return_value = fake_result
        from canvas_download.cli import main

        rc = main(["archive", "--course-id", "12345"])

    assert rc == 0
    out = capsys.readouterr().out
    assert f"Archived course 12345 to {fake_path}" in out
    # Ensure the output is NOT a JSON complete event
    for line in out.strip().splitlines():
        if line.strip():
            try:
                event = json.loads(line)
                assert event.get("type") != "complete", (
                    f"Plain mode should not emit JSON complete events, got: {line}"
                )
            except (json.JSONDecodeError, ValueError):
                pass  # Plain text — expected
