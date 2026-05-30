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
scripts/install-skills --list           # list skills
scripts/install-skills --dry-run        # preview
scripts/install-skills                  # symlink all into ~/.claude/skills
scripts/install-skills autoreview       # just one
```

### Claude Code

```sh
mkdir -p ~/.claude/skills
ln -sfn "$(pwd)/skills/autoreview" ~/.claude/skills/autoreview
```

### Codex

```sh
mkdir -p ~/.codex/skills
ln -sfn "$(pwd)/skills" ~/.codex/skills/agent-skills
```

Symlinks are best for local development (changes here are immediately visible).
Use `--mode copy` for portable or locked-down setups.

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

## Attribution & license

The `autoreview` helper and harness are adapted from
[`openclaw/agent-skills`](https://github.com/openclaw/agent-skills) (MIT). The
review prompt, target selection, structured-output schema, validation, and
panel logic are upstream; the Nimbus fork adds auto-attached repo invariants
(`--no-default-context`, `.agents/autoreview/*.md` discovery, the pre-launch and
architecture criteria) and removes OpenClaw-specific tooling references.

MIT. See [LICENSE](LICENSE).
