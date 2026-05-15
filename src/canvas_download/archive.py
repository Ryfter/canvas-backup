from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from canvas_download.canvas_client import CanvasApiError, CanvasClient
from canvas_download.config import ArchiveConfig
from canvas_download.filesystem import ensure_within, numbered_name, safe_name
from canvas_download.json_io import write_json, write_text


@dataclass(frozen=True)
class ArchiveResult:
    archive_path: Path
    report: dict[str, Any]


@dataclass(frozen=True)
class FileDownloadTask:
    file_id: Any
    url: str
    target_file: Path
    relative_label: str
    size: int | None = None


class CourseArchiver:
    def __init__(
        self,
        client: CanvasClient,
        archive_config: ArchiveConfig,
        progress: Callable[[str], None] | None = None,
    ) -> None:
        self.client = client
        self.archive_config = archive_config
        self.progress = progress

    def archive_course(self, course_id: int | str, shell_name: str | None = None) -> ArchiveResult:
        self._progress(f"[Canvas] Loading course {course_id}")
        course = self.client.get_course(course_id)
        course_name = shell_name or course.get("name") or course.get("course_code") or f"course-{course_id}"
        root = self.archive_config.root
        archive_path = root / safe_name(self.archive_config.year) / safe_name(self.archive_config.semester) / safe_name(course_name)
        ensure_within(root, archive_path)
        archive_path.mkdir(parents=True, exist_ok=True)
        self._progress(f"[Canvas] Archiving to {archive_path}")

        report: dict[str, Any] = {
            "course_id": course_id,
            "course_name": course_name,
            "archive_path": str(archive_path),
            "counts": {},
            "warnings": [],
            "failures": [],
        }

        manifests = archive_path / "manifests"
        write_json(manifests / "course.json", course)

        folders = self._archive_files(course_id, archive_path, report)
        modules = self._archive_modules(course_id, archive_path, report)
        pages = self._archive_pages(course_id, archive_path, report)
        assignments = self._archive_assignments(course_id, archive_path, report)
        quizzes = self._archive_quizzes(course_id, archive_path, report)
        discussions = self._archive_discussions(course_id, archive_path, report)
        due_dates = self._archive_due_dates(course_id, archive_path, assignments, report)

        write_json(
            manifests / "content-map.json",
            {
                "course": course,
                "folders": folders,
                "modules": modules,
                "pages": pages,
                "assignments": assignments,
                "quizzes": quizzes,
                "discussions": discussions,
                "due_dates": due_dates,
            },
        )
        write_json(manifests / "download-report.json", report)
        self._progress(f"[Canvas] Finished {course_name}")
        return ArchiveResult(archive_path=archive_path, report=report)

    def _archive_files(self, course_id: int | str, archive_path: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
        self._progress("[Canvas] Loading file folders")
        folders = self.client.list_folders(course_id)
        write_json(archive_path / "manifests" / "folders.json", folders)
        tasks: list[FileDownloadTask] = []

        folder_lookup = {folder.get("id"): folder for folder in folders}
        for folder_index, folder in enumerate(folders, start=1):
            folder_path = self._folder_path(folder, folder_lookup)
            folder_label = folder_path.as_posix() or "course files"
            self._progress(f"[Canvas] Folder {folder_index}/{len(folders)}: {folder_label}")
            target_dir = ensure_within(archive_path, archive_path / "files" / folder_path)
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                files = self.client.list_files(folder["id"])
            except CanvasApiError as exc:
                report["failures"].append({"type": "folder_files", "folder_id": folder.get("id"), "error": str(exc)})
                continue

            write_json(target_dir / "_canvas-files.json", files)
            for folder_file_index, file_record in enumerate(files, start=1):
                filename = safe_name(file_record.get("display_name") or file_record.get("filename"), fallback=f"file-{file_record.get('id')}")
                target_file = ensure_within(archive_path, target_dir / filename)
                url = file_record.get("url")
                if not url:
                    report["warnings"].append({"type": "file_missing_url", "file_id": file_record.get("id")})
                    continue
                tasks.append(
                    FileDownloadTask(
                        file_id=file_record.get("id"),
                        url=url,
                        target_file=target_file,
                        relative_label=f"{folder_label}/{filename}",
                        size=file_record.get("size") if isinstance(file_record.get("size"), int) else None,
                    )
                )

        file_count = self._download_files_concurrently(tasks, report)

        report["counts"]["folders"] = len(folders)
        report["counts"]["queued_files"] = len(tasks)
        report["counts"]["downloaded_files"] = file_count
        return folders

    def _download_files_concurrently(self, tasks: list[FileDownloadTask], report: dict[str, Any]) -> int:
        if not tasks:
            self._progress("[Canvas] No files to download")
            return 0

        workers = max(1, self.archive_config.download_workers)
        self._progress(f"[Canvas] Downloading {len(tasks)} file(s) with {workers} worker(s)")
        downloaded = 0
        total_bytes = 0
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(self.client.download_file, task.url, str(task.target_file)): task
                for task in tasks
            }
            for completed, future in enumerate(as_completed(future_map), start=1):
                task = future_map[future]
                try:
                    future.result()
                    downloaded += 1
                    total_bytes += task.target_file.stat().st_size if task.target_file.exists() else task.size or 0
                    self._progress(
                        f"[Canvas {completed}/{len(tasks)}] downloaded: "
                        f"{task.relative_label} ({format_bytes(total_bytes)} total)"
                    )
                except Exception as exc:
                    report["failures"].append({"type": "file_download", "file_id": task.file_id, "error": str(exc)})
                    self._progress(f"[Canvas {completed}/{len(tasks)}] failed: {task.relative_label}")
        return downloaded

    def _archive_modules(self, course_id: int | str, archive_path: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
        self._progress("[Canvas] Loading modules")
        modules = self.client.list_modules(course_id)
        module_root = archive_path / "modules"
        index_lines = [f"# Modules for course {course_id}", ""]
        enriched_modules: list[dict[str, Any]] = []

        for position, module in enumerate(modules, start=1):
            module_name = module.get("name") or f"module-{module.get('id')}"
            self._progress(f"[Canvas] Module {position}/{len(modules)}: {module_name}")
            module_dir = module_root / numbered_name(position, module_name)
            module_dir.mkdir(parents=True, exist_ok=True)
            items = self.client.list_module_items(course_id, module["id"])
            enriched = {**module, "items": items}
            enriched_modules.append(enriched)
            write_json(module_dir / "module.json", module)
            write_json(module_dir / "items.json", items)
            write_text(module_dir / "README.md", _module_markdown(module_name, items))
            index_lines.append(f"{position}. {module_name} ({len(items)} items)")

        write_text(module_root / "00-module-index.md", "\n".join(index_lines) + "\n")
        write_json(archive_path / "manifests" / "modules.json", enriched_modules)
        report["counts"]["modules"] = len(modules)
        report["counts"]["module_items"] = sum(len(module.get("items", [])) for module in enriched_modules)
        return enriched_modules

    def _archive_pages(self, course_id: int | str, archive_path: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
        self._progress("[Canvas] Loading pages")
        pages = self.client.list_pages(course_id)
        page_root = archive_path / "pages"
        detailed_pages = []
        for index, page in enumerate(pages, start=1):
            page_url = page.get("url")
            if not page_url:
                continue
            self._progress(f"[Canvas] Page {index}/{len(pages)}: {page.get('title') or page_url}")
            try:
                detail = self.client.get_page(course_id, page_url)
            except CanvasApiError as exc:
                report["failures"].append({"type": "page", "page_url": page_url, "error": str(exc)})
                continue
            name = safe_name(detail.get("title") or page_url)
            write_json(page_root / f"{name}.json", detail)
            write_text(page_root / f"{name}.html", detail.get("body") or "")
            detailed_pages.append(detail)

        write_json(archive_path / "manifests" / "pages.json", detailed_pages)
        report["counts"]["pages"] = len(detailed_pages)
        return detailed_pages

    def _archive_assignments(self, course_id: int | str, archive_path: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
        self._progress("[Canvas] Loading assignments")
        assignments = self.client.list_assignments(course_id)
        assignment_root = archive_path / "assignments"
        for index, assignment in enumerate(assignments, start=1):
            self._progress(f"[Canvas] Assignment {index}/{len(assignments)}: {assignment.get('name') or assignment.get('id')}")
            name = safe_name(assignment.get("name"), fallback=f"assignment-{assignment.get('id')}")
            write_json(assignment_root / f"{name}.json", assignment)
            write_text(assignment_root / f"{name}.html", assignment.get("description") or "")

        write_json(archive_path / "manifests" / "assignments.json", assignments)
        report["counts"]["assignments"] = len(assignments)
        return assignments

    def _archive_quizzes(self, course_id: int | str, archive_path: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
        self._progress("[Canvas] Loading quizzes")
        quizzes = self.client.list_quizzes(course_id)
        quiz_root = archive_path / "quizzes"
        for index, quiz in enumerate(quizzes, start=1):
            self._progress(f"[Canvas] Quiz {index}/{len(quizzes)}: {quiz.get('title') or quiz.get('id')}")
            name = safe_name(quiz.get("title"), fallback=f"quiz-{quiz.get('id')}")
            write_json(quiz_root / f"{name}.json", quiz)
        write_json(archive_path / "manifests" / "quizzes.json", quizzes)
        report["counts"]["quizzes"] = len(quizzes)
        return quizzes

    def _archive_discussions(self, course_id: int | str, archive_path: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
        self._progress("[Canvas] Loading discussions")
        discussions = self.client.list_discussion_topics(course_id)
        discussion_root = archive_path / "discussions"
        for index, topic in enumerate(discussions, start=1):
            self._progress(f"[Canvas] Discussion {index}/{len(discussions)}: {topic.get('title') or topic.get('id')}")
            name = safe_name(topic.get("title"), fallback=f"discussion-{topic.get('id')}")
            write_json(discussion_root / f"{name}.json", topic)
            write_text(discussion_root / f"{name}.html", topic.get("message") or "")
        write_json(archive_path / "manifests" / "discussions.json", discussions)
        report["counts"]["discussions"] = len(discussions)
        return discussions

    def _archive_due_dates(
        self,
        course_id: int | str,
        archive_path: Path,
        assignments: list[dict[str, Any]],
        report: dict[str, Any],
    ) -> dict[str, Any]:
        due_dates: dict[str, Any] = {"effective_due_dates": {}, "assignments": []}
        try:
            due_dates["effective_due_dates"] = self.client.effective_due_dates(course_id)
        except CanvasApiError as exc:
            report["warnings"].append({"type": "effective_due_dates", "error": str(exc)})

        for assignment in assignments:
            due_dates["assignments"].append(
                {
                    "id": assignment.get("id"),
                    "name": assignment.get("name"),
                    "due_at": assignment.get("due_at"),
                    "unlock_at": assignment.get("unlock_at"),
                    "lock_at": assignment.get("lock_at"),
                    "all_dates": assignment.get("all_dates", []),
                }
            )

        manifest_path = archive_path / "manifests"
        write_json(manifest_path / "due-dates.json", due_dates)
        self._write_due_dates_csv(manifest_path / "due-dates.csv", due_dates["assignments"])
        report["counts"]["due_date_rows"] = len(due_dates["assignments"])
        return due_dates

    def _write_due_dates_csv(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["id", "name", "due_at", "unlock_at", "lock_at", "all_dates"])
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        **row,
                        "all_dates": row.get("all_dates") if isinstance(row.get("all_dates"), str) else str(row.get("all_dates", [])),
                    }
                )

    def _folder_path(self, folder: dict[str, Any], lookup: dict[Any, dict[str, Any]]) -> Path:
        parts: list[str] = []
        current: dict[str, Any] | None = folder
        seen: set[Any] = set()
        while current:
            folder_id = current.get("id")
            if folder_id in seen:
                break
            seen.add(folder_id)
            name = current.get("name") or current.get("full_name") or f"folder-{folder_id}"
            if name != "course files":
                parts.append(safe_name(name))
            parent_id = current.get("parent_folder_id")
            current = lookup.get(parent_id)
        return Path(*reversed(parts)) if parts else Path()

    def _progress(self, message: str) -> None:
        if self.progress:
            self.progress(message)


def _module_markdown(module_name: str, items: list[dict[str, Any]]) -> str:
    lines = [f"# {module_name}", ""]
    for index, item in enumerate(items, start=1):
        title = item.get("title") or item.get("page_url") or f"item-{item.get('id')}"
        item_type = item.get("type") or "Item"
        indent = "  " if item.get("indent") else ""
        lines.append(f"{index}. {indent}{title} [{item_type}]")
    return "\n".join(lines) + "\n"


def format_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}" if unit != "B" else f"{int(amount)} B"
        amount /= 1024
    return f"{value} B"
