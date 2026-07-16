# Ecosystem README Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Android Performance Ecosystem Hub as the first row in one canonical eight-repository table, expose that table through English and Chinese README surfaces in all eight repositories, and push every repository without including unrelated local work.

**Architecture:** Keep the Hub in a dedicated top-level `hub` object and keep the seven lifecycle projects in `projects`. The Hub generator renders `[hub, ...projects]`, validates public README targets from the same metadata, and remains the only source of the marker blocks. Existing bilingual repositories consume the generated blocks directly; Perfetto Tools and Android Internal Wiki gain honest, lightweight companion-language READMEs.

**Tech Stack:** JSON catalog, Python 3 standard library generator/tests, Markdown READMEs, Git worktrees, GitHub remotes.

## Global Constraints

- The Hub is navigation metadata, not an eighth lifecycle project.
- The table order is Hub, TraceFix, Perfetto Tools, SmartPerfetto, Perfetto Skills, Android Performance Blog, Android Internal Wiki, Trace for Blog.
- Every table uses the same four columns: stage, project, purpose, address.
- Android Internal Wiki remains `Coming soon`; no private repository URL, branch, clone URL, or edit URL may appear in the public catalog or table.
- Existing repository versions, features, installation, release, license, and data-policy text remain owned by each repository and are not rewritten.
- SmartPerfetto changes must use an isolated worktree based on the latest `origin/main`; the dirty primary checkout must not be staged, reset, cleaned, or formatted.
- The public deploy repository `/Users/chris/Code/Gracker.github.io` is the Blog README target. The private Blog source worktree and its untracked article assets are out of scope.
- Use one focused documentation commit per repository and push to its existing default branch.
- Push the seven project repositories before the Hub so the Hub push-time remote audit observes the updated public READMEs.
- On this machine use `/usr/bin/python3` for Hub validation because the first PATH Python exits 137 and the Homebrew Python is blocked by a local code-signing failure.

---

### Task 1: Extend the Hub catalog and generator

**Files:**
- Modify: `/Users/chris/Code/android-performance-ecosystem/tests/test_ecosystem.py`
- Modify: `/Users/chris/Code/android-performance-ecosystem/ecosystem.json`
- Modify: `/Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py`
- Modify: `/Users/chris/Code/android-performance-ecosystem/snippets/ecosystem.en.md`
- Modify: `/Users/chris/Code/android-performance-ecosystem/snippets/ecosystem.zh-CN.md`
- Modify: `/Users/chris/Code/android-performance-ecosystem/README.md`
- Modify: `/Users/chris/Code/android-performance-ecosystem/README.zh-CN.md`

**Interfaces:**
- Produces: `render_entries(catalog) -> list[dict[str, Any]]`, ordered as Hub plus seven core projects.
- Produces: `public_targets(catalog)`, including Hub READMEs and every public project README target.
- Produces: canonical English and Chinese marker blocks consumed by Tasks 2-8.

- [ ] **Step 1: Add failing catalog and rendering tests**

Add tests that assert the Hub is separate from `projects`, both languages render ten table lines, the first data row is the Hub, public targets include both Hub READMEs, and Perfetto Tools exposes both language targets:

```python
def test_hub_is_separate_from_seven_core_projects(self):
    self.assertEqual("android-performance-ecosystem", self.catalog["hub"]["id"])
    self.assertEqual(7, len(self.catalog["projects"]))
    self.assertNotIn("android-performance-ecosystem", {
        project["id"] for project in self.catalog["projects"]
    })

def test_each_language_renders_hub_plus_seven_projects(self):
    for language in ecosystem.LANGUAGES:
        snippet = ecosystem.render_snippet(self.catalog, language)
        rows = [line for line in snippet.splitlines() if line.startswith("| ")]
        self.assertEqual(10, len(rows))
        self.assertIn("[Android Performance Ecosystem]", rows[2])

def test_public_targets_include_hub_and_bilingual_perfetto_tools(self):
    targets = list(ecosystem.public_targets(self.catalog))
    keys = {(item["repo"], item["path"], item["language"]) for item in targets}
    self.assertIn(("android-performance-ecosystem", "README.md", "en"), keys)
    self.assertIn(("android-performance-ecosystem", "README.zh-CN.md", "zh-CN"), keys)
    self.assertIn(("perfetto-tools", "README.md", "en"), keys)
    self.assertIn(("perfetto-tools", "README.zh-CN.md", "zh-CN"), keys)
```

- [ ] **Step 2: Run tests and confirm the new tests fail**

Run:

```bash
/usr/bin/python3 -m unittest discover -s tests -v
```

Expected: failures because `catalog["hub"]` and the second Perfetto Tools README target do not exist and the renderer still emits seven data rows.

- [ ] **Step 3: Add the Hub metadata and Chinese Perfetto Tools target**

Add this top-level object before `projects` in `ecosystem.json`:

```json
"hub": {
  "id": "android-performance-ecosystem",
  "name": "Android Performance Ecosystem",
  "stage": {"en": "Navigate", "zh-CN": "导航"},
  "role": {
    "en": "Maintain the shared project map, handoff metadata, generated README navigation, and drift checks.",
    "zh-CN": "维护统一项目地图、交接元数据、README 导航区块与漂移检查。"
  },
  "public_url": "https://github.com/Gracker/android-performance-ecosystem",
  "site_url": null,
  "availability": "public",
  "default_branch": "main",
  "readmes": [
    {"path": "README.md", "language": "en"},
    {"path": "README.zh-CN.md", "language": "zh-CN"}
  ]
}
```

Add `{ "path": "README.zh-CN.md", "language": "zh-CN" }` to the Perfetto Tools `readmes` list.

- [ ] **Step 4: Generalize validation and rendering**

Implement these boundaries in `scripts/ecosystem.py`:

```python
EXPECTED_HUB_ID = "android-performance-ecosystem"


def render_entries(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [catalog["hub"], *catalog["projects"]]
```

Validate the Hub's id, localized stage/role, public GitHub URL, default branch, and two safe README targets without adding its id to `EXPECTED_PROJECT_IDS`. Reuse one helper for public repository fields instead of duplicating Hub/project validation. Change `render_snippet()` to iterate over `render_entries(catalog)`. Change `public_targets()` to yield the Hub first and then public projects.

- [ ] **Step 5: Run the focused tests**

Run:

```bash
/usr/bin/python3 -m unittest discover -s tests -v
```

Expected: tests that compare committed snippets/Hub README blocks still fail as stale; the new catalog structure and row-count tests pass.

- [ ] **Step 6: Regenerate snippets and update the Hub README blocks**

Run:

```bash
/usr/bin/python3 scripts/ecosystem.py write-snippets
```

Replace the English and Chinese marker blocks in the two Hub READMEs with the matching generated snippets. Do not change surrounding Hub ownership or validation documentation.

- [ ] **Step 7: Run Hub validation**

Run:

```bash
/usr/bin/python3 -m unittest discover -s tests -v
/usr/bin/python3 scripts/ecosystem.py validate
git diff --check
```

Expected: all tests pass, catalog validation prints `OK`, and the diff check is silent.

### Task 2: Update TraceFix English and Chinese READMEs

**Files:**
- Modify: `/Users/chris/Code/TraceFix/README.md`
- Modify: `/Users/chris/Code/TraceFix/README_zh.md`

**Interfaces:**
- Consumes: canonical marker blocks from Task 1.

- [ ] Fetch `origin/master`, confirm the tracked worktree is clean and aligned, and replace only the two marker blocks.
- [ ] Validate both files with `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py check-readmes --target en=/Users/chris/Code/TraceFix/README.md --target zh-CN=/Users/chris/Code/TraceFix/README_zh.md`, run `git diff --check`, and confirm no TraceFix version/install text changed.
- [ ] Commit with `docs: add ecosystem hub to project map` but do not push until the independent review gate completes.

### Task 3: Add Perfetto Tools Chinese navigation companion

**Files:**
- Modify: `/Users/chris/Code/.worktrees/perfetto-tools-ecosystem/README.md`
- Create: `/Users/chris/Code/.worktrees/perfetto-tools-ecosystem/README.zh-CN.md`

**Interfaces:**
- Consumes: both canonical marker blocks from Task 1.
- Produces: the public Chinese README target declared in `ecosystem.json`.

- [ ] Fetch `origin/main`, confirm the ecosystem worktree matches it, add `[简体中文](README.zh-CN.md)` below the English title, and replace the English marker block.
- [ ] Create `README.zh-CN.md` with `[English](README.md)`, a concise description that Perfetto Tools fixes the capture/toolchain baseline for Perfetto Trace, FPS, and Simpleperf, the exact output of `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py render --language zh-CN`, and a final note linking `README.md` for complete installation, commands, compatibility, and troubleshooting.
- [ ] Run `.venv/bin/python -m pytest tests/ -v`, `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py check-readmes --target en=/Users/chris/Code/.worktrees/perfetto-tools-ecosystem/README.md --target zh-CN=/Users/chris/Code/.worktrees/perfetto-tools-ecosystem/README.zh-CN.md`, and `git diff --check`.
- [ ] Commit with `docs: add bilingual ecosystem navigation` but do not push yet.

### Task 4: Update SmartPerfetto in an isolated worktree

**Files:**
- Modify: `/Users/chris/Code/.worktrees/SmartPerfetto-ecosystem-readme/README.md`
- Modify: `/Users/chris/Code/.worktrees/SmartPerfetto-ecosystem-readme/README.zh-CN.md`

**Interfaces:**
- Consumes: canonical marker blocks from Task 1.

- [ ] Fetch `origin/main` from the primary repository without modifying its dirty worktree.
- [ ] Create `/Users/chris/Code/.worktrees/SmartPerfetto-ecosystem-readme` on branch `docs/ecosystem-readme-navigation` from `origin/main`.
- [ ] Replace only the English and Chinese marker blocks in the isolated worktree.
- [ ] Run the documented docs-only gate `git diff --check`, then run `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py check-readmes --target en=/Users/chris/Code/.worktrees/SmartPerfetto-ecosystem-readme/README.md --target zh-CN=/Users/chris/Code/.worktrees/SmartPerfetto-ecosystem-readme/README.zh-CN.md`.
- [ ] Commit with `docs: add ecosystem hub to project map` but do not push yet.

### Task 5: Update Perfetto Skills English and Chinese READMEs

**Files:**
- Modify: `/Users/chris/Code/SmartPerfetto/Perfetto-Skills/README.md`
- Modify: `/Users/chris/Code/SmartPerfetto/Perfetto-Skills/README.zh-CN.md`

**Interfaces:**
- Consumes: canonical marker blocks from Task 1.

- [ ] Fetch `origin/main`, require a clean aligned worktree, and replace only both marker blocks.
- [ ] Run `uv run python tools/check_cross_repo_impact.py --repository perfetto-skills --base "$(git merge-base HEAD origin/main)"`; record the README-only decision emitted by the tool.
- [ ] Run `uv run python tools/verify.py`, `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py check-readmes --target en=/Users/chris/Code/SmartPerfetto/Perfetto-Skills/README.md --target zh-CN=/Users/chris/Code/SmartPerfetto/Perfetto-Skills/README.zh-CN.md`, and `git diff --check`.
- [ ] Commit with `docs: add ecosystem hub to project map` but do not push yet.

### Task 6: Update Android Performance Blog public READMEs

**Files:**
- Modify: `/Users/chris/Code/Gracker.github.io/README.md`
- Modify: `/Users/chris/Code/Gracker.github.io/README.zh-CN.md`

**Interfaces:**
- Consumes: canonical marker blocks from Task 1.

- [ ] Fetch `origin/master`, require a clean aligned worktree, and replace only both marker blocks.
- [ ] Confirm `AndroidPerformance.com` remains the primary address in the Blog row, run `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py check-readmes --target en=/Users/chris/Code/Gracker.github.io/README.md --target zh-CN=/Users/chris/Code/Gracker.github.io/README.zh-CN.md`, and run `git diff --check`.
- [ ] Commit with `docs: add ecosystem hub to project map` but do not push yet.

### Task 7: Add Android Internal Wiki English navigation companion

**Files:**
- Modify: `/Users/chris/Code/android-internals-wiki/README.md`
- Create: `/Users/chris/Code/android-internals-wiki/README.en.md`

**Interfaces:**
- Consumes: both canonical marker blocks from Task 1.
- Preserves: public `Coming soon` state with no private repository metadata.

- [ ] Fetch `origin/master`, require a clean aligned worktree, add `[English](README.en.md)` to the Chinese README, clarify that only the navigation companion exists before v1.0, and replace the Chinese marker block.
- [ ] Create `README.en.md` with `[简体中文](README.md)`, an English summary that the alpha knowledge base covers App, Framework, Native, and Kernel, the exact output of `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py render --language en`, and an explicit note that the full English book remains planned after v1.0.
- [ ] Record Wiki README-specific verification as `NOT CONFIGURED`, run `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py check-readmes --target en=/Users/chris/Code/android-internals-wiki/README.en.md --target zh-CN=/Users/chris/Code/android-internals-wiki/README.md`, search `/Users/chris/Code/android-performance-ecosystem/ecosystem.json` and its snippets to prove that no private Wiki URL appears, and run `git diff --check`.
- [ ] Commit with `docs: add bilingual ecosystem navigation` but do not push yet.

### Task 8: Update Trace for Blog English and Chinese READMEs

**Files:**
- Modify: `/Users/chris/Code/SystraceForBlog/README.md`
- Modify: `/Users/chris/Code/SystraceForBlog/README.zh-CN.md`

**Interfaces:**
- Consumes: canonical marker blocks from Task 1.

- [ ] Fetch `origin/master`, require a clean aligned worktree, and replace only both marker blocks.
- [ ] Run `/usr/bin/python3 scripts/validate_catalog.py`, `/usr/bin/python3 -m unittest discover -s tests -v`, `/usr/bin/python3 /Users/chris/Code/android-performance-ecosystem/scripts/ecosystem.py check-readmes --target en=/Users/chris/Code/SystraceForBlog/README.md --target zh-CN=/Users/chris/Code/SystraceForBlog/README.zh-CN.md`, and `git diff --check`.
- [ ] Commit with `docs: add ecosystem hub to project map` but do not push yet.

### Task 9: Independent review, revision, and push closure

**Files:**
- Review: all commits and README marker blocks from Tasks 1-8.

**Interfaces:**
- Consumes: eight focused repository commits.
- Produces: eight updated default remote branches and a passing Hub remote drift audit.

- [ ] Dispatch one read-only reviewer to check architecture boundaries, bilingual consistency, private Wiki leakage, repository targeting, and unrelated-diff isolation. The reviewer must not edit files.
- [ ] Revise confirmed findings with `apply_patch`, rerun affected repository checks, amend only the corresponding focused commit, and repeat `git diff --check`.
- [ ] Push the project repositories with these exact commands from their respective worktrees: `git push origin master` for TraceFix, Blog, Wiki, and Trace for Blog; `git push origin HEAD:main` for the Perfetto Tools ecosystem worktree and isolated SmartPerfetto worktree; `git push origin main` for Perfetto Skills.
- [ ] Confirm each pushed remote branch resolves to the intended commit before continuing.
- [ ] Commit Task 1 Hub implementation as `feat: include hub in ecosystem README map`, keeping the already committed design and plan documents as separate commits.
- [ ] Run Hub tests and local validation again, then push Hub `main` last.
- [ ] Run `/usr/bin/python3 scripts/ecosystem.py check-readmes --remote` and expect `OK`.
- [ ] Check the Hub GitHub Actions run and wait for its `Verify ecosystem` job to pass.
- [ ] Confirm all eight local repositories compare cleanly with their pushed default remote branches; remove the temporary SmartPerfetto worktree and local task branch without touching the dirty primary checkout.
