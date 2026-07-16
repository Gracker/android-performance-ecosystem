# Android Performance Ecosystem README Navigation Design

## Goal

Every repository in the Android Performance Ecosystem must expose the same
English and Simplified Chinese project table in its root README surface. The
table must include the navigation Hub itself plus the seven core projects,
while preserving each repository's independent release, runtime, license, and
visibility boundaries.

The eight repositories are:

1. Android Performance Ecosystem
2. TraceFix
3. Perfetto Tools
4. SmartPerfetto
5. Perfetto Skills
6. Android Performance Blog
7. Android Internal Wiki
8. Trace for Blog

## Current State

`ecosystem.json` already defines the seven core projects and generates one
English and one Simplified Chinese marker block. Those blocks are present in
the existing public README targets, and the current remote drift check passes.

The remaining gaps are:

- the navigation Hub does not appear as a row in the generated table;
- Perfetto Tools has only an English root README;
- Android Internal Wiki has only a Chinese root README and intentionally keeps
  its full English content deferred until v1.0;
- the Hub is validated locally but is not part of the remote README target
  iterator.

## Considered Approaches

### 1. Add the Hub to the `projects` array

This produces eight rows with the smallest code change, but it incorrectly
turns the navigation repository into an eighth lifecycle project. Existing
documentation deliberately distinguishes the Hub from the seven core
projects. This approach is rejected.

### 2. Keep a separate Hub object and render it before the seven projects

Add a localized `hub` object to `ecosystem.json`, validate it independently,
and render it as the first table row. The `projects` array remains the source
of truth for the seven lifecycle projects. This preserves the current
architecture while satisfying the eight-row navigation requirement.

This is the selected approach.

### 3. Hardcode a Hub row in every README

This avoids changing the catalog schema but creates sixteen independently
editable copies and weakens drift detection. This approach is rejected.

## Catalog and Generator Design

`ecosystem.json` gains a top-level `hub` object with:

- stable id and display name;
- localized `stage` and `role` fields;
- public URL, default branch, and English/Chinese README targets.

The Hub row uses `Navigate` / `导航` as its stage. Its role explains that the
repository owns the shared project map, handoff metadata, generated README
block, and drift validation. It does not claim ownership of project versions,
capabilities, releases, or licenses.

`scripts/ecosystem.py` will:

- validate the Hub separately from the seven core projects;
- render the Hub first, followed by the existing project order;
- keep the table columns `Stage / Project / Purpose / Address` and their
  Chinese equivalents;
- include Hub README targets in remote drift checks;
- continue hiding the Android Internal Wiki repository URL and branch while
  its availability remains `coming_soon`.

The generated table contains ten Markdown table lines: one header, one
separator, and eight repository rows.

## README Language Design

Repositories that already have two root README files keep their current
language naming and receive the matching generated block in each file.

Two repositories need a lightweight companion language surface:

- Perfetto Tools gains `README.zh-CN.md`. It contains a Chinese project
  summary, the Chinese ecosystem table, and a clear link to `README.md` for
  complete setup, command, compatibility, and troubleshooting documentation.
- Android Internal Wiki gains `README.en.md`. It contains an English alpha
  summary, the English ecosystem table, and a clear link to `README.md`. It
  explicitly states that the full English book remains planned after v1.0.

The existing primary README in each repository gains a language switch link.
The companion files must not pretend to be full translations.

## Repository Targets

| Repository | English target | Chinese target |
| --- | --- | --- |
| Android Performance Ecosystem | `README.md` | `README.zh-CN.md` |
| TraceFix | `README.md` | `README_zh.md` |
| Perfetto Tools | `README.md` | `README.zh-CN.md` (new) |
| SmartPerfetto | `README.md` | `README.zh-CN.md` |
| Perfetto Skills | `README.md` | `README.zh-CN.md` |
| Android Performance Blog | `README.md` | `README.zh-CN.md` |
| Android Internal Wiki | `README.en.md` (new) | `README.md` |
| Trace for Blog | `README.md` | `README.zh-CN.md` |

## Privacy and Ownership Boundaries

- Android Internal Wiki remains `Coming soon` in every generated table.
- No private repository URL, clone URL, branch, or edit link enters the Hub
  catalog or public README copies.
- Every project remains authoritative for its own version, installation,
  feature inventory, release state, license, and data policy.
- The Hub owns only the shared navigation metadata and marker-block contract.

## Working Tree Isolation

The SmartPerfetto checkout currently contains extensive unrelated work. Its
README changes will be made in a dedicated worktree based on the latest
`origin/main`, committed independently, and pushed without including any file
from the existing dirty checkout.

Other repositories may be edited in place only when their tracked worktree is
clean and aligned with its default remote branch. Untracked article assets in
the private Blog source repository are out of scope; the ecosystem target is
the public `Gracker.github.io` repository.

## Validation

Before any push:

1. Run Hub unit tests and catalog validation with an executable local Python.
2. Validate every local README marker block against the generated language
   snippet, including the private Wiki through explicit local targets.
3. Run each affected repository's documented README/docs verification entry
   when one exists.
4. Run `git diff --check` in every repository.
5. Perform an independent read-only review of the final cross-repository diff.

After pushes:

1. Push the seven project repositories first.
2. Push the Hub last so its GitHub Actions remote drift check observes the new
   README blocks everywhere.
3. Run `check-readmes --remote` from the Hub.
4. Confirm every default remote branch points to the intended commit and has a
   clean local comparison.

## Commit and Push Strategy

Use one focused documentation commit per repository. Do not combine unrelated
local changes. Push each commit to that repository's existing default branch:

- `main`: Hub, Perfetto Tools, SmartPerfetto, Perfetto Skills
- `master`: TraceFix, Android Performance Blog, Android Internal Wiki,
  Trace for Blog

The Hub is pushed last because its workflow checks all public README copies on
every push to `main`.
