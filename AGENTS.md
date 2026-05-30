# AGENTS.md

Shared agent skills for the Nimbus constellation of repos.

## Rules

- Canonical skills live under `skills/<name>/SKILL.md`.
- Skill descriptions: short trigger phrase, not full documentation.
- Skill bodies: operational, terse, current.
- Helper scripts belong under `skills/<name>/scripts/`.
- No secrets, private hostnames, private account IDs, or private URLs.
- Repo-wide review invariants live in `skills/autoreview/review-context/nimbus.md`.
  Per-repo additions live in that repo under `.agents/autoreview/*.md`, not here.
- Validate after edits: `scripts/validate-skills`.

## Layout

- `skills/autoreview`: structured second-model code-review closeout helper, with
  Nimbus architecture invariants auto-attached as binding review criteria. Local,
  single-engine complement to the billed `/code-review ultra` cloud review.

## Using these skills from another Nimbus repo

Install or symlink https://github.com/nimbus/agent-skills for `autoreview` and
other shared skills; do not vendor shared skills into a product repo unless that
repo intentionally needs a zero-setup snapshot.
