# OpenRouter Notes

Use this document for direct OpenRouter setup, review, and troubleshooting. Keep keys and active user-level provider selection out of portable skills and repository instructions.

## When To Use Direct OpenRouter

Use direct OpenRouter when:

- the client can call one OpenAI-compatible endpoint directly
- one OpenRouter key and one model slug are enough
- there is no need for per-user budgets, proxy auth, spend tracking, model aliases, or fallbacks
- the user wants the fewest moving parts

Use [LiteLLM](litellm.md) in front of OpenRouter when aliases, budgets, routing, virtual keys, centralized logs, or multiple clients matter.

## Source Anchors

- OpenRouter quickstart: https://openrouter.ai/docs/quickstart
- OpenRouter API reference: https://openrouter.ai/docs/api/reference/overview
- Codex custom model providers: https://developers.openai.com/codex/config-advanced#custom-model-providers

## Config Placement

Keep the OpenRouter API key in an environment variable or secret manager. Do not commit the key, `.env` files, or user-level provider config.

For app code, use OpenRouter as an OpenAI-compatible endpoint when the SDK or client supports custom base URLs.

For Codex, put active provider config in user-level Codex config rather than the project repository.

## Minimal Smoke Test

```bash
curl -sS https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"<provider>/<model>","messages":[{"role":"user","content":"Reply with ok."}]}'
```

If the consumer needs the Responses API, verify that exact path before making it the default route.

## Review Checklist

- Is the key stored outside source control and logs?
- Is the selected model slug explicit and approved for the data being sent?
- Does the client handle provider errors, rate limits, and model unavailability?
- Is sensitive data allowed to leave the current provider boundary?
- Does the setup have a rollback path to the previous provider?
- If used through Codex, has the selected wire API been verified with the real endpoint?
