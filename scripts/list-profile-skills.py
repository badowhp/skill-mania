#!/usr/bin/env python3
"""Resolve and validate named local-install skill profiles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROFILE_NAMES = frozenset(("core", "content", "games", "regional"))


def load_profiles(path: Path) -> dict[str, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != PROFILE_NAMES:
        raise ValueError("profiles must contain exactly core, content, games, and regional")
    profiles: dict[str, list[str]] = {}
    for name, skills in data.items():
        if not isinstance(skills, list) or not skills or not all(
            isinstance(skill, str) and skill for skill in skills
        ):
            raise ValueError(f"profile {name!r} must contain non-empty skill names")
        if len(skills) != len(set(skills)):
            raise ValueError(f"profile {name!r} contains duplicate skills")
        profiles[name] = skills
    return profiles


def validate_inventory(profiles: dict[str, list[str]], skills_dir: Path) -> list[str]:
    errors: list[str] = []
    available = {path.parent.name for path in skills_dir.glob("*/SKILL.md")}
    owners: dict[str, list[str]] = {}
    for profile, skills in profiles.items():
        for skill in skills:
            owners.setdefault(skill, []).append(profile)
    unknown = sorted(set(owners) - available)
    missing = sorted(available - set(owners))
    duplicate = sorted(skill for skill, names in owners.items() if len(names) > 1)
    if unknown:
        errors.append(f"profiles contain unknown skills: {', '.join(unknown)}")
    if missing:
        errors.append(f"skills missing from profiles: {', '.join(missing)}")
    if duplicate:
        errors.append(f"skills assigned to multiple profiles: {', '.join(duplicate)}")
    return errors


def resolve(profiles: dict[str, list[str]], names: list[str]) -> list[str]:
    unknown = sorted(set(names) - set(profiles))
    if unknown:
        raise ValueError(
            f"unknown profiles: {', '.join(unknown)}; expected core, content, games, or regional"
        )
    return list(dict.fromkeys(skill for name in names for skill in profiles[name]))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles", nargs="*")
    parser.add_argument("--config", type=Path, default=root / "config" / "install-profiles.json")
    parser.add_argument("--skills-dir", type=Path, default=root / "skills")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        profiles = load_profiles(args.config)
        errors = validate_inventory(profiles, args.skills_dir)
        if errors:
            raise ValueError("; ".join(errors))
        selected = resolve(profiles, args.profiles)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"install profile error: {exc}", file=sys.stderr)
        return 1
    if args.check:
        print(f"install profiles cover {sum(len(items) for items in profiles.values())} skills")
    else:
        for skill in selected:
            print(skill)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
