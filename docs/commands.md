# Command Reference

All commands are run from the project folder.

## List Courses

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml courses
```

Lists Canvas courses visible to the token.

## Archive One Course

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive --course-id 12345
```

Override the shell folder name:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive --course-id 12345 --shell-name "ITM370"
```

Override year, semester, or root:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive --course-id 12345 --year 2025 --semester Fall --root "D:/CanvasArchive"
```

## Preview Recent Courses

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --dry-run
```

## Choose Shells Interactively

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose
```

When prompted, enter numbers:

```text
1,3,5-8
```

Use `all` to select every listed course. Press Enter on a blank prompt to cancel.

## Choose And Sync To Google Drive

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --sync-drive
```

## Limit A Test Run

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --limit 2
```

## Start From A Specific Year

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --since-year 2022 --choose
```

## Sync An Existing Local Archive

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml sync-drive --archive "D:\CanvasArchive\2026\Spring\ITM370"
```

The sync command creates missing Google Drive folders automatically.

## Progress Output

Long-running commands print counters while they work.

Examples:

```text
[Course 2/8] 2025/Fall/ITM370
[Canvas] Downloaded file 12 (folder file 3/9): Week 3/lecture.pdf
[Drive 12/140] updated: modules/01-Start Here/items.json
```

This output is informational. The final source of truth is still the manifest files in the archive.
