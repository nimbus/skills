# Nimbus Agent Skills

Shared skills for coding agents (Claude Code, Codex) that work across the Nimbus
constellation of repos. Write a workflow once, reuse it in every repo, and avoid
hand-copying long `SKILL.md` files.

## The Nimbus constellation

These skills are meant to be installed once and used in any of the Nimbus repos
under `~/src/github.com/nimbus/`:

| Repo | What it is |
| --- | --- |
| `nimbus` | The Convex-compatible backend: Rust workspace + npm monorepo |
| `deno` | Canonical Deno-family fork (Node-compatible runtime) |
| `rusty_v8` | Matching V8 binding fork |
| `bun` | Bun/JSC engine fork (alternate runtime lane) |
| `desktop` | Desktop app / computer-use shell |
| `machine-os` | Outer Linux VM image for macOS dev sandboxing |
| `nimbus-libkrun` | Unified sandbox backend fork (libkrun + muvm + snapshot/fork) |
| `nimbus-crun` | Container runtime fork (crun) for in-VM workloads |
| `nimbus-dynamodb-adapter` | Adapter worktree branch |
| `homebrew-tap` | Distribution tap |
| `claude-skill-convex`, `codex-plugin-convex` | Agent tooling for Convex |

How they connect: `nimbus` is the product. `deno`/`rusty_v8`/`bun` are the JS
engines it embeds in `nimbus-runtime`. `nimbus-libkrun`/`nimbus-crun`/`machine-os`
are the sandbox/isolation stack. `desktop` is the client. The forks follow an
unpin → fix → verify → repin workflow against the published tags consumed by
`nimbus`. A review skill that understands the `nimbus` invariants is useful in
all of them, which is why it lives here rather than vendored into one repo.

## Included skills

- `autoreview`: structured second-model code-review closeout, with the Nimbus
  architecture invariants auto-attached as binding review criteria.

## Quick start

```sh
git clone https://github.com/nimbus/agent-skills.git
cd agent-skills
scripts/install-skills --list                 # list skills
scripts/install-skills --dry-run              # preview
scripts/install-skills                        # symlink all into ~/.agents/skills
scripts/install-skills autoreview             # install only selected skills
scripts/install-skills --target ~/.codex/skills autoreview
scripts/install-skills --mode copy --target ~/.agents/skills
scripts/install-skills --force autoreview     # replace an existing install
```

Symlinks are best for local development because changes in this checkout are
immediately visible. Copies are better for portable or locked-down setups.

## Codex and Claude

For Codex, symlink this repo's `skills/` directory into `~/.codex/skills`:

```sh
mkdir -p ~/.codex/skills
ln -sfn "$(pwd)/skills" ~/.codex/skills/agent-skills
```

Installing a single skill directly also works when you do not want the grouped
`agent-skills` directory:

```sh
mkdir -p ~/.codex/skills
ln -sfn "$(pwd)/skills/autoreview" ~/.codex/skills/autoreview
```

For Claude Code, symlink the skill into `~/.claude/skills`:

```sh
mkdir -p ~/.claude/skills
ln -sfn "$(pwd)/skills/autoreview" ~/.claude/skills/autoreview
```

If `~/.claude/skills` already points at another shared skills folder, add
symlinks inside that folder instead.

The `autoreview` helper sends its frozen git bundle and review context to the
selected review engine. For private workspaces, run it only where that outbound
review is approved. From inside an active Codex or Claude session, invoking the
same external engine can become a nested-agent call and may be blocked by local
sandboxing or data-exfiltration policy; in that case, use the skill rubric for a
manual repo-grounded review and report that the structured helper was blocked.
Nested Codex is detected with `CODEX_SANDBOX`/`CODEX_THREAD_ID` and refused by
default; set `AUTOREVIEW_ALLOW_NESTED_CODEX=1` only for an intentional approved
nested run.

Recommended one-liner for Nimbus repo `AGENTS.md` files:

```text
Shared agent workflows: install or symlink https://github.com/nimbus/agent-skills for `autoreview` and other common skills; do not vendor shared skills here unless this repo intentionally needs a zero-setup snapshot.
```

## Zero-setup repos

Some important repos may need to work for contributors who cloned only that repo
and never installed shared skills. Those repos can vendor a generated snapshot
under `.agents/skills/`, but the snapshot is a distribution artifact, not the
source of truth:

- edit canonical skills here first
- sync snapshots downstream after review
- keep downstream copies small in number
- add provenance and drift checks when a repo vendors a snapshot

## Per-repo review criteria

`autoreview` always attaches `skills/autoreview/review-context/nimbus.md` (the
repo-wide invariants). Any Nimbus repo can add its own criteria by dropping
`*.md` files under `.agents/autoreview/` in that repo; the helper appends them
automatically. Example: fork-health guardrails in `deno`, capability-profile
rules in `nimbus-libkrun`.

## Repository layout

```text
skills/
  autoreview/
    SKILL.md
    review-context/nimbus.md     # auto-attached review criteria
    scripts/autoreview           # Python helper
    scripts/test-review-harness* # engine smoke calibration
scripts/
  install-skills                 # symlink/copy skills into an agent skills dir
  validate-skills                # check each SKILL.md frontmatter
```

## Validate

```sh
scripts/validate-skills
python3 -m py_compile skills/autoreview/scripts/autoreview skills/autoreview/scripts/test-review-harness.py
bash -n skills/autoreview/scripts/test-review-harness
```

## Editing rules

- Keep descriptions short and useful for routing.
- Keep skill bodies operational, not essay-like.
- No secrets, private hostnames, or private URLs.
- Prefer helper scripts for repeatable command logic.
- Do not update vendored downstream snapshots by hand. Update this repo, then
  sync.

## Attribution & license

The `autoreview` helper and harness are adapted from
[`openclaw/agent-skills`](https://github.com/openclaw/agent-skills) (MIT). The
review prompt, target selection, structured-output schema, validation, and
panel logic are upstream; the Nimbus fork adds auto-attached repo invariants
(`--no-default-context`, `.agents/autoreview/*.md` discovery, the pre-launch and
architecture criteria) and removes OpenClaw-specific tooling references.

MIT. See [LICENSE](LICENSE).
