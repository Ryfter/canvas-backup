# Troubleshooting

## `invalid choice: 'sync-drive'`

The installed CLI is stale.

Run:

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## `Canvas token is missing`

Check `.env`:

```env
CANVAS_TOKEN=your-token
```

Check `config.local.toml`:

```toml
[canvas]
token_env = "CANVAS_TOKEN"
```

## `canvas.token_env should be an environment variable name`

The token was pasted into `token_env`.

Wrong:

```toml
token_env = "123~actual-token-value"
```

Right:

```toml
token_env = "CANVAS_TOKEN"
```

Then put the token in `.env`.

## Google Opens A Browser But Sync Uploads Zero Files

The Drive authorization worked, but the local archive folder has no files yet.

Run a Canvas archive first:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose
```

Then sync:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml sync-drive --archive "D:\CanvasArchive\2026\Spring\ITM370"
```

## The Wrong Courses Are Selected

Use interactive selection:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --dry-run
```

Then select only the course numbers you want.

## Google Says The App Is In Testing

Add your Google account as a test user in the Google Cloud OAuth consent screen.

## A Course Fails Partway Through

Check:

```text
manifests/download-report.json
```

The tool is designed so reruns can reuse already-created folders and overwrite/update downloaded metadata.

## The Command Looks Stuck

Archive and Drive sync commands print counters while they work. If the same line does not change for a long time, the tool is probably waiting on a large Canvas file download or Google Drive upload.

After the command finishes, check:

```text
manifests/download-report.json
manifests/drive-sync.json
```

## PowerShell Blocks `setup.ps1`

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
```
