# Nimbus Skills

- Keep general review machinery in `agentstation/skills`; this repository owns
  only Nimbus profiles, criteria, and thin adapters.
- Canonical skills live under `skills/<name>/SKILL.md`.
- Nimbus-wide review invariants live in
  `skills/nimbus-autoreview/review-context/nimbus.md`.
- Per-repository additions live in that repository under
  `.agents/autoreview/*.md`.
- Use npx skills and its global lock for installation and updates. Do not add a
  second installer.
- Validate every change with `scripts/validate-skills` and the profile tests.
