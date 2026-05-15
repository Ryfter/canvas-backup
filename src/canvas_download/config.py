from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib
from typing import Any


@dataclass(frozen=True)
class CanvasConfig:
    base_url: str
    token_env: str = "CANVAS_TOKEN"
    token_value: str | None = None

    def token(self) -> str:
        if self.token_value:
            return self.token_value
        if not _looks_like_env_var_name(self.token_env):
            raise ValueError(
                "canvas.token_env should be an environment variable name like CANVAS_TOKEN, "
                "not the token value. Move the token to the environment variable, or use "
                "canvas.token in a git-ignored local config."
            )
        token = os.environ.get(self.token_env)
        if not token:
            raise ValueError(
                f"Canvas token is missing. Set the {self.token_env} environment variable."
            )
        return token


@dataclass(frozen=True)
class ArchiveConfig:
    root: Path
    year: str
    semester: str
    download_workers: int = 6


@dataclass(frozen=True)
class GoogleDriveConfig:
    enabled: bool = False
    credentials_file: Path | None = None
    token_file: Path | None = None
    root_folder_name: str = "Canvas Archive"


@dataclass(frozen=True)
class AppConfig:
    canvas: CanvasConfig
    archive: ArchiveConfig
    google_drive: GoogleDriveConfig


def load_config(path: Path | None = None) -> AppConfig:
    data: dict[str, Any] = {}
    if path:
        with path.open("rb") as handle:
            data = tomllib.load(handle)

    canvas_data = data.get("canvas", {})
    archive_data = data.get("archive", {})
    drive_data = data.get("google_drive", {})

    base_url = _required(canvas_data, "base_url", "canvas.base_url")
    root = _required(archive_data, "root", "archive.root")
    year = _required(archive_data, "year", "archive.year")
    semester = _required(archive_data, "semester", "archive.semester")

    return AppConfig(
        canvas=CanvasConfig(
            base_url=str(base_url),
            token_env=str(canvas_data.get("token_env", "CANVAS_TOKEN")),
            token_value=_optional_secret(canvas_data.get("token")),
        ),
        archive=ArchiveConfig(
            root=Path(root).expanduser(),
            year=str(year),
            semester=str(semester),
            download_workers=int(archive_data.get("download_workers", 6)),
        ),
        google_drive=GoogleDriveConfig(
            enabled=bool(drive_data.get("enabled", False)),
            credentials_file=_optional_path(drive_data.get("credentials_file")),
            token_file=_optional_path(drive_data.get("token_file")),
            root_folder_name=str(drive_data.get("root_folder_name", "Canvas Archive")),
        ),
    )


def _required(data: dict[str, Any], key: str, display: str) -> Any:
    if key not in data or data[key] in ("", None):
        raise ValueError(f"Missing required config value: {display}")
    return data[key]


def _optional_path(value: Any) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser()


def _optional_secret(value: Any) -> str | None:
    if not value:
        return None
    return str(value)


def _looks_like_env_var_name(value: str) -> bool:
    return bool(value) and value.replace("_", "").isalnum() and not value[0].isdigit()
