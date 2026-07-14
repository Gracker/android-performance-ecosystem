# Contributing

`ecosystem.json` is the source of truth only for cross-project metadata: names,
roles, public entry points, default branches, and README targets.
Each linked repository remains the source of truth for its own versions,
capabilities, installation, release, and license.

When changing the catalog:

1. Keep each project at one stable stage and describe its architectural boundary.
2. Use `public_url: null` and `availability: coming_soon` for non-public projects.
3. Never add a private repository slug, clone URL, edit URL, or access token.
4. Run `python3 scripts/ecosystem.py write-snippets`.
5. Copy the generated marker block to affected project READMEs.
6. Run `python3 -m unittest discover -s tests -v` and
   `python3 scripts/ecosystem.py validate`.
7. After public repositories are updated, run
   `python3 scripts/ecosystem.py check-readmes --remote`.

Adding a new core project requires a distinct lifecycle role, a maintained
public entry point or explicit coming-soon state, an owner, a license boundary,
and at least one concrete handoff to another project. Adjacent tools should not
be promoted to the core table only to make the catalog longer.
