from pathlib import Path

from canvas_download.dedupe import dedupe_archive_files


def test_dedupe_archive_files_removes_exact_duplicates(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    files = archive / "files"
    files.mkdir(parents=True)
    kept = files / "a.txt"
    duplicate = files / "b.txt"
    unique = files / "c.txt"
    kept.write_text("same", encoding="utf-8")
    duplicate.write_text("same", encoding="utf-8")
    unique.write_text("different", encoding="utf-8")

    result = dedupe_archive_files(archive)

    assert kept.exists()
    assert not duplicate.exists()
    assert unique.exists()
    assert result.duplicate_sets == 1
    assert result.removed == 1
    assert result.manifest_path.exists()
