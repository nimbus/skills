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

## Privacy and Execution Boundary

The helper sends the frozen git bundle, prompt context, and any `--dataset`
files to the selected review engine (`codex`, `claude`, `droid`, or `copilot`).
Do not run an external-engine review on private workspaces unless the user and
org policy allow that bundle to leave the machine or repo boundary.

Running the default `--engine codex` from inside an active Codex session starts
a nested Codex CLI. In sandboxed sessions this can fail before review with
readonly `~/.codex` state, PATH update, or app-server initialization errors.
That is an execution-context limitation, not a broken skill install.

The helper detects Codex-managed sessions with `CODEX_SANDBOX` or
`CODEX_THREAD_ID` and refuses nested `--engine codex` by default. Set
`AUTOREVIEW_ALLOW_NESTED_CODEX=1` only when you intentionally want the nested
Codex call and both the environment and data policy allow it.

If approval or policy blocks sending the private review bundle to an external
engine, do not retry through another external engine or route around the block.
Continue with a manual repo-grounded audit using this Contract, then report that
the structured helper was policy-blocked. To run the structured helper itself,
use a normal terminal or an approved internal environment where the selected
review engine may receive the bundle.

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
- When an accepted finding shows a bug class or repeated pattern, inspect the current review scope for sibling instances before fixing.
- Fix the scoped bug class at once when practical; stop at touched surfaces, owner boundaries, and clear follow-up territory.
- Keep going until structured review returns no accepted/actionable findings.
- If a review-triggered fix changes code, rerun focused tests and rerun the structured review helper.
- For security-audit suppression changes, verify accepted findings remain auditable: suppressed findings stay in structured output, active output keeps an unsuppressible suppression notice, and aggregate findings cannot hide unrelated active risk.
- The helper auto-attaches the Nimbus review criteria (`review-context/nimbus.md` plus any repo-local `.agents/autoreview/*.md`). Trust findings that cite a real invariant violation — zero-I/O `nimbus-core`, zero-workspace-deps `nimbus-runtime`, single mutation path, storage atomicity, bundle integrity, optional schema, pre-launch no-compat policy, behavior-asserting tests, modularity/naming. Do not dismiss them as style.
- Never switch or override the requested review engine/model. If the review hits model capacity, retry the same command a few times with the same engine/model.
- Be patient with large bundles. Structured review can take up to 30 minutes while the model call is active, especially with tools or web search.
- Treat heartbeat lines like `review still running: ... elapsed=... pid=...` as healthy progress, not a hang. Let the helper continue while heartbeats are advancing. Pass `--stream-engine-output` when live engine text is useful; Codex and Claude filter tool/file chatter, other engines pass raw output through.
- Do not kill a review just because it has been quiet for 2-5 minutes, or because it is still running under the 30-minute window. Inspect the process only after missing multiple expected heartbeats, after 30 minutes, or after an obviously failed subprocess; prefer letting the same helper command finish.
- Tools are useful in review mode. The helper allows read-only inspection tools and web search by default so reviewers can check dependency contracts, upstream docs (Deno/V8/Convex), and current behavior.
- Security perspective is always included, but it should not cripple legitimate functionality. Report security findings only when the change creates a concrete, actionable risk or removes an important safety check (e.g. the SHA-256 bundle integrity check, a trust boundary in `nimbus-auth`/`nimbus-server`).
- For regression provenance, use `git blame` / `git log` and, when a PR is traceable, `gh pr view`. Keep roles separate: blamed code author, blamed PR author, merger/committer, current author, and PR/date. If no PR is traceable, use the blamed commit SHA, date, and author. Do not guess a merger or frame missing PR metadata as a finding.
- If the blamed PR was merged by automation, identify the human trigger when practical. Check timeline/comments first; if rate-limited, use cached or public PR HTML when available. Report `automerge triggered by @login`; if not found, say trigger unknown.
- Do not invoke built-in `codex review`, nested reviewers, reviewer panels, or `/code-review ultra` from inside the review. The helper builds one bundle, calls one selected engine, validates one structured result, and stops.
- Stop as soon as the helper exits 0 with no accepted/actionable findings. Do not run an extra review just to get a nicer "clean" line, a second opinion, or clearer closeout wording.
- Treat the helper's successful exit plus absence of actionable findings as the clean review result, even if the underlying Codex CLI output is terse.
- Multi-reviewer panels are opt-in only. Use them when explicitly requested or when risk justifies the extra spend; you still verify every accepted finding before fixing.
- If rejecting a finding as intentional, add a brief inline code comment only when it explains a real invariant or ownership decision future reviewers should know.
- If Gitcrawl is in use and reports `database disk image is malformed`, run `gitcrawl doctor --json` once to let the portable cache repair before retrying review; do not bypass the shim unless repair fails and freshness requires live GitHub.
- If Gitcrawl is in use and reports a portable manifest mismatch, source/runtime DB health error, or stale portable-store checkout, run `gitcrawl doctor --json` and inspect `source_db_health`, `runtime_db_health`, and `portable_store_status` before falling back to live GitHub.
- Do not push just to review. Push only when the user requested push/ship/PR update. Respect each repo's branching norms (Nimbus `nimbus` is pre-launch and often commits to `main`; forks like `deno`/`rusty_v8` follow the tag/repin workflow in the Nimbus routing docs).

## Skill Path (set once)

Set the skill script paths once, then use `"$AUTOREVIEW"` and
`"$AUTOREVIEW_HARNESS"` in the examples below.

Choose one:

```bash
# Source checkout of nimbus/agent-skills:
export AUTOREVIEW="skills/autoreview/scripts/autoreview"
export AUTOREVIEW_HARNESS="skills/autoreview/scripts/test-review-harness"
```

```bash
# Codex grouped install:
export AUTOREVIEW="$HOME/.codex/skills/agent-skills/autoreview/scripts/autoreview"
export AUTOREVIEW_HARNESS="$HOME/.codex/skills/agent-skills/autoreview/scripts/test-review-harness"
```

```bash
# Codex direct skill install:
export AUTOREVIEW="$HOME/.codex/skills/autoreview/scripts/autoreview"
export AUTOREVIEW_HARNESS="$HOME/.codex/skills/autoreview/scripts/test-review-harness"
```

```bash
# Global shared skills root:
export AGENTS_HOME="${AGENTS_HOME:-$HOME/.agents}"
export AUTOREVIEW="$AGENTS_HOME/skills/autoreview/scripts/autoreview"
export AUTOREVIEW_HARNESS="$AGENTS_HOME/skills/autoreview/scripts/test-review-harness"
```

When using Claude Code, set `AGENTS_HOME="$HOME/.claude"` for global skills, or
use the direct `~/.claude/skills/autoreview` symlink.

## Pick Target

Dirty local work (unstaged/staged/untracked in the current checkout):

```bash
"$AUTOREVIEW" --mode local
```

`--mode uncommitted` is an alias for `--mode local`. A clean local review only
proves there is no local patch; for committed/pushed/PR work, point at the
commit or branch diff instead — do not force a dirty mode.

Branch/PR work:

```bash
"$AUTOREVIEW" --mode branch --base origin/main
```

Optional review context is first-class:

```bash
"$AUTOREVIEW" --mode branch --base origin/main --prompt-file /tmp/review-notes.md --dataset /tmp/evidence.json
```

If an open PR exists, use its actual base:

```bash
base=$(gh pr view --json baseRefName --jq .baseRefName)
"$AUTOREVIEW" --mode branch --base "origin/$base"
```

Committed single change (already-landed work on `main`, where a branch diff is
usually empty after push):

```bash
"$AUTOREVIEW" --mode commit --commit HEAD
```

## Parallel Closeout

Format first if formatting can change line locations, then run the canonical
Nimbus verification concurrently with the review:

```bash
# Rust crate, focused:
"$AUTOREVIEW" --mode local --parallel-tests "cargo test -p nimbus-engine"
# Workspace gate:
"$AUTOREVIEW" --mode branch --base origin/main --parallel-tests "make check"
# JS monorepo:
"$AUTOREVIEW" --mode local --parallel-tests "npm run typecheck"
```

Prefer the narrowest faithful command (see
`docs/architecture/testing/ci-failure-investigation.md`). If tests or review
force edits, rerun the affected tests and rerun review until no
accepted/actionable findings remain, then stop.

## Review Panels

Run multiple reviewers against one frozen bundle (opt-in):

```bash
"$AUTOREVIEW" --reviewers codex,claude
"$AUTOREVIEW" --panel                       # Codex + Claude
"$AUTOREVIEW" --reviewers codex:gpt-5.1:high,claude:sonnet:max
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

## Context Efficiency

Run the helper directly so target selection, engine choice, structured
validation, and exit status all stay in one path. If output is noisy, summarize
the completed helper output after it returns; do not ask another agent or
reviewer to rerun the review.

## Helper

After setting `AUTOREVIEW` and `AUTOREVIEW_HARNESS` above:

```bash
"$AUTOREVIEW" --help
```

Smoke harness (engine security calibration, not Nimbus logic):

```bash
"$AUTOREVIEW_HARNESS" --fixture benign --engine codex
```

The helper:

- chooses dirty local changes first; otherwise current PR base via `gh pr view`; otherwise `origin/main` for non-main branches
- accepts `--mode uncommitted` as an alias for `--mode local`
- supports `--engine codex` (default), `claude`, `droid`, `copilot`; override with `AUTOREVIEW_ENGINE`
- auto-attaches Nimbus review criteria unless `--no-default-context`
- resolves `git`, `gh`, reviewer, and PowerShell shell commands from absolute `PATH` entries only, never from the reviewed checkout; explicit relative `--*-bin` paths are resolved from the reviewed repository root
- runs the engine read-only; forbids file mutation and nested review in the prompt; Codex runs through `codex exec` with a read-only sandbox and structured output
- use `--mode commit --commit <ref>` for already-committed work, especially clean `main` after landing
- should be left in `--mode auto` or forced to `--mode branch` for PR/branch work; do not force `--mode local` after committing
- writes only to stdout unless `--output`, `--json-output`, or live streamed engine stderr is set
- supports `--dry-run`, `--parallel-tests`, `--parallel-tests-shell`, `--prompt`, `--prompt-file`, `--dataset`, `--no-tools`, `--no-web-search`, `--output`, `--json-output`, `--stream-engine-output`, and `--panel`/`--reviewers` with per-engine `--model`/`--thinking`
- supports `--stream-engine-output` or `AUTOREVIEW_STREAM_ENGINE_OUTPUT=1` for live engine text while preserving structured validation; Codex and Claude hide tool/file event details, emit compact activity summaries, and report usage at turn completion
- prints `autoreview clean: no accepted/actionable findings reported` and exits 0 when clean; exits nonzero when actionable findings are present

## Final Report

Include:

- review command used (engine, mode, ref)
- tests/proof run and result
- findings accepted/rejected, briefly why (cite the Nimbus invariant when relevant)
- the clean review result from the final run, or why a remaining finding was consciously rejected

Do not run another review solely to improve the report wording. If the final run
exited 0 with no accepted/actionable findings, report that exact run as clean.
