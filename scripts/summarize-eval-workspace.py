#!/usr/bin/env python3
"""Aggregate paired skill-evaluation grading and timing files."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


BASELINE_NAMES = ("without_skill", "old_skill", "baseline")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def grading_counts(path: Path) -> tuple[int, int]:
    grading = read_json(path)
    summary = grading.get("summary")
    if isinstance(summary, dict):
        return int(summary.get("passed", 0)), int(summary.get("total", 0))
    results = grading.get("assertion_results", [])
    if not isinstance(results, list):
        raise ValueError(f"{path} assertion_results must be a list")
    return sum(item.get("passed") is True for item in results), len(results)


def run_metrics(run_dir: Path) -> dict[str, int]:
    passed, total = grading_counts(run_dir / "grading.json")
    timing = read_json(run_dir / "timing.json")
    return {
        "passed": passed,
        "total": total,
        "input_tokens": int(timing.get("input_tokens", 0)),
        "output_tokens": int(timing.get("output_tokens", 0)),
        "reasoning_tokens": int(timing.get("reasoning_tokens", 0)),
        "tokens": int(timing["total_tokens"]),
        "duration_ms": int(timing["duration_ms"]),
    }


def summarize(workspace: Path) -> dict[str, Any]:
    cases = []
    for with_skill in sorted(workspace.rglob("with_skill")):
        if not with_skill.is_dir():
            continue
        baseline = next(
            (with_skill.parent / name for name in BASELINE_NAMES if (with_skill.parent / name).is_dir()),
            None,
        )
        if baseline is None:
            continue
        cases.append(
            {
                "case": with_skill.parent.relative_to(workspace).as_posix(),
                "with_skill": run_metrics(with_skill),
                "baseline": run_metrics(baseline),
                "baseline_kind": baseline.name,
            }
        )

    if not cases:
        raise ValueError("no paired with_skill and baseline run directories found")

    def aggregate(key: str) -> dict[str, float | int]:
        runs = [case[key] for case in cases]
        passed = sum(run["passed"] for run in runs)
        total = sum(run["total"] for run in runs)
        return {
            "passed": passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
            "median_input_tokens": round(
                statistics.median(run["input_tokens"] for run in runs)
            ),
            "median_output_tokens": round(
                statistics.median(run["output_tokens"] for run in runs)
            ),
            "median_reasoning_tokens": round(
                statistics.median(run["reasoning_tokens"] for run in runs)
            ),
            "median_tokens": round(statistics.median(run["tokens"] for run in runs)),
            "median_duration_ms": round(
                statistics.median(run["duration_ms"] for run in runs)
            ),
        }

    with_skill_summary = aggregate("with_skill")
    baseline_summary = aggregate("baseline")
    return {
        "cases": cases,
        "summary": {
            "with_skill": with_skill_summary,
            "baseline": baseline_summary,
            "pass_rate_delta": round(
                with_skill_summary["pass_rate"] - baseline_summary["pass_rate"], 4
            ),
            "median_token_delta": (
                with_skill_summary["median_tokens"] - baseline_summary["median_tokens"]
            ),
            "median_input_token_delta": (
                with_skill_summary["median_input_tokens"]
                - baseline_summary["median_input_tokens"]
            ),
            "median_output_token_delta": (
                with_skill_summary["median_output_tokens"]
                - baseline_summary["median_output_tokens"]
            ),
            "median_reasoning_token_delta": (
                with_skill_summary["median_reasoning_tokens"]
                - baseline_summary["median_reasoning_tokens"]
            ),
            "median_duration_delta_ms": (
                with_skill_summary["median_duration_ms"]
                - baseline_summary["median_duration_ms"]
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        report = summarize(args.workspace.resolve())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"evaluation workspace error: {exc}")
        return 1

    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
