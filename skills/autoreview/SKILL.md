---
name: autoreview
description: "Run a structured second-model code review (Codex default, Claude optional) as a closeout check on a local, branch, or commit diff across any Nimbus repo before commit or ship."
---

# Auto Review

Run the bundled structured review helper as a local closeout check. It freezes a
git change bundle, sends it to one selected review engine with the Nimbus review
criteria attached, validates one structured result, and gates on findings.

This is the **local, single-engine** complement to `/code-review ultra` (the
billed, user-triggered multi-agent cloud review of the current branch or a PR).
Use `autoreview` yourself during a task; reach for `/code-review ultra` when the
user explicitly asks for the heavyweight cloud pass. Do not invoke
`/code-review ultra` on the user's behalf.

The default engine is Codex. Because the agent doing the work is usually Claude,
a Codex review is a genuine second model, not an echo — keep it as the default
closeout engine. `--engine claude` (or `AUTOREVIEW_ENGINE=claude`) is fully
supported when you want Claude-on-Claude or Codex is unavailable.

Use when:

- the user asks for Codex review / Claude review / autoreview / second-model review
- after non-trivial code edits, before final/commit/ship
- reviewing a local branch, PR branch, or landed commit after fixes
- in any Nimbus repo: `nimbus`, `deno`, `rusty_v8`, `bun`, `desktop`,
  `machine-os`, `nimbus-libkrun`, `nimbus-crun`, or an adapter worktree

## Contract

- Treat review output as advisory. Never blindly apply it.
- Verify every finding by reading the real code path and adjacent files.
- Read dependency docs/source/types when the finding depends on external behavior.
- Reject unrealistic edge cases, speculative risks, broad rewrites, and fixes that over-complicate the codebase.
- Prefer small fixes at the right ownership boundary; no refactor unless it clearly improves the bug class.
- Keep going until structured review returns no accepted/actionable findings.
- If a review-triggered fix changes code, rerun focused tests and rerun the structured review helper.
- The helper auto-attaches the Nimbus review criteria (`review-context/nimbus.md` plus any repo-local `.agents/autoreview/*.md`). Trust findings that cite a real invariant violation — zero-I/O `nimbus-core`, zero-workspace-deps `nimbus-runtime`, single mutation path, storage atomicity, bundle integrity, optional schema, pre-launch no-compat policy, behavior-asserting tests, modularity/naming. Do not dismiss them as style.
- Never switch or override the requested review engine/model. If the review hits model capacity, retry the same command a few times with the same engine/model.
- Be patient with large bundles. Structured review can take up to 30 minutes while the model call is active, especially with tools or web search.
- Treat heartbeat lines like `review still running: ... elapsed=... pid=...` as healthy progress, not a hang. Pass `--stream-engine-output` when live engine text is useful; Codex and Claude filter tool/file chatter, other engines pass raw output through.
- Do not kill a review just because it has been quiet for 2-5 minutes, or because it is still running under the 30-minute window. Inspect the process only after missing multiple expected heartbeats, after 30 minutes, or after an obviously failed subprocess.
- Tools are useful in review mode. The helper allows read-only inspection tools and web search by default so reviewers can check dependency contracts, upstream docs (Deno/V8/Convex), and current behavior.
- Security perspective is always included, but it should not cripple legitimate functionality. Report security findings only when the change creates a concrete, actionable risk or removes an important safety check (e.g. the SHA-256 bundle integrity check, a trust boundary in `nimbus-auth`/`nimbus-server`).
- For regression provenance, use `git blame` / `git log` and, when a PR is traceable, `gh pr view`. Keep roles separate: blamed code author, blamed PR author, merger/committer, current author, and PR/date. If no PR is traceable, use the blamed commit SHA, date, and author. Do not guess a merger or frame missing PR metadata as a finding.
- Do not invoke nested reviewers, reviewer panels, or `/code-review ultra` from inside the review. The helper builds one bundle, calls one selected engine, validates one structured result, and stops.
- Stop as soon as the helper exits 0 with no accepted/actionable findings. Do not run an extra review just to get a nicer "clean" line or clearer closeout wording.
- Multi-reviewer panels are opt-in only. Use them when explicitly requested or when risk justifies the extra spend; you still verify every accepted finding before fixing.
- If rejecting a finding as intentional, add a brief inline code comment only when it explains a real invariant or ownership decision future reviewers should know.
- Do not push just to review. Push only when the user requested push/ship/PR update. Respect each repo's branching norms (Nimbus `nimbus` is pre-launch and often commits to `main`; forks like `deno`/`rusty_v8` follow the tag/repin workflow in the Nimbus routing docs).

## Pick Target

Dirty local work (unstaged/staged/untracked in the current checkout):

```bash
<autoreview-helper> --mode local
```

`--mode uncommitted` is an alias for `--mode local`. A clean local review only
proves there is no local patch; for committed/pushed/PR work, point at the
commit or branch diff instead — do not force a dirty mode.

Branch/PR work:

```bash
<autoreview-helper> --mode branch --base origin/main
```

Optional review context is first-class:

```bash
<autoreview-helper> --mode branch --base origin/main --prompt-file /tmp/review-notes.md --dataset /tmp/evidence.json
```

If an open PR exists, use its actual base:

```bash
base=$(gh pr view --json baseRefName --jq .baseRefName)
<autoreview-helper> --mode branch --base "origin/$base"
```

Committed single change (already-landed work on `main`, where a branch diff is
usually empty after push):

```bash
<autoreview-helper> --mode commit --commit HEAD
```

## Parallel Closeout

Format first if formatting can change line locations, then run the canonical
Nimbus verification concurrently with the review:

```bash
# Rust crate, focused:
<autoreview-helper> --mode local --parallel-tests "cargo test -p nimbus-engine"
# Workspace gate:
<autoreview-helper> --mode branch --base origin/main --parallel-tests "make check"
# JS monorepo:
<autoreview-helper> --mode local --parallel-tests "npm run typecheck"
```

Prefer the narrowest faithful command (see
`docs/architecture/testing/ci-failure-investigation.md`). If tests or review
force edits, rerun the affected tests and rerun review until no
accepted/actionable findings remain, then stop.

## Review Panels

Run multiple reviewers against one frozen bundle (opt-in):

```bash
<autoreview-helper> --reviewers codex,claude
<autoreview-helper> --panel                       # Codex + Claude
<autoreview-helper> --reviewers codex:gpt-5.1:high,claude:sonnet:max
```

Codex maps thinking to `model_reasoning_effort` (`low|medium|high|xhigh`);
Claude maps thinking to `--effort` (also accepts `max`). Engines without a real
thinking knob reject `--thinking`.

## Repo-local criteria

The bundled `review-context/nimbus.md` carries the repo-wide invariants. To add
criteria for a specific repo (e.g. fork-health rules in `deno`, capability
profiles in `nimbus-libkrun`), drop `*.md` files in that repo under
`.agents/autoreview/`; the helper auto-appends them. Disable all auto-context
with `--no-default-context` (or `AUTOREVIEW_NO_DEFAULT_CONTEXT=1`).

## Helper

```bash
# From a clone of nimbus/agent-skills:
skills/autoreview/scripts/autoreview --help

# Installed into the agent skills dir:
~/.claude/skills/autoreview/scripts/autoreview --help
~/.codex/skills/agent-skills/autoreview/scripts/autoreview --help
```

The helper:

- chooses dirty local changes first; otherwise current PR base via `gh pr view`; otherwise `origin/main` for non-main branches
- supports `--engine codex` (default), `claude`, `droid`, `copilot`; override with `AUTOREVIEW_ENGINE`
- auto-attaches Nimbus review criteria unless `--no-default-context`
- resolves `git`, `gh`, and reviewer binaries from absolute `PATH` entries only, never from the reviewed checkout
- runs the engine read-only; forbids file mutation and nested review in the prompt; Codex runs through `codex exec` with a read-only sandbox and structured output
- supports `--dry-run`, `--parallel-tests`, `--parallel-tests-shell`, `--prompt`, `--prompt-file`, `--dataset`, `--no-tools`, `--no-web-search`, `--output`, `--json-output`, `--stream-engine-output`, and `--panel`/`--reviewers` with per-engine `--model`/`--thinking`
- prints `autoreview clean: no accepted/actionable findings reported` and exits 0 when clean; exits nonzero when actionable findings are present

Smoke harness (engine security calibration, not Nimbus logic):

```bash
skills/autoreview/scripts/test-review-harness --fixture benign --engine codex
```

## Final Report

Include:

- review command used (engine, mode, ref)
- tests/proof run and result
- findings accepted/rejected, briefly why (cite the Nimbus invariant when relevant)
- the clean review result from the final run, or why a remaining finding was consciously rejected

Do not run another review solely to improve the report wording. If the final run
exited 0 with no accepted/actionable findings, report that exact run as clean.
