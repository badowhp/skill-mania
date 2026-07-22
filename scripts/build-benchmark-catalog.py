#!/usr/bin/env python3
"""Build the durable benchmark catalog from compact snapshots and local imports."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "benchmarks" / "catalog.json"
DEFAULT_BASELINES = REPO_ROOT / "benchmarks" / "baselines"
IMPORT_LABEL = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def eval_summary(skill_dir: Path) -> dict[str, int]:
    document = read_json(skill_dir / "evals" / "evals.json")
    evals = document.get("evals")
    if not isinstance(evals, list):
        raise ValueError(f"{skill_dir}/evals/evals.json must contain an evals array")
    positive = 0
    near_miss = 0
    assertions = 0
    for item in evals:
        if not isinstance(item, dict):
            raise ValueError(f"{skill_dir}/evals/evals.json contains a non-object eval")
        if item.get("should_trigger") is True:
            positive += 1
            values = item.get("assertions", [])
            if not isinstance(values, list):
                raise ValueError(f"{skill_dir}/evals/evals.json contains invalid assertions")
            assertions += len(values)
        else:
            near_miss += 1
    return {
        "positive": positive,
        "near_miss": near_miss,
        "assertions": assertions,
    }


def skill_inventory(skills_root: Path) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for skill_dir in sorted(skills_root.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
            result[skill_dir.name] = eval_summary(skill_dir)
    if not result:
        raise ValueError(f"no skills found in {skills_root}")
    return result


def optional_string(value: object) -> str:
    return value if isinstance(value, str) else ""


def optional_int(value: object) -> int:
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else 0


def optional_float(value: object) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return 0.0


def record_id(skill: str, record: dict[str, Any]) -> str:
    identity = {
        "skill": skill,
        "generated_at": record["generated_at"],
        "git_sha": record["git_sha"],
        "model": record["model"],
        "baseline_kind": record["baseline_kind"],
        "cases": record["cases"],
        "assertions": record["assertions"],
        "with_skill_rate": record["with_skill_rate"],
        "baseline_rate": record["baseline_rate"],
        "pass_rate_delta": record["pass_rate_delta"],
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def benchmark_records(path: Path, source: str) -> dict[str, dict[str, Any]]:
    document = read_json(path)
    configuration = document.get("configuration")
    skills = document.get("skills")
    if not isinstance(configuration, dict) or not isinstance(skills, dict):
        raise ValueError(f"{path} must contain configuration and skills objects")
    generated_at = optional_string(configuration.get("generated_at"))
    if not generated_at:
        raise ValueError(f"{path} has no configuration.generated_at")
    baseline = configuration.get("baseline")
    if not isinstance(baseline, dict):
        baseline = {}

    result: dict[str, dict[str, Any]] = {}
    for name, value in skills.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError(f"{path} contains an invalid skill result")
        record: dict[str, Any] = {
            "source": source,
            "generated_at": generated_at,
            "provider": optional_string(configuration.get("provider")),
            "model": optional_string(configuration.get("model")),
            "reasoning_effort": optional_string(configuration.get("reasoning_effort")),
            "judge_model": optional_string(configuration.get("judge_model")),
            "routing_model": optional_string(configuration.get("routing_model")),
            "git_sha": optional_string(configuration.get("git_sha")),
            "baseline_kind": optional_string(baseline.get("kind")),
            "baseline_label": optional_string(baseline.get("label")),
            "runner_version": optional_int(configuration.get("runner_version")),
            "context_mode": optional_string(configuration.get("context_mode")),
            "cases": optional_int(value.get("cases")),
            "assertions": optional_int(value.get("assertions")),
            "with_skill_rate": optional_float(value.get("with_skill_pass_rate")),
            "baseline_rate": optional_float(value.get("baseline_pass_rate")),
            "pass_rate_delta": optional_float(value.get("pass_rate_delta")),
            "verdict": optional_string(value.get("verdict")),
            "gate_passed": value.get("gate_passed") is True,
            "with_skill_tokens": optional_int(value.get("with_skill_tokens")),
            "baseline_tokens": optional_int(value.get("baseline_tokens")),
            "with_skill_duration_ms": optional_int(value.get("with_skill_duration_ms")),
            "baseline_duration_ms": optional_int(value.get("baseline_duration_ms")),
        }
        record["id"] = record_id(name, record)
        result[name] = record
    return result


def source_priority(source: str) -> int:
    if source.startswith("baselines/"):
        return 3
    if source.startswith("imported/"):
        return 2
    return 1


def add_record(
    records: dict[str, dict[str, dict[str, Any]]],
    inventory: dict[str, dict[str, int]],
    skill: str,
    record: dict[str, Any],
) -> None:
    if skill not in inventory:
        raise ValueError(f"benchmark references unknown skill {skill}")
    identifier = record.get("id")
    if not isinstance(identifier, str) or not identifier:
        record = dict(record)
        record["id"] = record_id(skill, record)
        identifier = record["id"]
    current = records.setdefault(skill, {}).get(identifier)
    if current is None or source_priority(str(record.get("source", ""))) > source_priority(
        str(current.get("source", ""))
    ):
        records[skill][identifier] = record


def existing_records(
    output: Path,
    inventory: dict[str, dict[str, int]],
    records: dict[str, dict[str, dict[str, Any]]],
) -> None:
    if not output.is_file():
        return
    document = read_json(output)
    if document.get("schema_version") != 1:
        raise ValueError(f"{output} uses an unsupported schema version")
    skills = document.get("skills")
    if not isinstance(skills, dict):
        raise ValueError(f"{output} must contain a skills object")
    for name, entry in skills.items():
        if name not in inventory or not isinstance(entry, dict):
            continue
        runs = entry.get("runs", [])
        if not isinstance(runs, list):
            raise ValueError(f"{output} has invalid runs for {name}")
        for run in runs:
            if not isinstance(run, dict):
                raise ValueError(f"{output} has a non-object run for {name}")
            add_record(records, inventory, name, run)


def import_argument(value: str) -> tuple[str, Path]:
    if "=" in value:
        label, raw_path = value.split("=", 1)
    else:
        raw_path = value
        label = Path(raw_path).parent.name or Path(raw_path).stem
    if not IMPORT_LABEL.fullmatch(label):
        raise argparse.ArgumentTypeError(
            "import labels use lowercase letters, numbers, dots, underscores, or hyphens"
        )
    path = Path(raw_path).expanduser().resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"benchmark import does not exist: {path}")
    return label, path


def build_catalog(
    skills_root: Path,
    baselines_root: Path,
    output: Path,
    imports: list[tuple[str, Path]],
    preserve: bool,
) -> dict[str, Any]:
    inventory = skill_inventory(skills_root)
    records: dict[str, dict[str, dict[str, Any]]] = {}
    if preserve:
        existing_records(output, inventory, records)

    if baselines_root.is_dir():
        for path in sorted(baselines_root.rglob("benchmark.json")):
            source = path.parent.relative_to(baselines_root.parent).as_posix()
            for skill, record in benchmark_records(path, source).items():
                add_record(records, inventory, skill, record)

    for label, path in imports:
        for skill, record in benchmark_records(path, f"imported/{label}").items():
            add_record(records, inventory, skill, record)

    skills: dict[str, dict[str, Any]] = {}
    generated_dates: list[str] = []
    saved = 0
    runs_total = 0
    for name, evals in inventory.items():
        runs = sorted(
            records.get(name, {}).values(),
            key=lambda item: (
                str(item.get("generated_at", "")),
                str(item.get("source", "")),
                str(item.get("id", "")),
            ),
        )
        if runs:
            saved += 1
            runs_total += len(runs)
            generated_dates.extend(str(run["generated_at"]) for run in runs)
        skills[name] = {
            "status": "saved" if runs else "not-saved",
            "evals": evals,
            "latest": runs[-1] if runs else None,
            "runs": runs,
        }

    return {
        "schema_version": 1,
        "policy": (
            "Durable aggregate of compact benchmark summaries. Raw prompts, model responses, "
            "credentials, and machine-specific workspace paths are not stored."
        ),
        "coverage": {
            "skills": len(skills),
            "with_saved_benchmark": saved,
            "without_saved_benchmark": len(skills) - saved,
            "saved_runs": runs_total,
            "latest_generated_at": max(generated_dates, default=None),
        },
        "skills": skills,
    }


def rendered(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, default=REPO_ROOT / "skills")
    parser.add_argument("--baselines-root", type=Path, default=DEFAULT_BASELINES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        type=import_argument,
        metavar="LABEL=BENCHMARK_JSON",
        help="import a compact local result without committing its raw workspace",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="discard archived imports and rebuild only from current inputs",
    )
    parser.add_argument("--check", action="store_true", help="fail when the catalog is stale")
    args = parser.parse_args()

    try:
        output = args.output.resolve()
        document = build_catalog(
            args.skills_root.resolve(),
            args.baselines_root.resolve(),
            output,
            args.include,
            preserve=not args.rebuild,
        )
        content = rendered(document)
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != content:
                print(f"benchmark catalog is stale: {output}", file=sys.stderr)
                return 1
            print(
                f"benchmark catalog covers {document['coverage']['skills']} skills and "
                f"{document['coverage']['saved_runs']} saved runs"
            )
            return 0
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(f".{output.name}.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"benchmark catalog error: {exc}", file=sys.stderr)
        return 2

    coverage = document["coverage"]
    print(
        f"wrote {output}: {coverage['with_saved_benchmark']} of "
        f"{coverage['skills']} skills have {coverage['saved_runs']} saved runs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
