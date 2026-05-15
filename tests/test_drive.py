from pathlib import Path

from canvas_download.drive import archive_drive_parts, drive_query_literal


def test_archive_drive_parts_uses_year_semester_shell() -> None:
    path = Path("D:/CanvasArchive/2026/Spring/ITM370")

    assert archive_drive_parts(path) == ["2026", "Spring", "ITM370"]


def test_drive_query_literal_escapes_quotes_and_backslashes() -> None:
    assert drive_query_literal("Bob's \\ Folder") == "'Bob\\'s \\\\ Folder'"
