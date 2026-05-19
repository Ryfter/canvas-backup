# Troubleshooting

## `.venv` Does Not Exist

Run the setup script first.

Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

macOS/Linux:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script creates `.venv`, `.env`, `config.local.toml`, `secrets/`, and configured local archive paths if they are missing.

You can also use the root launcher. It runs setup automatically if Canvas Backup is not installed yet.

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml courses
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml courses
```

Do not look for the command inside `.venv` during normal use. The root launcher is the beginner-friendly command.

## `invalid choice: 'sync-drive'`

The installed CLI is stale.

The easiest fix is to run the update script:

Windows PowerShell:

```powershell
.\scripts\update.ps1
```

macOS/Linux:

```bash
./scripts/update.sh
```

You can also refresh the install directly.

Windows PowerShell:

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

macOS/Linux:

```bash
./.venv/bin/python -m pip install -e ".[dev]"
```

You can also rerun the root launcher:

```text
<canvas-backup> --config config.local.toml courses
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

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose
```

Then sync:

```text
<canvas-backup> --config config.local.toml sync-drive --archive "~/CanvasArchive/2026/Spring/ITM370"
```

Use the operating-system command from [Command Reference](commands.md) in place of `<canvas-backup>`.

## The Wrong Courses Are Selected

Use interactive selection:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --dry-run
```

Then select only the course numbers you want.

## Google Says The App Is In Testing

Add your Google account as a test user in the Google Cloud OAuth consent screen.

## Running From Dropbox, OneDrive, Or Google Drive Desktop Fails

Do not run the Canvas Backup project folder from inside a synced folder. Sync tools can lock or delay `.venv/`, `.git/`, and dependency files during setup.

Use a normal local project folder:

```text
C:/Dev/canvas-backup
```

Then set the archive root to a synced folder if desired:

```toml
[archive]
root = "C:/Users/YourName/Dropbox/CanvasArchive"
```

The project folder should be local. The archive folder can be synced.

## A Course Fails Partway Through

Check:

```text
manifests/download-report.json
```

The tool is designed so reruns can reuse already-created folders and overwrite/update downloaded metadata.

## The Command Looks Stuck

Archive and optional Drive sync commands print counters while they work. If the same line does not change for a long time, the tool is probably waiting on a large Canvas file download or Google Drive upload.

After the command finishes, check:

```text
manifests/download-report.json
manifests/drive-sync.json
```

## Canvas Downloads Are Too Slow

Canvas Backup downloads Canvas files concurrently. The default is:

```toml
[archive]
download_workers = 6
```

You can raise it for a single run:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --sync-drive --download-workers 10
```

If Canvas returns rate-limit errors, lower the value to `4` or `2`. Canvas uses dynamic throttling, so very high concurrency can backfire.

## Duplicate Files Were Removed

Canvas Backup removes exact duplicate downloaded files from `files/` after archive download and before Drive sync. This only removes byte-for-byte duplicate files.

Check the duplicate manifest:

```text
manifests/duplicates.json
```

The manifest records the kept file path, removed file paths, size, and SHA-256 hash.

## PowerShell Blocks `setup.ps1`

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
```
