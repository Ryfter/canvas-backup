from pathlib import Path

from canvas_download.archive import CourseArchiver
from canvas_download.config import ArchiveConfig


class FakeCanvasClient:
    def get_course(self, course_id: str) -> dict:
        return {"id": course_id, "name": "ENG 101 Combined Sections"}

    def list_folders(self, course_id: str) -> list[dict]:
        return [
            {"id": 1, "name": "course files", "parent_folder_id": None},
            {"id": 2, "name": "Week 1", "parent_folder_id": 1},
        ]

    def list_files(self, folder_id: int) -> list[dict]:
        if folder_id == 2:
            return [
                {"id": 10, "display_name": "Prompt.pdf", "url": "https://canvas/files/10"},
                {"id": 11, "display_name": "Prompt Copy.pdf", "url": "https://canvas/files/11"},
            ]
        return []

    def download_file(self, url: str, target_path: str) -> None:
        Path(target_path).write_bytes(b"file contents")

    def list_modules(self, course_id: str) -> list[dict]:
        return [{"id": 100, "name": "Start Here"}]

    def list_module_items(self, course_id: str, module_id: int) -> list[dict]:
        return [{"id": 101, "title": "Read the Syllabus", "type": "Page", "indent": 0}]

    def list_pages(self, course_id: str) -> list[dict]:
        return [{"url": "read-the-syllabus", "title": "Read the Syllabus"}]

    def get_page(self, course_id: str, page_url: str) -> dict:
        return {"url": page_url, "title": "Read the Syllabus", "body": "<p>Hello</p>"}

    def list_assignments(self, course_id: str) -> list[dict]:
        return [
            {
                "id": 200,
                "name": "Essay 1",
                "description": "<p>Write.</p>",
                "due_at": "2026-02-01T23:59:00Z",
                "unlock_at": None,
                "lock_at": None,
                "all_dates": [],
            }
        ]

    def effective_due_dates(self, course_id: str) -> dict:
        return {"200": {"due_at": "2026-02-01T23:59:00Z"}}

    def list_quizzes(self, course_id: str) -> list[dict]:
        return [{"id": 300, "title": "Quiz 1"}]

    def list_discussion_topics(self, course_id: str) -> list[dict]:
        return [{"id": 400, "title": "Introductions", "message": "<p>Say hello.</p>"}]


def test_archive_course_writes_expected_layout(tmp_path: Path) -> None:
    messages: list[str] = []
    archiver = CourseArchiver(
        FakeCanvasClient(),
        ArchiveConfig(root=tmp_path, year="2026", semester="Spring"),
        progress=messages.append,
    )

    result = archiver.archive_course("123")

    course_root = tmp_path / "2026" / "Spring" / "ENG 101 Combined Sections"
    assert result.archive_path == course_root
    assert (course_root / "files" / "Week 1" / "Prompt.pdf").read_bytes() == b"file contents"
    assert not (course_root / "files" / "Week 1" / "Prompt Copy.pdf").exists()
    assert (course_root / "modules" / "01-Start Here" / "README.md").exists()
    assert (course_root / "pages" / "Read the Syllabus.html").read_text(encoding="utf-8") == "<p>Hello</p>"
    assert (course_root / "assignments" / "Essay 1.json").exists()
    assert (course_root / "manifests" / "due-dates.csv").exists()
    assert (course_root / "manifests" / "duplicates.json").exists()
    assert result.report["counts"]["modules"] == 1
    assert result.report["counts"]["duplicate_files_removed"] == 1
    assert any("[Canvas 1/2] downloaded" in message for message in messages)
    assert any("[Dedupe] Removed duplicate" in message for message in messages)
    assert any("Module 1/1" in message for message in messages)
