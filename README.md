# Canvas Backup

Canvas Backup is a local-first Python tool for archiving Canvas LMS course shells and optionally mirroring those archives to Google Drive.

It is designed for instructors who want to keep a reusable course library organized by:

```text
archive-root/
  year/
    semester/
      course-shell/
```

The tool preserves Canvas file folders, module order, module items, pages, assignments, quizzes, discussions, and due-date manifests.

After downloading, Canvas Backup checks downloaded Canvas files for exact duplicates, removes duplicate copies, and records the cleanup in `manifests/duplicates.json`. Drive sync runs the same duplicate check before uploading.

## Quick Start

From PowerShell:

```powershell
cd path\to\canvas-backup
.\scripts\setup.ps1
Copy-Item config.example.toml config.local.toml
Copy-Item .env.example .env
```

Edit `.env`:

```env
CANVAS_TOKEN=your-canvas-token
```

Edit `config.local.toml`:

```toml
[canvas]
base_url = "https://your-school.instructure.com"
token_env = "CANVAS_TOKEN"

[archive]
root = "D:/CanvasArchive"
year = "2026"
semester = "Spring"
download_workers = 6
```

Preview recent shells:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --dry-run
```

Download the selected shells and sync them to Google Drive:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --sync-drive
```

If Canvas file downloads are too slow, increase concurrent downloads:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --sync-drive --download-workers 10
```

## Documentation

- [Setup Guide](docs/setup.md)
- [Configuration](docs/configuration.md)
- [Command Reference](docs/commands.md)
- [Google Drive Setup](docs/google-drive.md)
- [Archive Format](docs/archive-format.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development](docs/development.md)
- [How Canvas Backup Was Created With AI](docs/ai-build-workflow.md)
- [Prompt Playbook](docs/prompt-playbook.md)
- [Project Design](docs/project-design.md)
- [Security Notes](SECURITY.md)

## What Gets Downloaded

- Canvas course metadata.
- Canvas file folders and files.
- Exact duplicate downloaded files are removed after download and before Drive upload.
- Modules and module items in order.
- Pages as HTML plus JSON metadata.
- Assignments as HTML plus JSON metadata.
- Due dates as JSON and CSV.
- Quizzes and discussion topics as JSON, with discussion HTML where available.
- Download and Drive sync reports.
- Duplicate cleanup reports.

## Important Safety Notes

Never commit secrets. These files are intentionally ignored:

- `.env`
- `config.local.toml`
- `secrets/`
- `secrets/google-client-secret.json`
- `secrets/google-token.json`

Google Drive sync creates folders if they do not exist. Local archive folders are also created automatically.

## Current Limitations

- External tool content, publisher integrations, and embedded third-party media may only be preserved as links or metadata if Canvas does not expose the underlying file through the API.
- Canvas access depends on the permissions attached to your Canvas token.
- Google Drive sync mirrors the local archive. It does not replace the local archive.
