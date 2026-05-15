from pathlib import Path

from canvas_download.drive import DriveSyncer, archive_drive_parts, drive_query_literal


class FakeFilesResource:
    def list(self, **kwargs):
        return self

    def execute(self):
        return {"files": [{"id": "abc", "name": "Folder"}]}


class FakeDriveService:
    def files(self):
        return FakeFilesResource()


def test_archive_drive_parts_uses_year_semester_shell() -> None:
    path = Path("D:/CanvasArchive/2026/Spring/ITM370")

    assert archive_drive_parts(path) == ["2026", "Spring", "ITM370"]


def test_drive_query_literal_escapes_quotes_and_backslashes() -> None:
    assert drive_query_literal("Bob's \\ Folder") == "'Bob\\'s \\\\ Folder'"


def test_drive_find_query_returns_first_file() -> None:
    syncer = DriveSyncer(FakeDriveService())

    assert syncer._find_by_query("name = 'Folder'") == {"id": "abc", "name": "Folder"}
