#!/usr/bin/env python3
"""Assemble completed output cases and a routing-only retry into one compact benchmark."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "skill_eval_runner", SCRIPT_DIR / "run-skill-evals.py"
)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def grading_summary(path: Path) -> dict[str, int]:
    summary = read_json(path)["summary"]
    return {"passed": int(summary["passed"]), "total": int(summary["total"])}


def run_metrics(path: Path) -> dict[str, Any]:
    grading = grading_summary(path / "grading.json")
    timing = read_json(path / "timing.json")
    total = grading["total"]
    return {
        **grading,
        "pass_rate": round(grading["passed"] / total, 4) if total else 0.0,
        "tokens": int(timing["total_tokens"]),
        "duration_ms": int(timing["duration_ms"]),
    }


def completed_records(workspace: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case_path in sorted(workspace.glob("*/*/case.json")):
        case = read_json(case_path)
        case_dir = case_path.parent
        baseline_kind = str(case["baseline_kind"])
        baseline = run_metrics(case_dir / baseline_kind)
        with_skill = run_metrics(case_dir / "with_skill")
        judge = read_json(case_dir / "judge.json")["timing"]
        current_package = case["with_skill_package"]
        baseline_package = case.get("baseline_package")
        records.append(
            {
                "skill": str(case["skill"]),
                "case": str(case["id"]),
                "baseline_kind": baseline_kind,
                "generation_order": list(case["generation_order"]),
                "with_skill_package_characters": int(current_package["characters"]),
                "with_skill_package_sha256": str(current_package["sha256"]),
                "baseline_package_characters": (
                    int(baseline_package["characters"]) if baseline_package else 0
                ),
                "baseline_package_sha256": (
                    str(baseline_package["sha256"]) if baseline_package else None
                ),
                "baseline": baseline,
                "with_skill": with_skill,
                "judge_tokens": int(judge["total_tokens"]),
                "judge_duration_ms": int(judge["duration_ms"]),
            }
        )
    return records


def workspace_usage(workspace: Path) -> dict[str, int]:
    benchmark = workspace / "benchmark.json"
    if benchmark.is_file():
        source = read_json(benchmark)["usage"]
    else:
        source = read_json(workspace / "error.json")["usage"]
    return {
        "model_calls": int(source["model_calls"]),
        "api_requests": int(source["api_requests"]),
        "total_tokens": int(source["total_tokens"]),
        "total_duration_ms": int(source["total_duration_ms"]),
    }


def validate_compatible(
    output_configuration: dict[str, Any], routing_configuration: dict[str, Any]
) -> None:
    for key in (
        "skills",
        "provider",
        "routing_model",
        "routing_reasoning_effort",
        "case_offset",
        "baseline",
        "git_sha",
    ):
        if output_configuration.get(key) != routing_configuration.get(key):
            raise ValueError(f"workspace configuration mismatch: {key}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_workspace", type=Path)
    parser.add_argument("routing_workspace", type=Path)
    parser.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args()

    try:
        configuration = read_json(args.output_workspace / "metadata.json")
        routing_configuration = read_json(args.routing_workspace / "metadata.json")
        validate_compatible(configuration, routing_configuration)
        records = completed_records(args.output_workspace)
        expected_cases = int(configuration["output_cases"])
        if len(records) != expected_cases:
            raise ValueError(
                f"output workspace has {len(records)} completed cases; expected {expected_cases}"
            )
        routing_benchmark = read_json(args.routing_workspace / "benchmark.json")
        routing_report = routing_benchmark.get("routing")
        if not isinstance(routing_report, dict):
            raise ValueError("routing workspace has no completed routing report")
        skills_summary, output_summary = RUNNER.summarize_cases(
            records,
            float(configuration["minimum_pass_rate"]),
            float(configuration["maximum_regression"]),
        )
        routing_gate = RUNNER.routing_gate_passed(
            routing_report, float(configuration["minimum_routing_accuracy"])
        )
        output_usage = workspace_usage(args.output_workspace)
        routing_usage = workspace_usage(args.routing_workspace)
        usage = {
            key: output_usage[key] + routing_usage[key]
            for key in (
                "model_calls",
                "api_requests",
                "total_tokens",
                "total_duration_ms",
            )
        }
        usage["maximum_total_tokens"] = int(configuration["maximum_total_tokens"])
        gate_passed = bool(output_summary["gate_passed"]) and routing_gate
        report = {
            "schema_version": 2,
            "configuration": {
                **configuration,
                "assembled_from": {
                    "output_workspace": args.output_workspace.as_posix(),
                    "routing_workspace": args.routing_workspace.as_posix(),
                },
            },
            "cases": records,
            "skills": skills_summary,
            "output_summary": output_summary,
            "routing": routing_report,
            "usage": usage,
            "gate": {
                "passed": gate_passed,
                "output_passed": bool(output_summary["gate_passed"]),
                "routing_passed": routing_gate,
            },
        }
        RUNNER.validate_empty_directory(args.snapshot, "snapshot")
        args.snapshot.mkdir(parents=True, exist_ok=True)
        summary = RUNNER.markdown_summary(report)
        RUNNER.write_json(args.snapshot / "benchmark.json", report)
        (args.snapshot / "summary.md").write_text(summary, encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"workspace finalization error: {exc}", file=sys.stderr)
        return 2

    print(summary, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
