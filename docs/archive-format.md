# Archive Format

The archive is local-first. Google Drive sync mirrors the completed local archive.

## Top-Level Structure

```text
D:/CanvasArchive/
  2026/
    Spring/
      ITM370/
        files/
        modules/
        pages/
        assignments/
        quizzes/
        discussions/
        manifests/
```

## `files/`

Canvas file folders are recreated under `files/`.

Each folder may include:

```text
_canvas-files.json
```

This stores Canvas metadata for files in that folder.

## `modules/`

Modules are numbered to preserve order:

```text
modules/
  00-module-index.md
  01-Start Here/
    module.json
    items.json
    README.md
```

`README.md` is a human-readable module outline.

## `pages/`

Each Canvas page is saved as:

```text
Page Title.html
Page Title.json
```

The HTML file contains the Canvas page body. The JSON file contains metadata.

## `assignments/`

Each assignment is saved as:

```text
Assignment Name.html
Assignment Name.json
```

The HTML file contains the assignment description. The JSON file contains assignment metadata, including dates when Canvas provides them.

## `quizzes/`

Quiz metadata is saved as JSON.

## `discussions/`

Discussion topics are saved as JSON. If Canvas provides a message body, it is also saved as HTML.

## `manifests/`

Important files:

```text
course.json
folders.json
modules.json
pages.json
assignments.json
quizzes.json
discussions.json
due-dates.json
due-dates.csv
content-map.json
download-report.json
drive-sync.json
```

`download-report.json` records counts, warnings, and failures.

`drive-sync.json` is created after Google Drive sync.
