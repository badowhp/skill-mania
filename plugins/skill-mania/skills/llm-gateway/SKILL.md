---
name: llm-gateway
description: Plan, configure, review, or troubleshoot LLM gateway setups with LiteLLM, OpenRouter, OpenAI-compatible proxies, model aliases, provider routing, virtual keys, budgets, and Codex custom model-provider integration. Use when the user mentions LiteLLM, OpenRouter, model gateway, LLM proxy, router, fallback models, virtual keys, provider config, or connecting Codex to a non-default model provider.
---
# LLM Gateway
Design and validate LLM gateway setups without leaking secrets or confusing portable skill guidance with local runtime configuration.
## Core Rules
1. Keep active provider config, API keys, proxy keys, and model-provider selection out of portable skills and repo `AGENTS.md`.
2. Put reusable workflow guidance, examples, and review checks in this skill.
3. Put actual Codex provider settings in user-level Codex config, not project-local `.codex/config.toml`.
4. Prefer direct OpenRouter when the user only needs one OpenAI-compatible endpoint.
5. Prefer LiteLLM when the user needs aliases, fallbacks, budgets, virtual keys, spend tracking, centralized logging, or multiple providers.
6. Validate Responses API compatibility before routing Codex through a proxy.
7. Treat proxy logs as sensitive. Disable message logging or redact keys when prompts, code, customer data, or secrets may pass through.
## Workflow
1. Classify the integration:
   - direct OpenRouter API call
   - local LiteLLM proxy for personal Codex usage
   - team LiteLLM gateway with virtual keys, budgets, or fallbacks
   - production gateway with observability and retention controls
2. Identify the runtime surface:
   - application code or SDK
   - LiteLLM `config.yaml`
   - user-level Codex `config.toml`
   - plugin skill package
   - MCP server or external tool
3. Read [references/litellm-openrouter-codex.md](references/litellm-openrouter-codex.md) when planning or reviewing LiteLLM/OpenRouter setup.
4. Use [assets/litellm-openrouter.config.example.yaml](assets/litellm-openrouter.config.example.yaml) only as a non-secret starting template.
5. Verify with the smallest real request before changing defaults.
6. For production, require owner, key rotation, budget/rate limits, log retention, model allowlist, failure behavior, and rollback path.
## Fit In This Repo
- Add skills, references, and non-secret templates under `skills/`.
- Sync packaged copies with `./scripts/sync-plugin-package.sh`.
- Do not commit `.env`, real LiteLLM config with secrets, OpenRouter keys, LiteLLM master keys, virtual keys, or user-level Codex provider config.
- Do not add provider redirects to project `.codex/config.toml`; Codex ignores those project-local keys and they are machine-local anyway.
## Output
For setup advice:

1. recommended path: direct OpenRouter or LiteLLM proxy
2. where each config belongs
3. exact non-secret snippets or template path
4. verification commands
5. security and rollback checks

For review:

1. blocking risks
2. config placement issues
3. secret/logging exposure
4. compatibility gaps
5. smallest safe remediation
