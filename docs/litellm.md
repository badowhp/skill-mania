# LiteLLM Gateway Notes

Use this document for non-secret LiteLLM planning, setup review, and troubleshooting. Keep active keys, virtual keys, and user-level model-provider choices out of this repository.

## When To Use LiteLLM

Use LiteLLM when a team or local setup needs:

- stable model aliases across clients
- provider fallback or routing rules
- virtual keys, budgets, rate limits, or spend tracking
- centralized logging, redaction, and gateway ownership
- one OpenAI-compatible boundary in front of multiple providers

Prefer direct provider calls when one endpoint, one key, and one model slug are enough.

## Source Anchors

- LiteLLM provider docs: https://docs.litellm.ai/docs/providers
- LiteLLM proxy config: https://docs.litellm.ai/docs/proxy/configs
- LiteLLM supported endpoints: https://docs.litellm.ai/docs/supported_endpoints
- OpenRouter provider through LiteLLM: https://docs.litellm.ai/docs/providers/openrouter
- Codex custom model providers: https://developers.openai.com/codex/config-advanced#custom-model-providers

## Config Placement

Put reusable, non-secret examples in docs. Put real runtime config outside the repository or in user-level config.

Do not commit:

- OpenRouter keys
- LiteLLM master keys
- generated virtual keys
- `.env` files
- real gateway config with secrets
- user-level Codex provider config

Do not put active provider redirects in project `.codex/config.toml`; provider choice is machine-local and may be ignored when placed at project scope.

## Minimal OpenRouter Gateway

Copy this outside the repository before use and keep secrets in environment variables or a secret manager:

```yaml
model_list:
  - model_name: codex-openrouter
    litellm_params:
      model: openrouter/<provider>/<model>
      api_key: "os.environ/OPENROUTER_API_KEY"
      api_base: "https://openrouter.ai/api/v1"
      rpm: 60

litellm_settings:
  drop_params: true
  turn_off_message_logging: true
  redact_user_api_key_info: true
```

Runtime environment:

```bash
export OPENROUTER_API_KEY="..."
export LITELLM_MASTER_KEY="sk-..."
litellm --config ./litellm-openrouter.config.yaml
```

Prefer generated virtual keys for shared clients. Use the master key only for local smoke tests or gateway administration.

## Codex User Config Shape

Put active provider config in user-level Codex config:

```toml
model_provider = "litellm_openrouter"
model = "codex-openrouter"

[model_providers.litellm_openrouter]
name = "LiteLLM via OpenRouter"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_CODEX_KEY"
wire_api = "responses"
```

Only set `wire_api = "responses"` after verifying the proxy and model path handle `/v1/responses`.

## Verification

Check LiteLLM health:

```bash
curl -sS http://localhost:4000/health
```

Check the alias through Chat Completions:

```bash
curl -sS http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"codex-openrouter","messages":[{"role":"user","content":"Reply with ok."}]}'
```

Check Responses API compatibility before routing Codex:

```bash
curl -sS http://localhost:4000/v1/responses \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"codex-openrouter","input":"Reply with ok."}'
```

## Review Checklist

Block shared use when:

- keys or `.env` files are committed
- the proxy listens publicly without TLS and authentication
- message logging is enabled for sensitive prompts, code, customer data, or secrets
- no owner exists for key rotation, budgets, and rate limits
- model aliases route to unapproved providers or retention paths
- fallback behavior can silently send sensitive prompts to a different provider class
- Codex is pointed at a Chat Completions-only path without Responses API validation

Prefer local bind addresses for personal dev, scoped virtual keys for team clients, provider/model allowlists, short log retention, and a documented rollback to the default provider.
