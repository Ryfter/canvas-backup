# Prompt Playbook

These are cleaned-up example prompts based on the Canvas Backup build process. They are safe to share because they do not include real tokens, credentials, private course data, or student data.

The exact wording does not need to be copied. The important part is the structure: explain the goal, explain the users, explain the constraints, and ask for a concrete next step.

## 1. Start With The Real Workflow

```text
I want to design a project that will go into my Canvas shells and download everything to Google Drive.

I want to retain the folder structure that is in the shell, as well as the module layout and the modules themselves.

The top-level folder should be year, then semester, then class shell. Sometimes I combine two or three sections of one class into one shell, so use the shell name.

I want all items and due dates pulled down. If Google Drive is too hard for the first version, downloading locally to my hard drive is acceptable.
```

Why this worked:

- It described the real job.
- It gave the folder structure.
- It explained combined course sections.
- It allowed a simpler first version.

## 2. Ask For A First Working Version

```text
This design sounds good. Please build the first working version.

Start with local downloads. Include configuration, a command-line interface, and tests. Keep Google Drive as a second step.
```

Why this worked:

- It narrowed the first build.
- It made testing part of the request.
- It avoided trying to solve everything at once.

## 3. Clarify Secret Handling

```text
Should the Canvas token be in a .env file?
```

Follow-up:

```text
Sounds good. Please make the .gitignore. .env is there.
```

Why this worked:

- It turned a security question into a concrete implementation.
- It led to `.env`, `.gitignore`, and safer documentation.

## 4. Ask For Help With API Setup

```text
I need these Google Drive files:

credentials_file = "secrets/google-client-secret.json"
token_file = "secrets/google-token.json"

How do I get those?
```

Why this worked:

- It named the confusing files.
- It made the setup problem specific.
- It separated the downloaded Google client secret from the generated token file.

## 5. Report Exact Command Errors

```text
I ran:

<canvas-backup> --config config.local.toml sync-drive --archive "~/CanvasArchive/2026/Spring/ITM370"

It returned:

invalid choice: 'sync-drive'
```

Why this worked:

- It included the exact command.
- It included the exact error.
- It made the missing command obvious.

## 6. Improve The Workflow

```text
I would like it to check if the folder is there, and if it is not, create the folder.

I really want to run the command and have it download the past four years of classes.
```

Why this worked:

- It moved from one-course use to a bulk workflow.
- It described what should happen automatically.

## 7. Keep Human Choice In The Loop

```text
I would like to choose the shells.

Unfortunately, I am listed as teacher on additional shells, and I do not want those.
```

Why this worked:

- It corrected an automation risk.
- It made the tool safer for real use.
- It led to interactive shell selection.

## 8. Ask For Public Documentation

```text
Fully document everything.

I want this uploaded to GitHub with a new repository. Call it Canvas Backup.

I also need it fully documented. Make it really easy to complete.
```

Why this worked:

- It asked for a complete handoff, not just code.
- It named the repository.
- It clarified the audience.

## 9. Give Performance Feedback

```text
This download through Canvas is horribly slow. We are talking 300 MB in 30 minutes slow.

I should be downloading at much faster speeds.
```

Why this worked:

- It gave a measurable performance problem.
- It led to concurrent downloads and progress counters.

## 10. Add A Data-Cleanup Workflow

```text
Once downloaded, I need to check what duplicates there are.

The workflow should be: download files, check for duplicates, remove duplicates, and then upload.

When I do a new sync, it should check for duplicates then.
```

Why this worked:

- It stated the exact desired sequence.
- It said when duplicate checks should happen.
- It became an automatic pre-upload step.

## Reusable Prompt Template

```text
I want to build a tool for [audience] that helps with [workflow].

The tool should:
- [required behavior]
- [required behavior]
- [required behavior]

The output should be organized like:
[folder structure or example output]

Important constraints:
- [privacy/security constraint]
- [must-have workflow]
- [optional feature]

Please start by designing the project, then build a first working version with tests and clear documentation.
```

## Prompting Tips For Less Technical Users

- Say what you are trying to accomplish in normal language.
- Include examples of folder names, files, or outputs.
- Share exact error messages.
- Ask for one improvement at a time.
- Ask the assistant to explain setup steps for a beginner.
- Ask the assistant to protect secrets before publishing.

## What Not To Share

Do not include:

- Canvas tokens.
- Google client secrets.
- Google token files.
- Student names, grades, submissions, or private records.
- Screenshots showing private course data.

Use placeholders instead:

```text
CANVAS_TOKEN=your-token-here
https://your-school.instructure.com
```
