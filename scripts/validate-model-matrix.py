#!/usr/bin/env python3
"""Validate the reviewed model-routing matrix used by skill evaluations."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


ROUTE_NAMES = frozenset(("quality", "balanced", "throughput"))
REASONING_EFFORTS = frozenset(("none", "low", "medium", "high", "xhigh", "max"))


def validate(data: object, today: dt.date) -> list[str]:
    if not isinstance(data, dict):
        return ["top-level value must be an object"]
    errors: list[str] = []
    try:
        reviewed_on = dt.date.fromisoformat(str(data["reviewed_on"]))
        review_after = dt.date.fromisoformat(str(data["review_after"]))
    except (KeyError, ValueError):
        errors.append("reviewed_on and review_after must be ISO dates")
    else:
        if review_after <= reviewed_on:
            errors.append("review_after must be later than reviewed_on")
        if today > review_after:
            errors.append(
                f"model matrix review expired on {review_after}; verify current official model guidance"
            )

    source_url = data.get("source_url")
    if source_url != "https://developers.openai.com/api/docs/guides/latest-model.md":
        errors.append("source_url must point to the official latest-model guide")

    routes = data.get("routes")
    if not isinstance(routes, dict) or set(routes) != ROUTE_NAMES:
        errors.append("routes must contain exactly quality, balanced, and throughput")
        routes = {}
    models: set[str] = set()
    for name in sorted(ROUTE_NAMES):
        route = routes.get(name)
        if not isinstance(route, dict):
            continue
        model = route.get("model")
        if not isinstance(model, str) or not model.startswith("gpt-"):
            errors.append(f"routes.{name}.model must be an OpenAI GPT model ID")
        elif model in models:
            errors.append(f"routes.{name}.model must be distinct")
        else:
            models.add(model)
        if route.get("reasoning_effort") not in REASONING_EFFORTS:
            errors.append(f"routes.{name}.reasoning_effort is invalid")
        if not isinstance(route.get("use_when"), str) or len(route["use_when"].strip()) < 20:
            errors.append(f"routes.{name}.use_when must explain the route")

    evaluation = data.get("evaluation")
    if not isinstance(evaluation, dict):
        errors.append("evaluation must be an object")
    else:
        for key in ("generator_route", "judge_route", "routing_route"):
            if evaluation.get(key) not in ROUTE_NAMES:
                errors.append(f"evaluation.{key} must name a route")
        for key in (
            "minimum_with_skill_pass_rate",
            "maximum_pass_rate_regression",
            "minimum_routing_accuracy",
        ):
            value = evaluation.get(key)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not 0 <= value <= 1
            ):
                errors.append(f"evaluation.{key} must be between 0 and 1")
        cases_per_skill = evaluation.get("scheduled_cases_per_skill")
        if (
            isinstance(cases_per_skill, bool)
            or not isinstance(cases_per_skill, int)
            or cases_per_skill < 1
        ):
            errors.append("evaluation.scheduled_cases_per_skill must be a positive integer")
        maximum_calls = evaluation.get("maximum_model_calls")
        if (
            isinstance(maximum_calls, bool)
            or not isinstance(maximum_calls, int)
            or maximum_calls < 1
        ):
            errors.append("evaluation.maximum_model_calls must be a positive integer")
        maximum_requests = evaluation.get("maximum_api_requests")
        if (
            isinstance(maximum_requests, bool)
            or not isinstance(maximum_requests, int)
            or maximum_requests < 1
        ):
            errors.append("evaluation.maximum_api_requests must be a positive integer")
        elif isinstance(maximum_calls, int) and maximum_requests < maximum_calls:
            errors.append("evaluation.maximum_api_requests must cover maximum_model_calls")
        maximum_tokens = evaluation.get("maximum_total_tokens")
        if (
            isinstance(maximum_tokens, bool)
            or not isinstance(maximum_tokens, int)
            or maximum_tokens < 1
        ):
            errors.append("evaluation.maximum_total_tokens must be a positive integer")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("evals/model-matrix.json"))
    parser.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    args = parser.parse_args()

    try:
        data = json.loads(args.matrix.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{args.matrix}: {exc}")
        return 1
    errors = validate(data, args.today)
    for error in errors:
        print(f"{args.matrix}: {error}")
    if errors:
        return 1
    print(f"ok {args.matrix}: reviewed through {data['review_after']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
