#!/usr/bin/env python3
"""Load and validate overlapping Skill Mania install groups."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


GROUP_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class SkillGroup:
    id: str
    name: str
    description: str
    aliases: tuple[str, ...]
    skills: tuple[str, ...]


def available_skills(skills_dir: Path) -> set[str]:
    return {
        path.parent.name
        for path in skills_dir.glob("*/SKILL.md")
        if path.parent.is_dir()
    }


def _non_empty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _string_list(value: object, label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise ValueError(f"{label} must be {qualifier}")
    items = tuple(_non_empty_string(item, label) for item in value)
    if len(items) != len(set(items)):
        raise ValueError(f"{label} contains duplicates")
    return items


def load_groups(path: Path) -> list[SkillGroup]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("skill groups require schema_version 1")
    raw_groups = data.get("groups")
    if not isinstance(raw_groups, list) or not raw_groups:
        raise ValueError("skill groups must contain a non-empty groups list")

    groups: list[SkillGroup] = []
    for index, raw_group in enumerate(raw_groups):
        if not isinstance(raw_group, dict):
            raise ValueError(f"groups[{index}] must be an object")
        group_id = _non_empty_string(raw_group.get("id"), f"groups[{index}].id")
        if not GROUP_ID_RE.fullmatch(group_id):
            raise ValueError(f"groups[{index}].id must be lowercase and hyphenated")
        groups.append(
            SkillGroup(
                id=group_id,
                name=_non_empty_string(raw_group.get("name"), f"groups[{index}].name"),
                description=_non_empty_string(
                    raw_group.get("description"), f"groups[{index}].description"
                ),
                aliases=_string_list(
                    raw_group.get("aliases", []),
                    f"groups[{index}].aliases",
                    allow_empty=True,
                ),
                skills=_string_list(raw_group.get("skills"), f"groups[{index}].skills"),
            )
        )
    return groups


def validate_groups(groups: list[SkillGroup], skills_dir: Path) -> list[str]:
    errors: list[str] = []
    known = available_skills(skills_dir)
    identifiers: dict[str, str] = {}
    represented: set[str] = set()

    for group in groups:
        for identifier in (group.id, *group.aliases):
            owner = identifiers.get(identifier)
            if owner is not None:
                errors.append(
                    f"group identifier {identifier!r} is shared by {owner!r} and {group.id!r}"
                )
            else:
                identifiers[identifier] = group.id
        unknown = sorted(set(group.skills) - known)
        if unknown:
            errors.append(f"group {group.id!r} contains unknown skills: {', '.join(unknown)}")
        represented.update(group.skills)

    missing = sorted(known - represented)
    if missing:
        errors.append(f"skills missing from every install group: {', '.join(missing)}")
    return errors


def resolve_groups(groups: list[SkillGroup], names: list[str]) -> list[str]:
    index: dict[str, SkillGroup] = {}
    for group in groups:
        index[group.id] = group
        for alias in group.aliases:
            index[alias] = group

    unknown = sorted(set(names) - set(index))
    if unknown:
        expected = ", ".join(group.id for group in groups)
        raise ValueError(f"unknown groups: {', '.join(unknown)}; expected one of {expected}")

    selected: list[str] = []
    seen: set[str] = set()
    for name in names:
        for skill in index[name].skills:
            if skill not in seen:
                selected.append(skill)
                seen.add(skill)
    return selected
