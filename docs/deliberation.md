# Deliberation Adoption Guide

[Deliberation](https://github.com/antonbabenko/deliberation) is an external multi-model review plugin and MCP server. It can ask GPT through Codex CLI, Gemini through Antigravity CLI, Grok through xAI, and configured OpenRouter models for specialist reviews or consensus.

Skill Mania does not bundle Deliberation. The capabilities overlap several local domain skills, while the runtime adds external code execution, provider data transfer, credentials, cost, and optional workspace writes. Treat it as an opt-in second-opinion system for consequential work.

## When It Fits

Use it for:

- architecture, migration, security, or release decisions where an independent model may expose a missed failure mode
- reviewing a substantial plan before implementation
- debugging after repeated evidence-backed attempts have failed
- resolving a real disagreement between reviewers

Do not use it for routine edits, simple file operations, the first attempt at a normal bug fix, or as a substitute for tests and primary-source documentation. Start with one advisory reviewer; use fan-out or consensus only when the decision justifies the extra latency and cost.

## Codex Installation

Prefer the native Codex plugin because it includes the MCP server registration, routing skill, and specialist personas:

```bash
codex plugin marketplace add antonbabenko/deliberation
```

Then open `/plugins` in Codex and install `deliberation`. Confirm discovery with:

```bash
codex plugin marketplace list
codex plugin list
codex mcp list
```

The standalone MCP server is an alternative when the persona and routing files are not needed:

```bash
codex mcp add deliberation -- npx -y @antonbabenko/deliberation-mcp
```

The upstream plugin currently launches an unpinned npm package through `npx -y`, so a fresh resolution can execute a newer release than the plugin revision you reviewed. For reproducible or regulated environments, register a reviewed package version such as `@antonbabenko/deliberation-mcp@3.11.0` or maintain a reviewed fork. Re-review before changing that pin.

## Trust Boundaries

Before enabling a provider, account for each boundary:

- Prompts and explicitly attached files go to the selected external provider; GPT and Gemini delegates may also inspect the working directory through their CLIs. Provider retention, training, regional, and contractual terms still apply.
- GPT and Gemini delegates can run in implementation mode and change the workspace. Grok and OpenRouter integrations are advisory-only in the reviewed release.
- The server spawns provider CLIs and the npm-delivered runtime. A provider login or API key grants whatever that provider normally permits.
- Consensus can multiply calls, tokens, latency, and charges across providers and rounds. Agreement is evidence, not proof.
- The upstream documentation notes that Gemini advisory isolation on Linux relies partly on mutation detection; it does not automatically revert an unexpected change. Use a clean worktree and inspect the diff after every delegated run.
- Session persistence, response capture, debug logs, and automatic repository-orientation attachments are separate disclosure surfaces even when the provider call itself is advisory.

At upstream v3.11.0, commit `28b1e0823f96`, reviewed on 2026-07-10, the project had path-containment checks, credential scrubbing, redirect protection for bearer tokens, `0600` session files, generated-host drift checks, and extensive tests. `npm run sync:check` passed and all 590 tests passed in this audit. The reviewed revision did not include a dedicated `SECURITY.md`; do not treat the absence of a documented reporting policy as a security guarantee.

## Safe Starting Configuration

Configure only the providers you intend to use. Keep credentials in the user environment or user-level provider configuration, never in this repository or a committed MCP file.

Keep disclosure features off until there is a specific need:

```json
{
  "orientation": { "enabled": false, "maxFiles": 6 },
  "sessions": {
    "persist": false,
    "maxRecords": 200,
    "maxAgeDays": 30,
    "captureText": false
  },
  "debug": { "enabled": false }
}
```

Use advisory mode by default. Require an explicit implementation request before allowing a delegate to write. Start with a fan-out of one or two providers and a low consensus round cap; increase either only after measuring quality, latency, and spend.

If session persistence is later enabled, remember that `captureText: false` still stores the question and verdict summaries. `captureText: true` stores scrubbed response bodies as plaintext local files. Turning capture off stops future writes but does not delete existing records.

## Verification Checklist

1. Record the reviewed Git revision, release, npm version, and provider list.
2. Inspect the plugin manifest, `.mcp.json`, package scripts, license, and requested environment variables before installation.
3. Test one advisory request in a disposable repository with a clean worktree. Compare `git status --short` before and after.
4. Send synthetic, non-sensitive content first. Confirm which provider received it and where usage appears in that provider's dashboard.
5. Verify that persistence, response capture, debug logging, and orientation attachment match the intended configuration.
6. Review every external opinion against repository evidence, tests, and primary documentation. Do not accept consensus as an approval gate by itself.
7. Repeat this review before marketplace upgrades or npm version changes.

## Primary References

- [Deliberation README](https://github.com/antonbabenko/deliberation/blob/master/README.md)
- [Audited v3.11.0 source](https://github.com/antonbabenko/deliberation/tree/v3.11.0)
- [Codex host guide](https://github.com/antonbabenko/deliberation/blob/master/docs/hosts/codex.md)
- [Setup and configuration](https://github.com/antonbabenko/deliberation/blob/master/SETUP.md)
- [Technical and security behavior](https://github.com/antonbabenko/deliberation/blob/master/TECHNICAL.md)
- [MIT license](https://github.com/antonbabenko/deliberation/blob/master/LICENSE)
