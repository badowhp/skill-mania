#!/usr/bin/env python3
"""Compare two compact skill benchmark reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


COMPARISON_FIELDS = (
    "provider",
    "model",
    "reasoning_effort",
    "judge_model",
    "judge_reasoning_effort",
    "routing_model",
    "routing_reasoning_effort",
    "case_offset",
    "context_mode",
)


def read_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("configuration"), dict):
        raise ValueError(f"{path} is not a skill benchmark report")
    if not isinstance(data.get("skills"), dict):
        raise ValueError(f"{path} has no per-skill results")
    return data


def case_keys(report: dict[str, Any]) -> list[str]:
    return sorted(
        f"{item.get('skill')}:{item.get('case')}"
        for item in report.get("cases", [])
        if isinstance(item, dict)
    )


def configuration_differences(
    baseline: dict[str, Any], current: dict[str, Any]
) -> list[str]:
    old = baseline["configuration"]
    new = current["configuration"]
    differences = [
        field
        for field in COMPARISON_FIELDS
        if old.get(field) != new.get(field)
    ]
    old_baseline = old.get("baseline") or {}
    new_baseline = new.get("baseline") or {}
    for field in ("kind", "label"):
        if old_baseline.get(field) != new_baseline.get(field):
            differences.append(f"baseline.{field}")
    if case_keys(baseline) != case_keys(current):
        differences.append("cases")
    return differences


def report_identity(report: dict[str, Any]) -> dict[str, Any]:
    configuration = report["configuration"]
    return {
        "git_sha": configuration.get("git_sha"),
        "generated_at": configuration.get("generated_at"),
        "provider": configuration.get("provider"),
        "model": configuration.get("model"),
        "judge_model": configuration.get("judge_model"),
        "routing_model": configuration.get("routing_model"),
        "case_offset": configuration.get("case_offset"),
        "baseline": configuration.get("baseline"),
    }


def rate_delta(old: Any, new: Any) -> float:
    return round(float(new or 0) - float(old or 0), 4)


def optional_rate_delta(old: Any, new: Any) -> float | None:
    if old is None or new is None:
        return None
    return rate_delta(old, new)


def compare_reports(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    old_skills = baseline["skills"]
    new_skills = current["skills"]
    common = sorted(set(old_skills) & set(new_skills))
    skills: dict[str, dict[str, Any]] = {}
    regressions: list[str] = []
    for name in common:
        old = old_skills[name]
        new = new_skills[name]
        with_delta = rate_delta(
            old.get("with_skill_pass_rate"), new.get("with_skill_pass_rate")
        )
        gate_regressed = old.get("gate_passed") is True and new.get("gate_passed") is not True
        skills[name] = {
            "baseline_with_skill_pass_rate": old.get("with_skill_pass_rate"),
            "current_with_skill_pass_rate": new.get("with_skill_pass_rate"),
            "with_skill_pass_rate_delta": with_delta,
            "baseline_without_or_old_skill_pass_rate": old.get("baseline_pass_rate"),
            "current_without_or_old_skill_pass_rate": new.get("baseline_pass_rate"),
            "comparison_baseline_pass_rate_delta": rate_delta(
                old.get("baseline_pass_rate"), new.get("baseline_pass_rate")
            ),
            "baseline_token_delta": old.get("token_delta"),
            "current_token_delta": new.get("token_delta"),
            "token_delta_change": int(new.get("token_delta", 0))
            - int(old.get("token_delta", 0)),
            "baseline_input_token_delta": old.get("input_token_delta"),
            "current_input_token_delta": new.get("input_token_delta"),
            "baseline_output_token_delta": old.get("output_token_delta"),
            "current_output_token_delta": new.get("output_token_delta"),
            "output_token_delta_change": int(new.get("output_token_delta", 0))
            - int(old.get("output_token_delta", 0)),
            "baseline_duration_delta_ms": old.get("duration_delta_ms"),
            "current_duration_delta_ms": new.get("duration_delta_ms"),
            "duration_delta_change_ms": int(new.get("duration_delta_ms", 0))
            - int(old.get("duration_delta_ms", 0)),
            "baseline_verdict": old.get("verdict"),
            "current_verdict": new.get("verdict"),
            "gate_regressed": gate_regressed,
        }
        if with_delta < 0 or gate_regressed:
            regressions.append(name)

    old_output = baseline.get("output_summary") or {}
    new_output = current.get("output_summary") or {}
    old_routing = (baseline.get("routing") or {}).get("summary") or {}
    new_routing = (current.get("routing") or {}).get("summary") or {}
    routing_delta = optional_rate_delta(
        old_routing.get("accuracy"), new_routing.get("accuracy")
    )
    if routing_delta is not None and routing_delta < 0:
        regressions.append("routing")
    old_gate = (baseline.get("gate") or {}).get("passed")
    new_gate = (current.get("gate") or {}).get("passed")
    if old_gate is True and new_gate is not True:
        regressions.append("overall-gate")

    differences = configuration_differences(baseline, current)
    return {
        "schema_version": 1,
        "comparable": not differences,
        "configuration_differences": differences,
        "baseline": report_identity(baseline),
        "current": report_identity(current),
        "added_skills": sorted(set(new_skills) - set(old_skills)),
        "removed_skills": sorted(set(old_skills) - set(new_skills)),
        "skills": skills,
        "overall": {
            "baseline_with_skill_pass_rate": old_output.get("with_skill_pass_rate"),
            "current_with_skill_pass_rate": new_output.get("with_skill_pass_rate"),
            "with_skill_pass_rate_delta": rate_delta(
                old_output.get("with_skill_pass_rate"),
                new_output.get("with_skill_pass_rate"),
            ),
            "baseline_routing_accuracy": old_routing.get("accuracy"),
            "current_routing_accuracy": new_routing.get("accuracy"),
            "routing_accuracy_delta": routing_delta,
            "baseline_gate_passed": old_gate,
            "current_gate_passed": new_gate,
        },
        "regressions": sorted(set(regressions)),
    }


def percent(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.0%}"


def signed_percent(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):+.0%}"


def markdown(report: dict[str, Any]) -> str:
    overall = report["overall"]
    lines = [
        "# Skill benchmark comparison",
        "",
        f"Comparable configuration: **{'yes' if report['comparable'] else 'no'}**.",
    ]
    if report["configuration_differences"]:
        lines.append(
            "Configuration differences: "
            + ", ".join(f"`{item}`" for item in report["configuration_differences"])
            + "."
        )
    lines.extend(
        [
            "",
            "| Skill | Previous | Current | Quality delta | Output-token change | Total-token change | Verdict change |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for name, item in report["skills"].items():
        lines.append(
            f"| `{name}` | {percent(item['baseline_with_skill_pass_rate'])} | "
            f"{percent(item['current_with_skill_pass_rate'])} | "
            f"{signed_percent(item['with_skill_pass_rate_delta'])} | "
            f"{item['output_token_delta_change']:+,} | "
            f"{item['token_delta_change']:+,} | "
            f"{item['baseline_verdict']} -> {item['current_verdict']} |"
        )
    lines.extend(
        [
            "",
            f"Overall quality delta: {signed_percent(overall['with_skill_pass_rate_delta'])}; "
            f"routing delta: {signed_percent(overall['routing_accuracy_delta'])}; "
            f"gate: {overall['baseline_gate_passed']} -> {overall['current_gate_passed']}.",
            "",
            "Potential regressions: "
            + (", ".join(f"`{item}`" for item in report["regressions"]) or "none")
            + ".",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()

    try:
        comparison = compare_reports(
            read_report(args.baseline), read_report(args.current)
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"benchmark comparison error: {exc}")
        return 2
    rendered = (
        json.dumps(comparison, indent=2) + "\n"
        if args.format == "json"
        else markdown(comparison)
    )
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return (
        1
        if args.fail_on_regression
        and comparison["comparable"]
        and comparison["regressions"]
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
