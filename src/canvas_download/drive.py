from __future__ import annotations

from dataclasses import dataclass
import mimetypes
from pathlib import Path
from typing import Any, Callable

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from canvas_download.config import GoogleDriveConfig
from canvas_download.dedupe import dedupe_archive_files
from canvas_download.json_io import write_json


DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


@dataclass(frozen=True)
class DriveSyncResult:
    root_folder_id: str
    archive_folder_id: str
    uploaded: int
    updated: int
    skipped: int
    manifest_path: Path


class GoogleDriveConfigError(ValueError):
    pass


def build_drive_service(config: GoogleDriveConfig) -> Any:
    if not config.credentials_file:
        raise GoogleDriveConfigError("Missing google_drive.credentials_file in config.")
    if not config.token_file:
        raise GoogleDriveConfigError("Missing google_drive.token_file in config.")
    if not config.credentials_file.exists():
        raise GoogleDriveConfigError(f"Google credentials file not found: {config.credentials_file}")

    credentials: Credentials | None = None
    if config.token_file.exists():
        credentials = Credentials.from_authorized_user_file(str(config.token_file), [DRIVE_FILE_SCOPE])

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(GoogleAuthRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(config.credentials_file),
                scopes=[DRIVE_FILE_SCOPE],
            )
            credentials = flow.run_local_server(port=0)

        config.token_file.parent.mkdir(parents=True, exist_ok=True)
        config.token_file.write_text(credentials.to_json(), encoding="utf-8")

    return build("drive", "v3", credentials=credentials)


class DriveSyncer:
    def __init__(
        self,
        service: Any,
        root_folder_name: str = "Canvas Archive",
        progress: Callable[[str], None] | None = None,
    ) -> None:
        self.service = service
        self.root_folder_name = root_folder_name
        self.progress = progress
        self._folder_cache: dict[tuple[str, str], str] = {}

    def sync_archive(self, archive_path: Path) -> DriveSyncResult:
        archive_path = archive_path.resolve()
        if not archive_path.exists() or not archive_path.is_dir():
            raise ValueError(f"Archive folder does not exist: {archive_path}")

        dedupe_archive_files(archive_path, progress=self.progress)
        self._progress(f"[Drive] Preparing folders for {archive_path.name}")
        root_folder_id = self._ensure_folder(self.root_folder_name, "root")
        parent_id = root_folder_id
        for part in archive_drive_parts(archive_path):
            parent_id = self._ensure_folder(part, parent_id)

        uploaded = 0
        updated = 0
        skipped = 0
        files: list[dict[str, Any]] = []
        local_files = sorted(path for path in archive_path.rglob("*") if path.is_file())
        sync_files = [
            path for path in local_files if path.relative_to(archive_path).as_posix() != "manifests/drive-sync.json"
        ]
        skipped = len(local_files) - len(sync_files)

        for index, local_file in enumerate(sync_files, start=1):
            relative_path = local_file.relative_to(archive_path)
            folder_id = self._ensure_relative_folder(parent_id, relative_path.parent)
            existing = self._find_file(local_file.name, folder_id)
            uploaded_file = self._upload_file(local_file, folder_id, existing_id=existing.get("id") if existing else None)
            if existing:
                updated += 1
                action = "updated"
            else:
                uploaded += 1
                action = "uploaded"
            self._progress(f"[Drive {index}/{len(sync_files)}] {action}: {relative_path.as_posix()}")
            files.append(
                {
                    "action": action,
                    "local_path": str(local_file),
                    "relative_path": relative_path.as_posix(),
                    "drive_id": uploaded_file.get("id"),
                    "drive_name": uploaded_file.get("name"),
                    "webViewLink": uploaded_file.get("webViewLink"),
                }
            )

        manifest = {
            "archive_path": str(archive_path),
            "drive_root_folder_name": self.root_folder_name,
            "drive_root_folder_id": root_folder_id,
            "drive_archive_folder_id": parent_id,
            "counts": {
                "uploaded": uploaded,
                "updated": updated,
                "skipped": skipped,
            },
            "files": files,
        }
        manifest_path = archive_path / "manifests" / "drive-sync.json"
        write_json(manifest_path, manifest)
        self._progress(f"[Drive] Finished sync: uploaded {uploaded}, updated {updated}, skipped {skipped}")
        return DriveSyncResult(
            root_folder_id=root_folder_id,
            archive_folder_id=parent_id,
            uploaded=uploaded,
            updated=updated,
            skipped=skipped,
            manifest_path=manifest_path,
        )

    def _ensure_relative_folder(self, parent_id: str, relative_folder: Path) -> str:
        current_parent = parent_id
        for part in relative_folder.parts:
            if part in ("", "."):
                continue
            current_parent = self._ensure_folder(part, current_parent)
        return current_parent

    def _ensure_folder(self, name: str, parent_id: str) -> str:
        cache_key = (parent_id, name)
        if cache_key in self._folder_cache:
            return self._folder_cache[cache_key]

        existing = self._find_folder(name, parent_id)
        if existing:
            folder_id = existing["id"]
        else:
            body = {"name": name, "mimeType": FOLDER_MIME_TYPE, "parents": [parent_id]}
            created = (
                self.service.files()
                .create(body=body, fields="id, name", supportsAllDrives=True)
                .execute()
            )
            folder_id = created["id"]

        self._folder_cache[cache_key] = folder_id
        return folder_id

    def _find_folder(self, name: str, parent_id: str) -> dict[str, Any] | None:
        return self._find_by_query(
            f"name = {drive_query_literal(name)} and "
            f"mimeType = {drive_query_literal(FOLDER_MIME_TYPE)} and "
            f"{drive_query_literal(parent_id)} in parents and trashed = false"
        )

    def _find_file(self, name: str, parent_id: str) -> dict[str, Any] | None:
        return self._find_by_query(
            f"name = {drive_query_literal(name)} and "
            f"mimeType != {drive_query_literal(FOLDER_MIME_TYPE)} and "
            f"{drive_query_literal(parent_id)} in parents and trashed = false"
        )

    def _find_by_query(self, query: str) -> dict[str, Any] | None:
        result = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name, mimeType, webViewLink)", pageSize=1)
            .execute()
        )
        files = result.get("files", [])
        return files[0] if files else None

    def _upload_file(self, local_file: Path, parent_id: str, existing_id: str | None = None) -> dict[str, Any]:
        mime_type = mimetypes.guess_type(local_file.name)[0] or "application/octet-stream"
        media = MediaFileUpload(str(local_file), mimetype=mime_type, resumable=True)
        body = {"name": local_file.name}
        if existing_id:
            return (
                self.service.files()
                .update(fileId=existing_id, body=body, media_body=media, fields="id, name, webViewLink")
                .execute()
            )
        body["parents"] = [parent_id]
        return (
            self.service.files()
            .create(body=body, media_body=media, fields="id, name, webViewLink", supportsAllDrives=True)
            .execute()
        )

    def _progress(self, message: str) -> None:
        if self.progress:
            self.progress(message)


def archive_drive_parts(archive_path: Path) -> list[str]:
    parts = [part for part in archive_path.parts if part not in ("", "\\")]
    if len(parts) >= 3:
        return parts[-3:]
    return [archive_path.name]


def drive_query_literal(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
