# Professor Quick Start

This is the shortest path for an instructor who wants to back up Canvas course shells.

Canvas Backup creates a local archive first. Google Drive sync is optional and can be added later.

If you are comfortable with command-line tools and want more implementation detail, see [Technical Professor Guide](technical-professor-guide.md).

## What You Need

- Python 3.11 or newer.
- Git, or a ZIP download of this repository.
- A Canvas access token.
- Optional: Google Drive credentials if you want automatic Drive upload.

## One-Time Setup

### 1. Download Canvas Backup

Using Git:

```bash
git clone https://github.com/Ryfter/canvas-backup.git
cd canvas-backup
```

If you downloaded a ZIP from GitHub, unzip it and open a terminal in the `canvas-backup` folder.

### 2. Run Setup

Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

If PowerShell blocks the script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
```

macOS/Linux:

```bash
chmod +x scripts/setup.sh canvas-backup.sh
./scripts/setup.sh
```

Setup creates the files and folders the tool needs:

```text
.venv/              Internal Python environment
.env                Your Canvas token
config.local.toml   Your local settings
secrets/            Optional Google Drive credentials
~/CanvasArchive     Default local archive folder
```

You do not need to open or run anything inside `.venv`.

### 3. Add Your Canvas Token

Open `.env` in a text editor and replace the placeholder:

```env
CANVAS_TOKEN=your-canvas-token
```

Keep this file private. Do not upload it, email it, or paste it into chat.

### 4. Set Your Canvas URL

Open `config.local.toml` and set your Canvas site:

```toml
[canvas]
base_url = "https://your-school.instructure.com"
token_env = "CANVAS_TOKEN"
```

The default local archive folder is:

```toml
[archive]
root = "~/CanvasArchive"
```

The `~` means your home folder. It works on Windows, macOS, and Linux.

## Daily Commands

Run commands from the `canvas-backup` project folder.

Windows uses:

```powershell
.\canvas-backup.ps1
```

macOS/Linux uses:

```bash
./canvas-backup.sh
```

### Test Canvas Access

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml courses
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml courses
```

If this lists your courses, the Canvas token is working.

### Preview The Last 4 Years

This does not download anything. It only shows the shells the tool found.

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml archive-recent --years 4 --choose --dry-run
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml archive-recent --years 4 --choose --dry-run
```

### Download Selected Shells

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml archive-recent --years 4 --choose
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml archive-recent --years 4 --choose
```

When prompted, choose the shells you want:

```text
1,3,5-8
```

Use `all` only if every listed shell should be archived.

## Add Google Drive Later

Local backup works without Google Drive.

When you are ready for Drive upload:

1. Follow [Google Drive Setup](google-drive.md).
2. Put the Google credential file at `secrets/google-client-secret.json`.
3. Run the archive command with `--sync-drive`.

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml archive-recent --years 4 --choose --sync-drive
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml archive-recent --years 4 --choose --sync-drive
```

## Where Files Go

By default, files go here:

```text
~/CanvasArchive/
  2026/
    Spring/
      Course Shell Name/
```

Inside each course shell, Canvas Backup saves:

- Canvas files and folders.
- Modules and module items.
- Pages.
- Assignments.
- Due dates.
- Quizzes.
- Discussions.
- Download, duplicate, and Drive sync reports.

## If Something Is Missing

If the command is not found, use the launcher in the project folder:

Windows:

```powershell
.\canvas-backup.ps1 --help
```

macOS/Linux:

```bash
./canvas-backup.sh --help
```

If `.venv`, `.env`, `config.local.toml`, or `secrets/` are missing, run setup again. Setup is safe to rerun.

For more help, see [Troubleshooting](troubleshooting.md).

## Updating Later

If you installed with Git, update from the project folder:

Windows PowerShell:

```powershell
.\scripts\update.ps1
```

macOS/Linux:

```bash
./scripts/update.sh
```

See [Updating Canvas Backup](updating.md) for details.
