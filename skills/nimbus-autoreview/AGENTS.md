# Nimbus autoreview maintenance

- Dependency: `agentstation/skills`, skill `autoreview`.
- Keep this adapter thin. Model routing, config parsing, isolation, secret
  scanning, and report validation belong upstream.
- Keep Nimbus architecture criteria in `review-context/nimbus.md`.
- Update `autoreview.toml` only for Nimbus-specific model/cadence choices.
- Run the wrapper test and the repository skill validator after every change.
