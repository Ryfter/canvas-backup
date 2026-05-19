# Technical Professor Guide

This guide is for instructors who are comfortable with command-line tools and want to understand how Canvas Backup works under the hood.

Most professors should start with [Professor Quick Start](professor-quickstart.md). This guide adds implementation details, operational choices, and troubleshooting context for more technical users.

## Mental Model

Canvas Backup has two default layers, plus one optional upload layer:

```text
Canvas API -> Local archive -> Optional Google Drive API mirror
```

The local archive is the source of truth. The archive root can be a normal local folder, external drive, network drive, or local folder synced by Google Drive Desktop, Dropbox, or OneDrive. Built-in Google Drive API sync is treated as an optional upload target, not the primary storage location.

## Repository Layout

Important project files:

```text
canvas-backup.ps1              Windows launcher
canvas-backup.sh               macOS/Linux launcher
scripts/setup.ps1              Windows first-time setup
scripts/setup.sh               macOS/Linux first-time setup
config.example.toml            Template config
.env.example                   Template environment file
src/canvas_download/           Python package
tests/                         Pytest test suite
docs/                          Documentation
```

Important local files created during setup:

```text
.venv/                         Project-local Python environment
.env                           Canvas token; ignored by Git
config.local.toml              Local settings; ignored by Git
secrets/google-client-secret.json
secrets/google-token.json
```

The launchers exist so normal users do not need to call commands inside `.venv`.

## Why `.venv` Is Used

`.venv` keeps Canvas Backup dependencies isolated from the rest of the computer. This avoids conflicts with system Python packages or other Python projects.

For this project, `.venv` is an implementation detail. Users should run:

Windows:

```powershell
.\canvas-backup.ps1 --config config.local.toml courses
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml courses
```

The launcher checks whether the installed command exists. If it does not, the launcher runs setup first.

## Configuration Files

Canvas Backup separates secrets from settings.

`.env` stores secrets:

```env
CANVAS_TOKEN=your-canvas-token
```

`config.local.toml` stores local settings:

```toml
[canvas]
base_url = "https://your-school.instructure.com"
token_env = "CANVAS_TOKEN"

[archive]
root = "~/CanvasArchive"
year = "2026"
semester = "Spring"
download_workers = 6

[google_drive]
enabled = false
credentials_file = "secrets/google-client-secret.json"
token_file = "secrets/google-token.json"
root_folder_name = "Canvas Archive"
```

`token_env` should be the name of the environment variable, not the token itself. The default is `CANVAS_TOKEN`.

The setup script creates missing local paths based on this config:

- The archive root.
- The `secrets/` folder.
- Parent folders for Google credential and token files.

The archive root can point to a local synced folder. See [Local And Synced Folder Backups](local-and-synced-folders.md).

## Archive Path Rules

The standard archive shape is:

```text
<archive-root>/
  <year>/
    <semester>/
      <course-shell-name>/
```

For `archive-recent`, year and semester are inferred from Canvas course data when possible. The tool checks term names, course names, course codes, SIS IDs, and Canvas dates.

For `archive`, year and semester come from `config.local.toml` unless overridden:

```text
<canvas-backup> --config config.local.toml archive --course-id 12345 --year 2025 --semester Fall
```

Shell names are filesystem-safe versions of the Canvas course shell name. For combined sections, this intentionally uses the shell-level course name rather than individual section names.

## Course Selection Workflow

Many instructors are listed as teachers in shells they do not want to archive. Use `--choose` so selection is explicit.

Preview without downloading:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --dry-run
```

Download selected shells:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose
```

Selection syntax:

```text
1,3,5-8
```

Use `all` only when every listed shell should be archived.

## What Gets Downloaded

The archiver currently saves:

- Course metadata.
- Canvas file folders and files.
- Module records and module item records.
- Human-readable module outlines.
- Pages as HTML plus JSON metadata.
- Assignments as HTML plus JSON metadata.
- Assignment due dates, unlock dates, lock dates, and section/date overrides when Canvas exposes them.
- Effective due-date data when Canvas permits access.
- Quiz metadata.
- Discussion topic metadata and HTML message bodies.
- Content, download, duplicate, and Drive sync manifests.

The archive is designed to support course rebuilding and module reuse, not only raw file backup.

## Manifest Files

Each course shell includes a `manifests/` folder.

Important manifests:

```text
course.json              Canvas course record
folders.json             Canvas folder records
modules.json             Module records with module items
pages.json               Page records
assignments.json         Assignment records
quizzes.json             Quiz records
discussions.json         Discussion records
due-dates.json           Due-date details
due-dates.csv            Spreadsheet-friendly due-date export
content-map.json         Combined map of archived content
download-report.json     Counts, warnings, and failures
duplicates.json          Exact duplicate cleanup report
drive-sync.json          Google Drive sync report
```

For reuse planning, start with:

- `modules/00-module-index.md`
- Each module folder's `README.md`
- `manifests/due-dates.csv`
- `manifests/content-map.json`

## Duplicate Handling

Canvas Backup removes exact duplicate downloaded files after archive download and before Drive sync.

Current scope:

- Scans files under `files/`.
- Ignores `_canvas-files.json`.
- Ignores unfinished `.part` files.
- Groups possible duplicates by file size.
- Hashes same-size candidates with SHA-256.
- Keeps one copy and removes byte-for-byte duplicates.
- Records all removals in `manifests/duplicates.json`.

It does not remove near-duplicates, renamed-but-edited files, or duplicate generated JSON/HTML metadata.

## Performance Tuning

Canvas file downloads run concurrently. The default is:

```toml
[archive]
download_workers = 6
```

For a one-time run:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --download-workers 10
```

Higher is not always better. Canvas may throttle or slow down under too many parallel requests. Practical guidance:

- Start with `6`.
- Try `8` or `10` if large file downloads are slow.
- Drop to `4` or `2` if Canvas returns rate-limit errors or failures increase.

The progress output shows counters such as:

```text
[Canvas 12/140] downloaded: Week 3/lecture.pdf (300.5 MB total)
[Drive 12/140] updated: modules/01-Start Here/items.json
```

## Synced Folder And Google Drive API Details

Built-in Google Drive API sync is optional. A local synced folder may be simpler for many users.

Use a synced folder when the user already has Google Drive Desktop, Dropbox, or OneDrive installed and wants normal desktop sync behavior.

Use built-in Google Drive API sync when the user wants the tool itself to upload the completed archive to Google Drive.

Avoid placing the project folder inside a synced folder. The archive root can be synced; the project folder should stay in a normal local folder.

When Google Drive API sync is enabled, the sync command:

- Checks duplicates before upload.
- Creates the top-level Drive folder if missing.
- Creates year, semester, and shell folders if missing.
- Reuses existing folders with the same name and parent.
- Uploads new files.
- Updates existing files with the same name in the same Drive folder.
- Skips the local `manifests/drive-sync.json` file while uploading, then writes a fresh local sync manifest.

The Drive folder path is based on the last three local archive path parts:

```text
year / semester / course-shell
```

For example:

```text
~/CanvasArchive/2026/Spring/ITM370
```

syncs to:

```text
Canvas Archive / 2026 / Spring / ITM370
```

The app uses the Google Drive `drive.file` OAuth scope. This limits access to files and folders created or opened by the app.

## Reruns And Recovery

Setup is safe to rerun. It recreates missing local folders and reinstalls the package into `.venv`.

Archive reruns reuse the same folder path and overwrite generated metadata files. Downloaded Canvas files are written to the same local paths. If a course fails partway through, check:

```text
manifests/download-report.json
```

Drive sync can be rerun after a failed or partial upload. It searches for existing Drive files by name inside the same Drive folder and updates them when found.

## Security Checklist

Before sharing screenshots, commits, or support requests:

- Do not share `.env`.
- Do not share `config.local.toml` if it contains sensitive local paths.
- Do not share `secrets/google-client-secret.json`.
- Do not share `secrets/google-token.json`.
- Do not paste Canvas tokens into chat, email, or GitHub issues.
- Do not include student submissions or confidential student data in public examples.

Before committing changes, confirm these files are not tracked:

```powershell
git ls-files .env config.local.toml secrets google-token.json secrets/google-client-secret.json
```

No output is the expected result.

## Useful Technical Commands

Update from GitHub and refresh the local install:

Windows:

```powershell
.\scripts\update.ps1
```

macOS/Linux:

```bash
./scripts/update.sh
```

Run tests:

Windows:

```powershell
.\scripts\test.ps1
```

macOS/Linux:

```bash
./scripts/test.sh
```

Refresh the editable install:

Windows:

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

macOS/Linux:

```bash
./.venv/bin/python -m pip install -e ".[dev]"
```

Force local path creation from config:

Windows:

```powershell
.\.venv\Scripts\python -m canvas_download.bootstrap --config config.local.toml
```

macOS/Linux:

```bash
./.venv/bin/python -m canvas_download.bootstrap --config config.local.toml
```

## Known Limits

- Canvas API access depends on the permissions attached to the token.
- External tool content and publisher integrations may only be preserved as links or metadata.
- Discussion replies and student-generated content may require additional API coverage depending on the course and permissions.
- Duplicate detection is exact-match only.
- Built-in Google Drive API sync mirrors the local archive when used; it is not a replacement for keeping a local copy.
