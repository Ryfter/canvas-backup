# Configuration

Canvas Backup uses two local files:

- `.env` for secrets.
- `config.local.toml` for settings.

Both files are ignored by Git.

## `.env`

```env
CANVAS_TOKEN=your-canvas-token
```

The CLI automatically loads `.env` before reading the Canvas token.

## `config.local.toml`

Start from:

```powershell
Copy-Item config.example.toml config.local.toml
```

Example:

```toml
[canvas]
base_url = "https://your-school.instructure.com"
token_env = "CANVAS_TOKEN"

[archive]
root = "D:/CanvasArchive"
year = "2026"
semester = "Spring"

[google_drive]
enabled = false
credentials_file = "secrets/google-client-secret.json"
token_file = "secrets/google-token.json"
root_folder_name = "Canvas Archive"
```

## Canvas Settings

`canvas.base_url`

Your Canvas instance, such as:

```toml
base_url = "https://school.instructure.com"
```

`canvas.token_env`

The environment variable that stores the token:

```toml
token_env = "CANVAS_TOKEN"
```

`canvas.token`

Optional local-only shortcut:

```toml
token = "your-token"
```

Prefer `.env` instead of placing tokens in TOML.

## Archive Settings

`archive.root`

The local archive root. Missing folders are created automatically.

```toml
root = "D:/CanvasArchive"
```

`archive.year` and `archive.semester`

Used by the single-course `archive` command. The `archive-recent` command infers year and semester per course.

## Google Drive Settings

`google_drive.credentials_file`

The OAuth desktop app credential downloaded from Google Cloud Console.

`google_drive.token_file`

Created automatically after the first Google authorization.

`google_drive.root_folder_name`

The top-level Google Drive folder. The sync command creates it if needed.
