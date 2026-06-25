# LiteLLM, OpenRouter, And Codex
Use this for LiteLLM/OpenRouter planning, setup review, or Codex custom provider routing.
## Source Anchors
- LiteLLM OpenRouter provider: https://docs.litellm.ai/docs/providers/openrouter
- LiteLLM proxy config: https://docs.litellm.ai/docs/proxy/configs
- LiteLLM supported endpoints: https://docs.litellm.ai/docs/supported_endpoints
- OpenRouter quickstart: https://openrouter.ai/docs/quickstart
- OpenRouter API reference: https://openrouter.ai/docs/api/reference/overview
- Codex custom providers: https://developers.openai.com/codex/config-advanced#custom-model-providers
## Placement Decision
Use direct OpenRouter when:

- the client can call an OpenAI-compatible endpoint directly
- one OpenRouter key and one model slug are enough
- there is no need for per-user budgets, proxy auth, spend tracking, model aliases, or fallbacks

Use LiteLLM in front of OpenRouter when:

- multiple clients need stable model aliases
- Codex or app clients should not hold the OpenRouter key
- the team needs budget controls, virtual keys, rate limits, spend tracking, fallbacks, or centralized routing
- logs, callbacks, and observability need one gateway boundary

Use a skill in this repo for:

- repeatable setup workflow
- non-secret config examples
- review checklists
- verification commands

Use user-level runtime config for:

- active Codex `model_provider`
- proxy base URL
- bearer-token environment variable name
- personal or machine-local profile selection

Do not put active provider redirects in project `.codex/config.toml`. Codex ignores project-local provider/auth redirect keys, and the repo should not decide a developer's model provider.
## Minimal LiteLLM OpenRouter Shape
Use the template at [../assets/litellm-openrouter.config.example.yaml](../assets/litellm-openrouter.config.example.yaml).

Runtime environment:

```bash
export OPENROUTER_API_KEY="..."
export LITELLM_MASTER_KEY="sk-..."
litellm --config ./litellm-openrouter.config.yaml
```

The config should use `api_key: "os.environ/OPENROUTER_API_KEY"` so the provider key stays out of YAML. Prefer `LITELLM_MASTER_KEY` or generated virtual keys for client auth.
## Codex User Config Shape
Put active provider config in user-level Codex config, not this repo:

```toml
model_provider = "litellm_openrouter"
model = "codex-openrouter"

[model_providers.litellm_openrouter]
name = "LiteLLM via OpenRouter"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_CODEX_KEY"
wire_api = "responses"
```

For local-only smoke tests without LiteLLM key management, `env_key` can point at `LITELLM_MASTER_KEY`. For shared use, generate a scoped LiteLLM virtual key for Codex and store it as `LITELLM_CODEX_KEY`.

Only set `wire_api = "responses"` after verifying the proxy/model path handles `/v1/responses`. If Responses API behavior fails, do not route Codex through that provider until the proxy/model path is fixed.
## Verification
Check LiteLLM is reachable:

```bash
curl -sS http://localhost:4000/health
```

Check the model alias with Chat Completions:

```bash
curl -sS http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"codex-openrouter","messages":[{"role":"user","content":"Reply with ok."}]}'
```

Check the Responses API before using Codex custom provider routing:

```bash
curl -sS http://localhost:4000/v1/responses \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"codex-openrouter","input":"Reply with ok."}'
```
## Security Review
Block release or shared use when:

- OpenRouter keys, LiteLLM master keys, virtual keys, or `.env` files are committed
- the proxy listens publicly without TLS and auth
- message logging is enabled for sensitive prompts, code, customer data, or secrets
- there is no owner for key rotation and budget/rate-limit changes
- model aliases route to unapproved providers or data-retention paths
- fallback behavior can silently send sensitive prompts to a different provider class
- Codex is pointed at a Chat Completions-only path without Responses API validation

Prefer:

- local bind address for personal dev
- scoped virtual keys for team clients
- provider and model allowlists
- budget and rate limits per key or team
- redacted logs and short retention
- documented rollback to the default Codex provider
