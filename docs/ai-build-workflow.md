# How Canvas Backup Was Created With AI

This document explains the workflow used to create Canvas Backup. It is written for colleagues who may not write code every day but want to understand how an AI-assisted project like this can be built responsibly.

## The Short Version

Canvas Backup was built through a conversation with an AI coding assistant. The human provided the problem, constraints, and product decisions. The AI wrote code, documentation, tests, and GitHub commits. The human reviewed behavior, tried commands, reported problems, and refined the workflow.

The project was not created from one perfect prompt. It was built iteratively:

```text
idea -> design -> first script -> test locally -> add Google Drive -> improve UX -> document -> publish -> optimize
```

## The Original Problem

The practical goal was:

- Download Canvas course shell content.
- Preserve year, semester, and course shell organization.
- Preserve Canvas file folders and module layout.
- Save assignments, pages, quizzes, discussions, and due dates.
- Support Google Drive upload.
- Make the tool easy enough for instructors to use.

One important human decision shaped the project: local backup should come first, and Google Drive should mirror that local backup. That made the workflow safer because files can be checked locally before upload.

## Human And AI Roles

The human did these things:

- Explained the educational workflow and why course shells matter.
- Decided the folder structure: year, semester, course shell.
- Pointed out missing requirements, such as choosing shells manually.
- Tested commands and reported errors.
- Created local Canvas and Google credentials.
- Asked for documentation and GitHub publishing.

The AI assistant did these things:

- Designed the project structure.
- Looked up current Canvas and Google Drive API documentation.
- Wrote Python code.
- Added tests.
- Updated documentation.
- Added Git ignore rules so secrets would not be published.
- Created and pushed the GitHub repository.
- Responded to test results and runtime problems.

## Build Phases

### 1. Design First

The first step was not code. The first step was a project design document:

- What should be downloaded?
- What folder structure should be used?
- What should stay local?
- What should go to Google Drive?
- What files should never be committed?

This became [Project Design](project-design.md).

### 2. Local Archive First

The first working version downloaded Canvas content locally. This was intentional. Local files are easier to inspect, retry, back up, and troubleshoot than direct cloud uploads.

The first local archive included:

- Files and Canvas folders.
- Modules and module items.
- Pages.
- Assignments.
- Quizzes.
- Discussions.
- Due-date manifests.

### 3. Configuration And Secrets

The project was set up so secret values stay out of GitHub:

- `.env` stores the Canvas token.
- `config.local.toml` stores local settings.
- `secrets/` stores Google OAuth files.
- `.gitignore` prevents these files from being committed.

This was a major safety checkpoint before publishing the repository.

### 4. Google Drive Sync

Google Drive sync was added after local archiving worked. The sync command:

- Creates missing Drive folders.
- Reuses existing folders.
- Uploads new files.
- Updates existing files.
- Writes a sync manifest.

### 5. Choosing Course Shells

A bulk download command was not enough because instructors may be listed as teachers on extra course shells. An interactive chooser was added so the user can select only the shells they want.

Example:

```text
Choose course numbers, ranges like 1,3-5, 'all', or blank to cancel:
```

### 6. Progress And Speed

After testing, the user found Canvas downloads were too slow. The downloader was updated to:

- Download Canvas files concurrently.
- Show progress counters.
- Use `.part` files during download.
- Let the user tune concurrency with `--download-workers`.

### 7. Duplicate Cleanup

The final workflow became:

```text
download -> check duplicates -> remove duplicates -> upload
```

Duplicate detection is exact-match only. The tool checks file size and SHA-256 hash before removing a duplicate.

## What Made The Workflow Work

The most useful pattern was small, direct feedback:

- "This command failed."
- "This is too slow."
- "I need to choose shells."
- "I want this public on GitHub."
- "I need this documented for colleagues."

Each comment became a concrete improvement.

## What To Copy For Your Own Project

Start with your real workflow, not a technical solution.

Useful structure:

```text
I want to build a tool that does X.
The people using it are Y.
The output should be organized like Z.
These things are required.
These things are optional.
These files or credentials must stay private.
Please document each step so someone else can use it.
```

Then work in stages:

1. Ask for a design.
2. Build a small first version.
3. Try it with real data.
4. Report exact errors.
5. Add safety checks.
6. Add documentation.
7. Publish only after secrets are ignored.

## Important Caution

Do not paste real tokens, passwords, private student data, or confidential institutional data into prompts. Use placeholders.

Good:

```text
My Canvas URL is https://school.instructure.com.
The token is stored in CANVAS_TOKEN.
```

Avoid:

```text
Here is my actual token: ...
```

## Shareable Summary

Canvas Backup is an example of AI-assisted software development where the instructor provided the educational problem and tested the workflow, while the AI assistant handled code generation, documentation, and GitHub publishing. The result is a practical tool that is organized around instructor needs rather than around the API alone.
