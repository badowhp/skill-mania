# Agent Automation Templates

These are opt-in project templates, not plugin defaults. Copy the script and the matching configuration into a target repository only after the team has reviewed its tool permissions and failure behavior.

## Included Guard

`guard-agent-command.py` blocks a short list of unmistakably destructive shell commands when a hook sends a tool payload on standard input. It is intentionally narrow: it does not attempt to parse every shell language or decide whether a command is generally safe.

- Copy the script to `.agent-automation/guard-agent-command.py`.
- For Claude Code, merge `claude-settings.json` into `.claude/settings.json`.
- For GitHub Copilot, copy `copilot-hooks.json` to `.github/hooks/agent-safety.json`.
- Exercise an allowed command and a deliberately blocked command in a disposable repository before trusting the guard.

Do not use hooks to transmit prompts, code, credentials, or command logs to third parties. Do not run formatting, deployment, or full test suites after every tool call; use targeted project gates instead. Codex plugins may expose skills and approved apps, but this repository does not assume a compatible lifecycle-hook surface.
