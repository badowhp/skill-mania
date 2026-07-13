# Agent Permission Templates

These opt-in templates give Codex and Claude Code the same least-privilege baseline. The repository itself uses the project-level versions in `.codex/config.toml` and `.claude/settings.json`.

## Security Model

The policy has three independent layers:

1. The OS sandbox confines writes to the active workspace and temp directory, blocks command network access by default, and denies common credential paths.
2. Permission rules keep a human in the loop for shell, Git history, network, publishing, infrastructure, cloud, container, and MCP operations. Full-access and automatic-review modes are disabled.
3. `guard-agent-command.py` denies high-confidence destructive actions before execution, including recursive deletion, worktree-discarding Git commands, forced pushes, device erasure, infrastructure destruction, cluster deletion, destructive cloud operations, and destructive SQL.

The hook deliberately blocks these actions instead of offering an approval button. Run one manually after reviewing it if it is genuinely required.

## Add the Policy to a Repository

Use Codex 0.138.0 or newer and Claude Code 2.1.187 or newer. Review the files before copying them because project requirements differ.

Copy:

- `codex-config.toml` to `.codex/config.toml`
- `claude-settings.json` to `.claude/settings.json`
- `guard-agent-command.py` to `.agent-automation/guard-agent-command.py`
- Optional: `copilot-hooks.json` to `.github/hooks/agent-safety.json` for the same command guard in Copilot CLI; this does not add the Codex or Claude OS sandbox policy.

Codex loads project configuration and hooks only after the repository is trusted. Open `/hooks`, review the exact hook definition, and trust it. Claude Code shows its normal project-trust prompt and then loads the checked-in settings.

The Claude configuration uses regular permission mode, refuses to start if its OS sandbox is unavailable, and disables unsandboxed retries. A newly needed network domain therefore stays inside the network proxy and requires approval. The Codex profile disables command network access entirely; use a narrowly reviewed profile when a project genuinely requires it.

## Enforce the Baseline on a Unix Workstation

Project settings are strong defaults but are still project-controlled. The managed templates are for a non-bypassable workstation policy on macOS or Linux.

First inspect any policy already installed. Do not overwrite an existing file; merge the rules deliberately.

```bash
sudo install -d -m 0755 /etc/agent-safety
sudo install -m 0755 guard-agent-command.py /etc/agent-safety/guard-agent-command.py
```

For Codex, install `codex-requirements.toml` as `/etc/codex/requirements.toml`. This allows only the managed workspace and read-only permission profiles, requires the `untrusted` approval policy with the user as reviewer, disables live web and computer-control surfaces, enforces secret-read denials, and adds managed command rules and the shared hook.

```bash
sudo install -d -m 0755 /etc/codex
sudo install -m 0644 codex-requirements.toml /etc/codex/requirements.toml
```

For Claude Code on macOS, use a managed-settings drop-in so an existing base file is not replaced:

```bash
sudo install -d -m 0755 "/Library/Application Support/ClaudeCode/managed-settings.d"
sudo install -m 0644 claude-managed-settings.json "/Library/Application Support/ClaudeCode/managed-settings.d/20-agent-safety.json"
```

On Linux or WSL2, use `/etc/claude-code/managed-settings.d/20-agent-safety.json` instead. Install `bubblewrap` and `socat` before enabling `failIfUnavailable`; macOS uses Seatbelt and needs no extra sandbox package.

Managed policy can interfere with deployment, credentialed tests, container tooling, and infrastructure work by design. Use a separately isolated VM or a reviewed managed-policy change for those workflows. Do not weaken the everyday profile ad hoc.

## Verify It

Run the deterministic tests from this repository:

```bash
python3 -m unittest tests.test_agent_automation_templates -v
```

Then start fresh sessions and check the effective sources:

- Codex: run `codex --strict-config doctor --summary`, then inspect `/permissions` and `/hooks`.
- Claude Code: run `claude doctor`, then inspect `/permissions`, `/sandbox`, and `/status`.
- In a disposable repository, confirm `git status --short` is allowed and `git reset --hard`, `git clean -fd`, and `rm -rf build` are denied.

## Limits

No command-pattern hook understands every shell or every equivalent program. Codex also documents that current `PreToolUse` interception does not cover every unified-exec or non-shell tool path. The OS sandbox and managed permission constraints are therefore the primary boundaries; the hook is defense in depth.

The workspace remains writable, so an agent can still make broad tracked edits. Keep important work committed or backed up, review diffs, and do not run either client with its dangerous bypass flag. Do not use hooks to transmit prompts, code, credentials, or command logs to third parties.
