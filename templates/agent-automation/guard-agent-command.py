#!/usr/bin/env python3
"""Reject a small set of unmistakably destructive shell commands from hook input."""

from __future__ import annotations

import json
import re
import sys
from typing import Any


BLOCKED = (
    (re.compile(r"\brm\s+(?:-[A-Za-z]*[rf][A-Za-z]*\s+|--recursive\s+--force\s+)(?:/|~)(?:\s|$)"), "recursive deletion of a filesystem root"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "hard git reset"),
    (re.compile(r"\bgit\s+clean\s+-[A-Za-z]*f[A-Za-z]*\b"), "forced git clean"),
)


def strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in strings(child)]
    if isinstance(value, dict):
        return [item for child in value.values() for item in strings(child)]
    return []


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("agent command guard: expected JSON hook input", file=sys.stderr)
        return 2

    command = "\n".join(strings(payload.get("tool_input", payload)))
    for pattern, reason in BLOCKED:
        if pattern.search(command):
            print(f"agent command guard: blocked {reason}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
