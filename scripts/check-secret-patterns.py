#!/usr/bin/env python3
"""Reject high-confidence credential patterns from repository text files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXCLUDED_PARTS = frozenset((".git", ".cache", ".tmp", "node_modules", "__pycache__"))
PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("OpenAI API key", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b")),
)
SAFE_ENV_TEMPLATE_NAMES = frozenset((".env.example", ".env.sample", ".env.template"))


def candidate_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        parts = path.relative_to(root).parts
        if (
            path.is_symlink()
            or not path.is_file()
            or EXCLUDED_PARTS.intersection(parts)
            or any(part.endswith("-workspace") for part in parts)
        ):
            continue
        if path.stat().st_size > 2_000_000:
            continue
        files.append(path)
    return sorted(files)


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in candidate_files(root):
        relative = path.relative_to(root)
        if (
            path.name == ".env"
            or path.name.startswith(".env.")
            and path.name not in SAFE_ENV_TEMPLATE_NAMES
        ):
            findings.append(f"{relative}: tracked .env-style file")
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            findings.append(f"{relative}: could not read file: {exc}")
            continue
        if b"\x00" in raw:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(f"{relative}:{line_number}: possible {label}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    findings = scan(args.root.resolve())
    for finding in findings:
        print(finding)
    if findings:
        return 1
    print("no high-confidence credential patterns found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
