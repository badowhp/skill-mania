#!/usr/bin/env python3
"""Report and enforce context budgets for canonical Agent Skills."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STARTUP_DESCRIPTION_CHARS = 6500
SKILL_MD_CHARS = 17500
REFERENCE_CHARS = 40000
SKILL_REFERENCE_TOTAL_CHARS = 50000


def estimate_tokens(characters: int) -> tuple[int, int]:
    """Return a conservative English/Markdown BPE estimate range."""
    return round(characters / 4.2), round(characters / 3.5)


def frontmatter_value(text: str, key: str) -> str:
    frontmatter = text.split("---", 2)[1]
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip().strip('"\'')


def collect(root: Path) -> dict[str, object]:
    skills: list[dict[str, object]] = []
    startup_parts: list[str] = []

    for skill_file in sorted(root.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        name = frontmatter_value(text, "name")
        description = frontmatter_value(text, "description")
        skill_path = f"{root.name}/{skill_file.relative_to(root).as_posix()}"
        startup_parts.append(f"{name}: {description} ({skill_path})")
        low, high = estimate_tokens(len(text))
        references = []
        for reference in sorted((skill_file.parent / "references").rglob("*.md")):
            reference_text = reference.read_text(encoding="utf-8")
            ref_low, ref_high = estimate_tokens(len(reference_text))
            references.append(
                {
                    "path": reference.as_posix(),
                    "characters": len(reference_text),
                    "estimated_tokens": [ref_low, ref_high],
                    "within_budget": len(reference_text) <= REFERENCE_CHARS,
                }
            )
        reference_characters = sum(reference["characters"] for reference in references)
        reference_low, reference_high = estimate_tokens(reference_characters)
        skills.append(
            {
                "name": name,
                "path": skill_path,
                "characters": len(text),
                "estimated_tokens": [low, high],
                "within_budget": len(text) <= SKILL_MD_CHARS,
                "references": references,
                "reference_total": {
                    "characters": reference_characters,
                    "estimated_tokens": [reference_low, reference_high],
                    "within_budget": reference_characters <= SKILL_REFERENCE_TOTAL_CHARS,
                },
            }
        )

    startup_text = "\n".join(startup_parts)
    startup_low, startup_high = estimate_tokens(len(startup_text))
    return {
        "limits": {
            "startup_description_characters": STARTUP_DESCRIPTION_CHARS,
            "skill_md_characters": SKILL_MD_CHARS,
            "reference_characters": REFERENCE_CHARS,
            "skill_reference_total_characters": SKILL_REFERENCE_TOTAL_CHARS,
        },
        "startup": {
            "characters": len(startup_text),
            "estimated_tokens": [startup_low, startup_high],
            "within_budget": len(startup_text) <= STARTUP_DESCRIPTION_CHARS,
        },
        "skills": skills,
    }


def failures(report: dict[str, object]) -> list[str]:
    errors: list[str] = []
    startup = report["startup"]
    if isinstance(startup, dict) and not startup["within_budget"]:
        errors.append("startup skill metadata exceeds the repository budget")
    for skill in report["skills"]:
        if not skill["within_budget"]:
            errors.append(f"{skill['path']} exceeds the SKILL.md budget")
        reference_total = skill["reference_total"]
        if not reference_total["within_budget"]:
            errors.append(f"{skill['path']} references exceed the total reference budget")
        for reference in skill["references"]:
            if not reference["within_budget"]:
                errors.append(f"{reference['path']} exceeds the reference budget")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default="skills", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true", help="exit nonzero when a budget is exceeded")
    args = parser.parse_args()

    report = collect(args.root)
    errors = failures(report)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        startup = report["startup"]
        print(
            f"startup metadata: {startup['characters']} chars, "
            f"~{startup['estimated_tokens'][0]}-{startup['estimated_tokens'][1]} tokens"
        )
        for skill in report["skills"]:
            estimate = skill["estimated_tokens"]
            print(
                f"{skill['name']}: {skill['characters']} chars, "
                f"~{estimate[0]}-{estimate[1]} tokens, {len(skill['references'])} references, "
                f"~{skill['reference_total']['estimated_tokens'][0]}-"
                f"{skill['reference_total']['estimated_tokens'][1]} reference tokens"
            )
        for error in errors:
            print(f"budget error: {error}")
    return 1 if args.check and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
