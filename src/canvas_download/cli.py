from __future__ import annotations

import argparse
from pathlib import Path
import sys

from dotenv import load_dotenv

from canvas_download.archive import CourseArchiver
from canvas_download.canvas_client import CanvasClient
from canvas_download.config import ArchiveConfig, load_config
from canvas_download.course_selection import CourseArchiveTarget, parse_number_selection, select_recent_courses
from canvas_download.drive import DriveSyncer, build_drive_service


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="canvas-backup")
    parser.add_argument("--config", type=Path, help="Path to a TOML config file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("courses", help="List Canvas courses visible to the token.")

    archive = subparsers.add_parser("archive", help="Archive a Canvas course shell locally.")
    archive.add_argument("--course-id", required=True, help="Canvas course ID to archive.")
    archive.add_argument("--year", help="Archive year folder override.")
    archive.add_argument("--semester", help="Archive semester folder override.")
    archive.add_argument("--root", type=Path, help="Archive root override.")
    archive.add_argument("--shell-name", help="Folder name override for combined-section shells.")

    sync_drive = subparsers.add_parser("sync-drive", help="Mirror a local archive folder into Google Drive.")
    sync_drive.add_argument("--archive", required=True, type=Path, help="Local archive folder to upload.")

    archive_recent = subparsers.add_parser("archive-recent", help="Archive recent Canvas course shells in bulk.")
    archive_recent.add_argument("--years", type=int, default=4, help="Number of prior years to include. Default: 4.")
    archive_recent.add_argument("--since-year", type=int, help="Override the computed starting year.")
    archive_recent.add_argument("--root", type=Path, help="Archive root override.")
    archive_recent.add_argument("--sync-drive", action="store_true", help="Sync each completed local archive to Google Drive.")
    archive_recent.add_argument("--choose", action="store_true", help="Interactively choose which selected shells to archive.")
    archive_recent.add_argument("--dry-run", action="store_true", help="Show selected courses without downloading.")
    archive_recent.add_argument("--limit", type=int, help="Archive at most this many selected courses.")

    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)

        if args.command == "courses":
            client = CanvasClient(config.canvas.base_url, config.canvas.token())
            return _courses(client)
        if args.command == "archive":
            client = CanvasClient(config.canvas.base_url, config.canvas.token())
            archive_config = ArchiveConfig(
                root=args.root or config.archive.root,
                year=args.year or config.archive.year,
                semester=args.semester or config.archive.semester,
            )
            archiver = CourseArchiver(client, archive_config, progress=print)
            result = archiver.archive_course(args.course_id, shell_name=args.shell_name)
            print(f"Archived course {args.course_id} to {result.archive_path}")
            print(f"Report: {result.archive_path / 'manifests' / 'download-report.json'}")
            return 0
        if args.command == "sync-drive":
            service = build_drive_service(config.google_drive)
            syncer = DriveSyncer(service, root_folder_name=config.google_drive.root_folder_name, progress=print)
            result = syncer.sync_archive(args.archive)
            print(f"Synced archive to Google Drive folder ID: {result.archive_folder_id}")
            print(f"Uploaded: {result.uploaded}; updated: {result.updated}; skipped: {result.skipped}")
            print(f"Manifest: {result.manifest_path}")
            return 0
        if args.command == "archive-recent":
            client = CanvasClient(config.canvas.base_url, config.canvas.token())
            return _archive_recent(args, config, client)

        parser.error(f"Unknown command: {args.command}")
        return 2
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _courses(client: CanvasClient) -> int:
    courses = client.list_courses()
    for course in courses:
        course_id = course.get("id")
        name = course.get("name") or course.get("course_code") or "Untitled course"
        term = course.get("term", {}).get("name") if isinstance(course.get("term"), dict) else None
        suffix = f" ({term})" if term else ""
        print(f"{course_id}\t{name}{suffix}")
    return 0


def _archive_recent(args: argparse.Namespace, config: object, client: CanvasClient) -> int:
    courses = client.list_courses()
    targets = select_recent_courses(courses, years=args.years, since_year=args.since_year)
    if args.limit:
        targets = targets[: args.limit]

    if not targets:
        print("No matching courses found.")
        return 0

    print_targets(targets)

    if args.choose:
        targets = choose_targets(targets)
        if not targets:
            print("No courses selected.")
            return 0
        print("Final selection:")
        print_targets(targets)

    if args.dry_run:
        return 0

    drive_syncer: DriveSyncer | None = None
    if args.sync_drive:
        service = build_drive_service(config.google_drive)
        drive_syncer = DriveSyncer(service, root_folder_name=config.google_drive.root_folder_name, progress=print)

    failures = 0
    for course_index, target in enumerate(targets, start=1):
        print(f"[Course {course_index}/{len(targets)}] {target.year}/{target.semester}/{target.shell_name}")
        archive_config = ArchiveConfig(
            root=args.root or config.archive.root,
            year=target.year,
            semester=target.semester,
        )
        archiver = CourseArchiver(client, archive_config, progress=print)
        try:
            result = archiver.archive_course(target.course_id, shell_name=target.shell_name)
            print(f"Archived {target.course_id} to {result.archive_path}")
            if drive_syncer:
                sync_result = drive_syncer.sync_archive(result.archive_path)
                print(
                    "Synced to Drive "
                    f"(uploaded: {sync_result.uploaded}; updated: {sync_result.updated}; skipped: {sync_result.skipped})"
                )
        except Exception as exc:
            failures += 1
            print(f"Failed {target.course_id} ({target.shell_name}): {exc}", file=sys.stderr)

    if failures:
        print(f"Completed with {failures} failure(s).", file=sys.stderr)
        return 1
    return 0


def print_targets(targets: list[CourseArchiveTarget]) -> None:
    print(f"Selected {len(targets)} course(s):")
    for index, target in enumerate(targets, start=1):
        print(
            f"{index:>3}. {target.course_id}\t"
            f"{target.year}/{target.semester}/{target.shell_name}\t"
            f"({target.source_label})"
        )


def choose_targets(targets: list[CourseArchiveTarget]) -> list[CourseArchiveTarget]:
    while True:
        selection = input("Choose course numbers, ranges like 1,3-5, 'all', or blank to cancel: ")
        try:
            selected_indexes = parse_number_selection(selection, len(targets))
        except ValueError as exc:
            print(f"Invalid selection: {exc}", file=sys.stderr)
            continue
        return [targets[index] for index in selected_indexes]
