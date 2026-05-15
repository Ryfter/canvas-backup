from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Callable

from canvas_download.json_io import write_json


@dataclass(frozen=True)
class DuplicateFile:
    path: Path
    relative_path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class DedupeResult:
    scanned: int
    duplicate_sets: int
    removed: int
    saved_bytes: int
    manifest_path: Path


def dedupe_archive_files(
    archive_path: Path,
    progress: Callable[[str], None] | None = None,
) -> DedupeResult:
    archive_path = archive_path.expanduser().resolve()
    files_root = archive_path / "files"
    manifest_path = archive_path / "manifests" / "duplicates.json"

    if not files_root.exists():
        manifest = {
            "scope": "files",
            "scanned": 0,
            "duplicate_sets": [],
            "removed": [],
            "saved_bytes": 0,
        }
        write_json(manifest_path, manifest)
        _progress(progress, "[Dedupe] No files directory found")
        return DedupeResult(scanned=0, duplicate_sets=0, removed=0, saved_bytes=0, manifest_path=manifest_path)

    candidates = [
        path
        for path in sorted(files_root.rglob("*"))
        if path.is_file() and path.name != "_canvas-files.json" and not path.name.endswith(".part")
    ]
    _progress(progress, f"[Dedupe] Checking {len(candidates)} file(s) for exact duplicates")

    by_size: dict[int, list[Path]] = {}
    for path in candidates:
        by_size.setdefault(path.stat().st_size, []).append(path)

    by_hash: dict[tuple[int, str], list[DuplicateFile]] = {}
    scanned = 0
    for size, paths in by_size.items():
        if len(paths) < 2:
            scanned += len(paths)
            continue
        for path in paths:
            digest = sha256_file(path)
            scanned += 1
            relative_path = path.relative_to(archive_path).as_posix()
            by_hash.setdefault((size, digest), []).append(
                DuplicateFile(path=path, relative_path=relative_path, size=size, sha256=digest)
            )

    duplicate_sets = []
    removed_entries = []
    saved_bytes = 0
    for (size, digest), duplicates in sorted(by_hash.items(), key=lambda item: item[0]):
        if len(duplicates) < 2:
            continue
        duplicates = sorted(duplicates, key=lambda item: (len(item.relative_path), item.relative_path.lower()))
        keep = duplicates[0]
        removed = duplicates[1:]
        for duplicate in removed:
            duplicate.path.unlink(missing_ok=True)
            saved_bytes += duplicate.size
            removed_entries.append(
                {
                    "path": duplicate.relative_path,
                    "kept_path": keep.relative_path,
                    "size": duplicate.size,
                    "sha256": duplicate.sha256,
                }
            )
            _progress(progress, f"[Dedupe] Removed duplicate: {duplicate.relative_path} -> {keep.relative_path}")
        duplicate_sets.append(
            {
                "sha256": digest,
                "size": size,
                "kept": keep.relative_path,
                "removed": [duplicate.relative_path for duplicate in removed],
            }
        )

    manifest = {
        "scope": "files",
        "scanned": scanned,
        "duplicate_set_count": len(duplicate_sets),
        "removed_count": len(removed_entries),
        "saved_bytes": saved_bytes,
        "duplicate_sets": duplicate_sets,
        "removed": removed_entries,
    }
    write_json(manifest_path, manifest)
    _progress(
        progress,
        f"[Dedupe] Finished: {len(duplicate_sets)} duplicate set(s), "
        f"{len(removed_entries)} file(s) removed, {format_bytes(saved_bytes)} saved",
    )
    return DedupeResult(
        scanned=scanned,
        duplicate_sets=len(duplicate_sets),
        removed=len(removed_entries),
        saved_bytes=saved_bytes,
        manifest_path=manifest_path,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}" if unit != "B" else f"{int(amount)} B"
        amount /= 1024
    return f"{value} B"


def _progress(progress: Callable[[str], None] | None, message: str) -> None:
    if progress:
        progress(message)
