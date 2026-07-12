#!/usr/bin/env python3
"""Enforce a small dependency and permissions policy for GitHub Actions."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


USES_RE = re.compile(r"^\s*-\s+uses:\s*([^\s#]+)", re.MULTILINE)
PINNED_ACTION_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not re.search(r"^permissions:\s*$", text, re.MULTILINE):
        errors.append("top-level permissions are required")
    if re.search(r"^\s*pull_request_target:\s*$", text, re.MULTILINE):
        errors.append("pull_request_target is not allowed")
    if re.search(r"^\s*pull_request:\s*$", text, re.MULTILINE) and "secrets." in text:
        errors.append("pull request workflows must not reference repository secrets")
    if re.search(r"^\s*workflow_dispatch:\s*$", text, re.MULTILINE) and "secrets." in text:
        required_controls = {
            "default-branch job guard": (
                "github.ref_name == github.event.repository.default_branch"
            ),
            "explicit default-branch checkout": (
                "ref: ${{ github.event.repository.default_branch }}"
            ),
            "protected evaluation environment": "environment: skill-evals",
        }
        for label, marker in required_controls.items():
            if marker not in text:
                errors.append(f"secret-backed manual workflow needs {label}")
    if re.search(r"^\s*permissions:\s*write-all\s*$", text, re.MULTILINE):
        errors.append("permissions: write-all is not allowed")
    if path.name != "release.yml" and re.search(
        r"^\s*contents:\s*write\s*$", text, re.MULTILINE
    ):
        errors.append("contents: write is reserved for release.yml")
    if "actions/checkout@" in text and "persist-credentials: false" not in text:
        errors.append("checkout credentials must not persist")
    for line in text.splitlines():
        if "secrets." not in line:
            continue
        if not re.fullmatch(
            r"\s{10,}[A-Z][A-Z0-9_]*:\s*\$\{\{\s*secrets\.[A-Z][A-Z0-9_]*\s*}}\s*",
            line,
        ):
            errors.append("secret references must be scoped to a step env variable")
    if re.search(r"curl\b[^\n|]*\|\s*(?:ba)?sh\b", text):
        errors.append("download-and-execute shell pipelines are not allowed")
    for action in USES_RE.findall(text):
        if action.startswith(("./", "docker://")):
            continue
        if not PINNED_ACTION_RE.fullmatch(action):
            errors.append(f"third-party action must be pinned to a full commit SHA: {action}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workflows",
        type=Path,
        default=Path(__file__).resolve().parents[1] / ".github" / "workflows",
    )
    args = parser.parse_args()

    workflow_files = sorted((*args.workflows.glob("*.yml"), *args.workflows.glob("*.yaml")))
    if not workflow_files:
        print(f"{args.workflows}: no workflow files found")
        return 1
    failures = []
    for workflow in workflow_files:
        for error in validate(workflow):
            failures.append(f"{workflow}: {error}")
    for failure in failures:
        print(failure)
    if failures:
        return 1
    print(f"workflow security policy passed for {len(workflow_files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
