---
name: pr-description
description: Draft pull request descriptions by comparing the current branch against origin/main and filling the repository PR template. Use when the user asks for a PR description, PR summary, release note-style change summary for a branch, or wants the repo's pull request template completed from git history and the working tree.
---

# Pr Description

## Overview

Compare the current branch with `origin/main`, inspect the repository PR template, and draft a concise PR description grounded in actual file changes, commits, and test evidence.

## Workflow

1. Confirm the repository root and read `.github/pull_request_template.md` if it exists.
2. Run `scripts/collect_pr_context.sh` from the repo root to gather:
   - merge base against `origin/main`
   - changed files and status
   - commit subjects unique to the branch
   - diff stats
   - the PR template contents
3. Read the changed files that matter. Do not write a PR description from file names alone.
4. Fill the template with concrete changes, user-visible impact, and risks derived from the diff.
5. Be strict about testing:
   - Mark a checkbox as checked only if that command was actually run and passed in the current session.
   - Leave items unchecked if they were not run.
   - Use `Other:` for manual verification, deployment checks, or nonstandard validation.

## Template Rules

- Preserve the repository template headings and checklist structure.
- Keep `## Summary` to 1 short paragraph.
- Use flat bullets under `## What Changed`.
- Keep `## Risks` specific. Mention migrations, env changes, deploy-script changes, or cross-service coupling when relevant.
- For `## Screenshots or Demo`, add a short note when there is no UI impact instead of inventing screenshots.
- For `## Checklist`, check an item only when the diff or session evidence supports it.

## Writing Rules

- Prefer behavior and intent over low-signal file inventories.
- Mention operational fixes separately from feature work when both happened.
- Call out unverified assumptions plainly.
- If the branch includes setup, deploy, or infrastructure changes, include them in both `What Changed` and `Risks`.
- If the template file is missing, use this fallback structure:
  - `## Summary`
  - `## What Changed`
  - `## Testing`
  - `## Screenshots or Demo`
  - `## Risks`
  - `## Checklist`

## Output Pattern

Return the completed Markdown only, unless the user explicitly asks for commentary about how it was generated.
