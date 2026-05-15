# Command Reference

All commands are run from the project folder.

For a first-time instructor workflow, start with [Professor Quick Start](professor-quickstart.md).

Windows uses:

```powershell
.\canvas-backup.ps1
```

macOS/Linux uses:

```bash
./canvas-backup.sh
```

The examples below use `<canvas-backup>` as a placeholder for the command that matches your operating system. The launcher runs setup automatically if Canvas Backup has not been installed into `.venv` yet.

## List Courses

```text
<canvas-backup> --config config.local.toml courses
```

Lists Canvas courses visible to the token.

## Archive One Course

```text
<canvas-backup> --config config.local.toml archive --course-id 12345
```

Override the shell folder name:

```text
<canvas-backup> --config config.local.toml archive --course-id 12345 --shell-name "ITM370"
```

Override year, semester, or root:

```text
<canvas-backup> --config config.local.toml archive --course-id 12345 --year 2025 --semester Fall --root "~/CanvasArchive"
```

Use more concurrent file downloads:

```text
<canvas-backup> --config config.local.toml archive --course-id 12345 --download-workers 10
```

## Preview Recent Courses

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --dry-run
```

## Choose Shells Interactively

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose
```

When prompted, enter numbers:

```text
1,3,5-8
```

Use `all` to select every listed course. Press Enter on a blank prompt to cancel.

## Choose And Sync To Google Drive

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --sync-drive
```

Use more concurrent Canvas file downloads during a bulk archive:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --sync-drive --download-workers 10
```

## Limit A Test Run

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --limit 2
```

## Start From A Specific Year

```text
<canvas-backup> --config config.local.toml archive-recent --since-year 2022 --choose
```

## Sync An Existing Local Archive

```text
<canvas-backup> --config config.local.toml sync-drive --archive "~/CanvasArchive/2026/Spring/ITM370"
```

The sync command checks for duplicate downloaded files, removes exact duplicates, then creates missing Google Drive folders automatically.

## Remove Duplicates Without Uploading

```text
<canvas-backup> --config config.local.toml dedupe --archive "~/CanvasArchive/2026/Spring/ITM370"
```

This checks `files/` inside the archive. It removes exact duplicate file bytes and writes:

```text
manifests/duplicates.json
```

## Progress Output

Long-running commands print counters while they work.

Examples:

```text
[Course 2/8] 2025/Fall/ITM370
[Canvas 12/140] downloaded: Week 3/lecture.pdf (300.5 MB total)
[Dedupe] Removed duplicate: files/Week 3/lecture copy.pdf -> files/Week 3/lecture.pdf
[Drive 12/140] updated: modules/01-Start Here/items.json
```

This output is informational. The final source of truth is still the manifest files in the archive.
