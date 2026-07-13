# Changelog

All notable changes to Canvas Backup are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-12

First released version. Canvas Backup archives Canvas LMS course shells to a local
folder organized as `archive-root/year/semester/course-shell/`, and can optionally
sync that folder to Google Drive.

### Added

- Local-first course archiving. Preserves Canvas file folders, module order, module
  items, pages, assignments, quizzes, discussions, and due-date manifests.
- `courses` command to list Canvas courses visible to the token.
- `archive` command to archive a single course shell, with overrides for year,
  semester, archive root, and shell folder name.
- `archive-recent` command for bulk archiving, with interactive shell selection
  (`--choose`), `--dry-run` preview, `--limit`, and `--since-year`.
- Parallel Canvas file downloads, tunable with `--download-workers`.
- Automatic deduplication of exact-duplicate downloaded files before Google Drive
  sync, recorded in `manifests/duplicates.json`. Also available standalone via the
  `dedupe` command.
- Optional Google Drive upload via the Drive API (`sync-drive`, `--sync-drive`).
  Archives that already live inside a Google Drive Desktop, Dropbox, or OneDrive
  folder do not need it.
- Progress counters for long-running downloads and syncs.
- `--json-progress` on `archive`, emitting JSON Lines progress and a structured
  completion event for programmatic callers.
- Cross-platform setup and launchers: `canvas-backup.ps1`, `canvas-backup.sh`, and
  `scripts/setup.*`, which bootstrap `.venv` on first run.
- Documentation set covering setup, configuration, commands, the archive format,
  Google Drive, updating, troubleshooting, local and synced folder workflows, and
  both a professor quick start and a technical professor guide.
- MIT license.

[1.0.0]: https://github.com/Ryfter/canvas-backup/releases/tag/v1.0.0
