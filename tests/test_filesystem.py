from pathlib import Path

import pytest

from canvas_download.filesystem import ensure_within, numbered_name, safe_name


def test_safe_name_removes_windows_unsafe_characters() -> None:
    assert safe_name(' Week 1: "Intro" / Setup? ') == "Week 1- -Intro- - Setup-"


def test_safe_name_handles_reserved_windows_names() -> None:
    assert safe_name("CON") == "_CON"


def test_numbered_name_prefixes_order() -> None:
    assert numbered_name(3, "Module: Start") == "03-Module- Start"


def test_ensure_within_rejects_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        ensure_within(tmp_path, tmp_path.parent / "outside.txt")
