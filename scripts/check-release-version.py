#!/usr/bin/env python3
"""Verify synchronized plugin versions and an optional release tag."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_version(path: Path) -> str:
    return str(json.loads(path.read_text(encoding="utf-8"))["version"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", nargs="?", help="expected tag, for example v0.2.0")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    manifests = [
        root / "plugins" / "skill-mania" / ".codex-plugin" / "plugin.json",
        root / "plugins" / "skill-mania" / ".claude-plugin" / "plugin.json",
    ]
    versions = {read_version(path) for path in manifests}
    if len(versions) != 1:
        print("plugin manifest versions do not match")
        return 1

    version = versions.pop()
    if args.tag and args.tag != f"v{version}":
        print(f"release tag {args.tag!r} does not match manifest version v{version}")
        return 1

    print(f"plugin version {version} is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
