#!/usr/bin/env python3
"""Validate the repository's cross-skill routing evaluation matrix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_CASE_KEYS = ("id", "prompt", "lead_skill", "near_miss_skills", "why")
OVERLAY_SKILLS = frozenset(("caveman", "ponytail"))
REQUIRED_OVERLAPS = {
    frozenset(("agent-context-maintainer", "skill-curator")),
    frozenset(("austrian-law-helper", "writing-assistant")),
    frozenset(("design-engineer", "design-reviewer")),
    frozenset(("design-reviewer", "visual-qa")),
    frozenset(("gameplay-consultant", "godot-game-creation-engineer")),
    frozenset(("project-manager", "senior-developer")),
    frozenset(("project-manager", "software-architect")),
    frozenset(("security-engineer", "senior-devops-engineer")),
    frozenset(("senior-developer", "senior-devops-engineer")),
    frozenset(("senior-developer", "testing-engineer")),
    frozenset(("seo-geo", "writing-assistant")),
}


def skill_names(root: Path) -> set[str]:
    return {
        path.parent.name
        for path in root.glob("*/SKILL.md")
        if path.parent.is_dir()
    }


def load_matrix(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    if not path.is_file():
        return None, [f"{path}: file is required"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc.msg}"]
    if not isinstance(data, dict):
        return None, [f"{path}: top-level value must be an object"]
    return data, []


def validate_matrix(data: dict[str, object], known_skills: set[str]) -> list[str]:
    errors: list[str] = []
    domain_skills = known_skills - OVERLAY_SKILLS
    known_overlays = known_skills & OVERLAY_SKILLS
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < len(domain_skills):
        return ["cases must cover every production domain skill"]

    seen_ids: set[str] = set()
    covered_leads: set[str] = set()
    covered_overlays: set[str] = set()
    observed_overlaps: set[frozenset[str]] = set()

    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in REQUIRED_CASE_KEYS:
            if key not in case:
                errors.append(f"{prefix}.{key} is required")

        case_id = case.get("id")
        if not isinstance(case_id, str) or len(case_id.strip()) < 3:
            errors.append(f"{prefix}.id must be a descriptive string")
        elif case_id in seen_ids:
            errors.append(f"{prefix}.id {case_id!r} is duplicated")
        else:
            seen_ids.add(case_id)

        prompt = case.get("prompt")
        if not isinstance(prompt, str) or len(prompt.strip()) < 20:
            errors.append(f"{prefix}.prompt must be a descriptive string")

        why = case.get("why")
        if not isinstance(why, str) or len(why.strip()) < 20:
            errors.append(f"{prefix}.why must explain the routing decision")

        lead = case.get("lead_skill")
        if not isinstance(lead, str) or lead not in known_skills:
            errors.append(f"{prefix}.lead_skill must name a production skill")
            continue
        if lead in OVERLAY_SKILLS:
            errors.append(
                f"{prefix}.lead_skill must name a domain skill; put {lead!r} in overlay_skills"
            )
            continue
        covered_leads.add(lead)

        near_misses = case.get("near_miss_skills")
        if not isinstance(near_misses, list) or not near_misses:
            errors.append(f"{prefix}.near_miss_skills must be a non-empty list")
            continue
        seen_near_misses: set[str] = set()
        for peer in near_misses:
            if not isinstance(peer, str) or peer not in known_skills:
                errors.append(f"{prefix}.near_miss_skills contains an unknown skill")
                continue
            if peer == lead:
                errors.append(f"{prefix}.near_miss_skills must not contain the lead skill")
                continue
            if peer in OVERLAY_SKILLS:
                errors.append(
                    f"{prefix}.near_miss_skills must not contain overlays; use overlay_skills"
                )
                continue
            if peer in seen_near_misses:
                errors.append(f"{prefix}.near_miss_skills must not contain duplicates")
                continue
            seen_near_misses.add(peer)
            observed_overlaps.add(frozenset((lead, peer)))

        overlays = case.get("overlay_skills")
        if overlays is not None:
            if not isinstance(overlays, list) or not overlays:
                errors.append(f"{prefix}.overlay_skills must be a non-empty list when present")
            else:
                seen_overlays: set[str] = set()
                for overlay in overlays:
                    if not isinstance(overlay, str) or overlay not in known_overlays:
                        errors.append(
                            f"{prefix}.overlay_skills must contain only production overlays"
                        )
                        continue
                    if overlay in seen_overlays:
                        errors.append(f"{prefix}.overlay_skills must not contain duplicates")
                        continue
                    seen_overlays.add(overlay)
                    covered_overlays.add(overlay)

    missing_leads = sorted(domain_skills - covered_leads)
    if missing_leads:
        errors.append(f"routing matrix is missing lead coverage for: {', '.join(missing_leads)}")

    missing_overlays = sorted(known_overlays - covered_overlays)
    if missing_overlays:
        errors.append(
            f"routing matrix is missing overlay coverage for: {', '.join(missing_overlays)}"
        )

    missing_overlaps = REQUIRED_OVERLAPS - observed_overlaps
    if missing_overlaps:
        pairs = ", ".join("/".join(sorted(pair)) for pair in sorted(missing_overlaps, key=sorted))
        errors.append(f"routing matrix is missing required overlaps: {pairs}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills", type=Path, default=Path("skills"))
    parser.add_argument("--matrix", type=Path, default=Path("evals/routing-matrix.json"))
    args = parser.parse_args()

    known_skills = skill_names(args.skills)
    if not known_skills:
        print(f"{args.skills}: no production skills found", file=sys.stderr)
        return 1

    data, errors = load_matrix(args.matrix)
    if data is not None:
        errors.extend(validate_matrix(data, known_skills))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"ok {args.matrix}: {len(data['cases'])} routing cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
