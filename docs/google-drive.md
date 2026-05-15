# Google Drive Setup

Google Drive sync is optional. Canvas downloads work without Google Drive.

## What The Files Mean

`secrets/google-client-secret.json`

Downloaded from Google Cloud Console. It identifies this local desktop application to Google.

`secrets/google-token.json`

Created automatically after the first successful Google login. Do not create it manually.

## Create Google Credentials

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Search for **Google Drive API**.
4. Open **Google Drive API** and click **Enable**.
5. Go to **APIs & Services > OAuth consent screen**.
6. Configure the consent screen.
7. If the app is in testing mode, add your Google account as a test user.
8. Go to **APIs & Services > Credentials**.
9. Choose **Create Credentials > OAuth client ID**.
10. Select **Desktop app**.
11. Download the JSON file.
12. Save it in this project as:

```text
secrets/google-client-secret.json
```

Create the folder if needed:

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force secrets
```

macOS/Linux:

```bash
mkdir -p secrets
```

## First Sync

Run a sync command:

Windows PowerShell:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml sync-drive --archive "~/CanvasArchive/2026/Spring/ITM370"
```

macOS/Linux:

```bash
./.venv/bin/canvas-backup --config config.local.toml sync-drive --archive "~/CanvasArchive/2026/Spring/ITM370"
```

Google opens a browser authorization page. After approval, the app creates:

```text
secrets/google-token.json
```

## Drive Folder Behavior

The sync command:

- Creates the top-level Drive folder if missing.
- Creates year, semester, and shell folders if missing.
- Reuses existing folders with the same name and parent.
- Uploads new files.
- Updates existing files with the same name in the same Drive folder.
- Writes `manifests/drive-sync.json` in the local archive.

## Scope

The app uses the Google Drive `drive.file` scope. This is limited to files and folders created or opened by the app.
