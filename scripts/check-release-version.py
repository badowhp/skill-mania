#!/usr/bin/env python3
"""Verify synchronized plugin versions and an optional release tag."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
RELEASE_PATHS = (
    "skills",
    "config/install-profiles.json",
    "scripts/install-local.sh",
    "plugins/skill-mania/skills",
    "plugins/skill-mania/.codex-plugin/plugin.json",
    "plugins/skill-mania/.claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
)


def read_version(path: Path) -> str:
    return str(json.loads(path.read_text(encoding="utf-8"))["version"])


def version_tuple(version: str) -> tuple[int, int, int]:
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise ValueError(f"unsupported release version {version!r}; expected X.Y.Z")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def latest_release_tag(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "tag", "--list", "v[0-9]*", "--sort=-v:refname"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or "git tag failed")
    return next((line.strip() for line in result.stdout.splitlines() if line.strip()), None)


def release_changes_since(root: Path, tag: str) -> list[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", tag, "--", *RELEASE_PATHS],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", *RELEASE_PATHS],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked.returncode or untracked.returncode:
        detail = tracked.stderr or untracked.stderr or tracked.stdout or untracked.stdout
        raise RuntimeError(detail.strip() or "git release-content comparison failed")
    return sorted(set(tracked.stdout.splitlines()) | set(untracked.stdout.splitlines()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", nargs="?", help="expected tag, for example v0.2.0")
    parser.add_argument(
        "--require-bump",
        action="store_true",
        help="require a newer manifest version when release content differs from the latest tag",
    )
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
    try:
        current_version = version_tuple(version)
    except ValueError as exc:
        print(exc)
        return 1
    if args.tag and args.tag != f"v{version}":
        print(f"release tag {args.tag!r} does not match manifest version v{version}")
        return 1

    if args.require_bump:
        try:
            latest_tag = latest_release_tag(root)
        except RuntimeError as exc:
            print(f"could not inspect release tags: {exc}")
            return 1
        if latest_tag is None:
            print("no release tag found; skipping content-versus-version comparison")
        else:
            try:
                tagged_version = version_tuple(latest_tag.removeprefix("v"))
            except ValueError as exc:
                print(exc)
                return 1
            try:
                changed = release_changes_since(root, latest_tag)
            except RuntimeError as exc:
                print(f"could not compare release content: {exc}")
                return 1
            if current_version < tagged_version:
                print(f"manifest version {version} is older than latest release {latest_tag}")
                return 1
            if current_version == tagged_version and changed:
                print(
                    f"release content changed since {latest_tag} without a manifest version bump:"
                )
                for path in changed:
                    print(f"  {path}")
                return 1

    print(f"plugin version {version} is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
