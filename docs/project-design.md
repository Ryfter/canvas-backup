# Canvas Backup Project Design

## Goal

Build a Python tool that can archive one or more Canvas course shells so prior course materials can be reused when building new modules.

The archive must preserve:

- Canvas file/folder structure.
- Module order and module item order.
- The module records themselves.
- Pages, assignments, quizzes, discussions, and other linked module items.
- Due dates, availability dates, and section overrides where available.
- A human-readable and machine-readable manifest for rebuilding or reviewing the course later.

Google Drive upload is feasible, but it should be treated as a sync layer. The local archive should be the canonical output because it is easier to verify, retry, diff, and recover from partial Drive uploads.

## Folder Layout

The archive path should be supplied by config or CLI flags:

```text
<archive-root>/
  <year>/
    <semester>/
      <course-shell-name>/
        files/
          <canvas-folder-tree>/
        modules/
          00-module-index.md
          01-module-name/
            module.json
            items.json
            README.md
        pages/
          <page-slug>.html
          <page-slug>.json
        assignments/
          <assignment-name>.html
          <assignment-name>.json
        quizzes/
          <quiz-name>.json
        discussions/
          <discussion-topic>.html
          <discussion-topic>.json
        manifests/
          course.json
          modules.json
          due-dates.csv
          due-dates.json
          content-map.json
          download-report.json
```

Example:

```text
~/CanvasArchive/2026/Spring/ENG-101 Combined Sections/
```

For combined sections, the shell name should come from the Canvas course shell, not from individual SIS sections. Section-level due date overrides should be recorded in the due-date manifests.

## API Coverage

Canvas source data:

- Courses: list accessible courses and fetch a selected course.
- Files and folders: enumerate Canvas folders, then download files into matching local paths.
- Modules: fetch modules and each module's module items to preserve instructional sequence.
- Pages: fetch page body HTML and metadata.
- Assignments: fetch assignment descriptions, due dates, unlock dates, lock dates, points, submission type, and overrides.
- Effective due dates: fetch course-wide effective due date data when available.
- Quizzes and discussions: fetch linked quiz/discussion records referenced by modules.
- Content export: optionally generate a Common Cartridge export as an additional safety artifact, but not as the only backup format because it is less convenient for browsing and reuse.

Google Drive target:

- Authenticate with OAuth for an installed app.
- Create or reuse nested folders for `year / semester / course shell`.
- Upload files from the completed local archive.
- Store Drive file IDs in a sync manifest so reruns can update or skip existing files.

## Configuration

Use a config file plus CLI overrides.

```toml
[canvas]
base_url = "https://school.instructure.com"
token_env = "CANVAS_TOKEN"

[archive]
root = "~/CanvasArchive"
year = "2026"
semester = "Spring"

[google_drive]
enabled = false
credentials_file = "secrets/google-client-secret.json"
token_file = "secrets/google-token.json"
root_folder_name = "Canvas Archive"
```

Do not store Canvas tokens or Google OAuth tokens in git.

## CLI Shape

Recommended commands:

```text
canvas-backup courses
canvas-backup archive --course-id 12345 --year 2026 --semester Spring
canvas-backup sync-drive --archive "~/CanvasArchive/2026/Spring/ENG-101 Combined Sections"
canvas-backup archive-recent --years 4 --choose --sync-drive
```

## Implementation Phases

1. Local archive foundation
   - Add config loading.
   - Add Canvas API client with pagination and retry handling.
   - Add filesystem-safe naming.
   - Download course metadata, folders, files, modules, and module items.

2. Rich content archive
   - Download pages, assignments, quizzes, discussions, and linked module item data.
   - Generate module README files that show the original module sequence.
   - Generate due-date CSV/JSON manifests.

3. Verification
   - Produce a download report with counts, skipped items, failed items, and source API URLs.
   - Add rerun behavior so failed files can be retried without re-downloading everything.

4. Google Drive sync
   - Add OAuth setup.
   - Mirror the local archive into Drive.
   - Save Drive IDs in `manifests/drive-sync.json`.
   - Support dry runs and resumable uploads.

5. Rebuild support
   - Add exports that help build a new module from prior material.
   - Optionally generate import-ready planning files, such as module outlines, due-date tables, and content checklists.

## Important Design Choices

- Local first: always create a complete local archive before uploading to Google Drive.
- Manifests first: keep JSON and CSV metadata alongside downloaded content so the archive is useful even if Canvas URLs later change.
- Preserve sequence: module order and item order should be explicit in `modules.json` and in readable module README files.
- Preserve dates separately: due dates should live in dedicated manifests instead of being buried only inside assignment JSON.
- Remove duplicate downloaded files before upload: exact duplicate file bytes are removed from `files/` and logged in `manifests/duplicates.json`.
- Keep reruns safe: the downloader should be idempotent and should not delete prior archive files unless explicitly asked.

## Known Constraints

- Canvas content embedded from external tools may not be downloadable through Canvas APIs. The archive should preserve links and metadata for those items.
- Some Canvas files may require authenticated download URLs that expire. The tool should download file bytes immediately and record original metadata separately.
- Google Drive upload can fail halfway through large courses. A Drive sync manifest is needed for reliable resume behavior.
- API access depends on the permissions granted to the Canvas token.
