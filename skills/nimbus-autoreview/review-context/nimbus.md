# Nimbus review contract

Nimbus is a Convex-compatible backend server: a Rust workspace plus an npm
monorepo, with forked JS engines (deno / rusty_v8 / bun) and sandbox backends
(nimbus-libkrun / nimbus-crun / machine-os). Review changes against the
invariants below in addition to ordinary correctness and security review. These
are repository contracts, not preferences — a violation is a finding.

## Pre-launch policy (overrides training instincts)

Nimbus has not launched. There are no production users or data to migrate.

- Breaking changes are preferred over compatibility layers.
- No backwards-compatibility code, no migration shims, no legacy feature flags.
- Delete old behavior; do not deprecate it.
- If the diff adds a compatibility/migration/deprecation path, that is the
  defect — flag it and prefer the clean replacement.

## Crate dependency invariants (architecture, do not violate)

- `nimbus-core` has zero I/O. Types and validation only. No file reads, no
  network, no clocks-as-dependencies. A new `std::fs`, `reqwest`, socket, or
  similar in `nimbus-core` is a finding.
- `nimbus-runtime` has zero workspace dependencies. It defines the V8 surface
  and the `HostBridge` trait. Any `nimbus-*` path dependency added to
  `crates/nimbus-runtime/Cargo.toml`, or Nimbus-specific integration leaking
  into it, is a finding. Nimbus integration belongs in the server's bridge impl.
- Dependency direction flows toward `nimbus-core`. Watch for new edges that
  create cycles or invert the layering (core → engine → server).

## Mutation path

Every mutation — HTTP, WebSocket, scheduler, or V8 runtime — flows through the
engine-owned mutation path (`apply_mutation_with_mode*` plus the queued journal
path). There is no separate code path. A change that introduces a second write
path, or that lets a runtime host op (`ctx.db.insert(...)` etc.) bypass the
`Service` path, is a finding.

## Storage atomicity

Document write, supporting index effects, and commit-log append must remain a
single storage transaction. Never commit a document without its index entries;
never append a commit without the document write. A diff that splits these into
separate transactions, or that can leave indexes/commit-log inconsistent on the
error path, is a finding.

## Runtime bundle integrity

Runtime bundles are SHA-256 integrity-checked before every invocation. A change
that skips, caches-away, or weakens that check is a security finding.

## Schema is optional

A table without a schema accepts any document. Setting a schema adds constraints
but never removes the ability to write. A change that makes schema mandatory, or
that rejects writes to schemaless tables, is a finding.

## Tests verify behavior, not compilation

- Every test asserts a specific outcome. A test that only checks "it didn't
  panic" or "it compiled" is not a test — flag it.
- Do not weaken assertions, delete tests, change expected values to match wrong
  output, or suppress warnings to make a change pass. That is masking a defect.
- Reliability proofs state the invariant they wait for. Prefer bounded
  "wait until X" helpers with diagnostic failure messages over raw `sleep`,
  `yield_now` loops, or anonymous timeout literals. Raising a timeout as the
  first response to flakiness is a finding; ask which state boundary lacks a
  semantic wait instead. (See docs/architecture/testing/reliability-posture.md.)

## Completion-gate discipline

If a plan's completion gate says handle N cases, all N must be handled. A subset
plus TODOs for the rest is a finding. Watch for lazy-exit phrasing in code or
comments ("good enough for now", "left as an exercise", "out of scope" for
in-scope work, "as a first pass", "can be improved later").

## Modularity and naming

- Files under 1,500 lines are usually fine. 1,500–1,999 lines need an explicit
  justification in the owning plan. 2,000+ lines must be decomposed or
  documented as an ownership exception. Do not split mechanically — group by
  concept ownership.
- Prefer concept-owned names (`bootstrap.rs`, `provider.rs`, `read.rs`,
  `write.rs`, `state.rs`) over `helpers.rs`, `common.rs`, `misc.rs`, `utils.rs`
  unless ownership is genuinely shared and obvious. A new `utils`/`misc` grab-bag
  is a finding.
- Once a file is a composition root, new logic belongs in concept-owned children,
  not in a re-inflated inline switchboard.

## JavaScript packages

`packages/nimbus` is the canonical JS SDK; `packages/convex` is a compatibility
wrapper that should stay thin (adapters / aliases / re-exports) rather than
copy-forwarding parallel logic. `crates/nimbus` is the unrelated Rust facade —
do not conflate them.

## Convex API surface

Changes under `packages/convex/`, `demos/convex/`, or any Convex API surface
must follow `docs/adapters/convex/ai-guidelines.md`, which overrides general
Convex knowledge. Flag deviations from those rules.

## Verification expectations

Reviewers should expect (and may recommend) the canonical commands rather than
ad hoc ones: `cargo fmt --all --check`, `make check`, `make clippy`, `make test`,
`make deny`, `make verify-third-party-attribution`, and the harness lanes
(`make verify-harness [SURFACE=...]`). JS: `npm run typecheck`, `npm run test`,
`npm run build`. Node is a dev build dependency for any Rust target that touches
`nimbus-server`.
