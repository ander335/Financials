---
name: sync-skill-shims
description: Use when the user asks to sync, update, or refresh skill shims, or when skills in the common folder or project skills folder may have changed. Creates missing shim skills in .claude/skills/ and updates any shims whose description has drifted from the original.
---

# Sync Skill Shims

Maintain thin shim skills in `.claude/skills/` that mirror every skill from:
- **Common skills**: `../Common/AI/skills/` (one level above this repo)
- **Project skills**: `skills/` (this repo's own skills folder)

Each shim copies the original skill's `description` frontmatter field verbatim and contains a single body line redirecting to the real skill file. No other content is duplicated.

## Shim format

```markdown
---
name: <skill-name>
description: <exact description from original SKILL.md>
---

Read and follow the full skill at `<relative-path-from-project-root-to-original>`.
```

Relative paths to use in the body (from the project root, i.e. `G:\projects\Financials`):
- Common skill: `../Common/AI/skills/<name>/SKILL.md`
- Project skill: `skills/<name>/SKILL.md`

## Steps

1. **Discover source skills**
   - List all subdirectories under `../Common/AI/skills/` that contain a `SKILL.md`.
   - List all subdirectories under `skills/` that contain a `SKILL.md` (or `skill.md` — case-insensitive).

2. **For each source skill**, read its frontmatter to extract `name` and `description`.

3. **Check the shim** at `.claude/skills/<name>/SKILL.md`:
   - **Missing** → create it using the shim format above.
   - **Exists, description matches** → no action needed; note it as in-sync.
   - **Exists, description differs** → update only the `description` line in the shim frontmatter.

4. **Orphan check** — list all folders under `.claude/skills/`. If any folder has no corresponding source skill in either location, flag it to the user (do not delete automatically).

5. **Report** a short summary: created N, updated N, in-sync N, flagged N orphans.
