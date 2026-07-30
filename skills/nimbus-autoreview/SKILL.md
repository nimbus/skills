---
name: nimbus-autoreview
description: Use instead of the general autoreview skill for pre-PR and configured checkpoint reviews across Nimbus repositories.
---

# Nimbus autoreview

Run the thin wrapper, which delegates to the globally installed `autoreview`
helper while attaching the Nimbus architecture contract:

```bash
export NIMBUS_AUTOREVIEW="${AGENTS_HOME:-$HOME/.agents}/skills/nimbus-autoreview/scripts/nimbus-autoreview"
"$NIMBUS_AUTOREVIEW" --gate pre-pr --mode auto
```

Use this profile throughout the Nimbus constellation: `nimbus`, engine forks,
sandbox/runtime repositories, desktop, machine images, adapters, and release
tooling. It inherits global and repository autoreview configuration, then
applies the Nimbus model profile and review criteria.

The wrapper defaults GPT-5.6 Sol to `xhigh` and keeps Anthropic models at
`high`. Automatic selection still avoids the current host harness. Fable is
available only when explicitly requested:

```bash
"$NIMBUS_AUTOREVIEW" --profile fable --mode branch --base origin/main
```

Manual review and configured plan checkpoints use the same arguments as the
general helper:

```bash
"$NIMBUS_AUTOREVIEW" --mode local
"$NIMBUS_AUTOREVIEW" --gate phase --mode auto
```

Apply every rule in
[`review-context/nimbus.md`](review-context/nimbus.md). Repository-local
criteria under `.agents/autoreview/*.md` should be passed explicitly by the
owning repository until the general helper gains safe directory discovery.

Treat findings as advisory, verify them against the real code path, keep fixes
inside the original task and owner boundary, and rerun focused proof plus one
review after an accepted finding changes code.
