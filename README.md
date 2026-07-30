# Nimbus Skills

Project-specific Agent Skills for the Nimbus constellation. General-purpose
workflows stay in their upstream skill repositories; this repository contains
only Nimbus profiles and criteria.

## Install

Install the general review engine first, then the Nimbus profile:

```bash
npx skills add agentstation/skills --skill autoreview -g \
  -a codex -a claude-code -a goose -y
npx skills add nimbus/skills --skill nimbus-autoreview -g \
  -a codex -a claude-code -a goose -y
```

Both are recorded in the global npx-skills lock. Claude Code and Goose see the
same canonical `~/.agents/skills` installation as Codex.

## Included skill

`nimbus-autoreview` delegates bundle creation, isolation, scanning, model
routing, and structured validation to `agentstation/skills@autoreview`. It adds
Nimbus architecture invariants and a Nimbus model profile:

- GPT-5.6 Sol uses `xhigh` for the large cross-module codebase.
- Anthropic reviewers remain capped at `high`.
- Fable remains explicit-only and can be requested with `--profile fable`.
- Automatic cadence inherits the global setting, which defaults to the
  substantive-code pre-PR gate.

Validate with:

```bash
scripts/validate-skills
python3 -m unittest skills/nimbus-autoreview/tests/test_nimbus_autoreview.py
```
