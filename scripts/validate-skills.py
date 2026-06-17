#!/usr/bin/env python3
"""Validate Agent Skills in this repository without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
OPENAI_INTERFACE_KEYS = ("display_name", "short_description", "default_prompt")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening YAML frontmatter marker")

    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
    if end is None:
        raise ValueError("missing closing YAML frontmatter marker")

    data: dict[str, str] = {}
    current_block_key: str | None = None
    current_block: list[str] = []

    def flush_block() -> None:
        nonlocal current_block_key, current_block
        if current_block_key is not None:
            data[current_block_key] = "\n".join(current_block).strip()
        current_block_key = None
        current_block = []

    for raw_line in lines[1:end]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if current_block_key and raw_line.startswith((" ", "\t")):
            current_block.append(raw_line.strip())
            continue

        flush_block()
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if not match:
            continue

        key, value = match.group(1), match.group(2).strip()
        if value in {"|", ">"}:
            current_block_key = key
            current_block = []
            continue

        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        data[key] = value

    flush_block()
    return data, lines


def validate_links(skill_dir: Path, lines: list[str]) -> list[str]:
    errors: list[str] = []
    for line_no, line in enumerate(lines, start=1):
        for target in LINK_RE.findall(line):
            if (
                target.startswith(("http://", "https://", "mailto:", "#"))
                or target.startswith("/")
                or target.startswith("data:")
            ):
                continue
            clean_target = target.split("#", 1)[0]
            if not clean_target:
                continue
            if not (skill_dir / clean_target).exists():
                errors.append(f"line {line_no}: broken relative link {target!r}")
    return errors


def validate_reference_routing(skill_dir: Path, lines: list[str]) -> list[str]:
    errors: list[str] = []
    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        return errors

    body = "\n".join(lines)
    for reference_file in sorted(path for path in references_dir.rglob("*") if path.is_file()):
        relative_path = reference_file.relative_to(skill_dir).as_posix()
        if relative_path not in body:
            errors.append(f"reference {relative_path!r} is not linked from SKILL.md")

    return errors


def strip_yaml_quotes(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def validate_openai_yaml(path: Path) -> list[str]:
    errors: list[str] = []
    interface: dict[str, str] = {}
    current_section: str | None = None

    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if not raw_line.startswith((" ", "\t")):
            if not raw_line.endswith(":"):
                errors.append(f"line {line_no}: expected top-level section")
                continue
            current_section = raw_line[:-1].strip()
            if current_section != "interface":
                errors.append(f"line {line_no}: unsupported top-level key {current_section!r}")
            continue

        if current_section != "interface":
            errors.append(f"line {line_no}: metadata must be under interface")
            continue

        match = re.match(r"^\s{2}([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if not match:
            errors.append(f"line {line_no}: expected two-space indented key")
            continue

        key, value = match.group(1), strip_yaml_quotes(match.group(2).strip())
        interface[key] = value

    for key in OPENAI_INTERFACE_KEYS:
        if not interface.get(key):
            errors.append(f"interface.{key} is required")

    return errors


def validate_agents_metadata(skill_dir: Path) -> list[str]:
    metadata_file = skill_dir / "agents" / "openai.yaml"
    if not metadata_file.exists():
        return []

    errors = validate_openai_yaml(metadata_file)
    return [f"agents/openai.yaml: {error}" for error in errors]


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"

    try:
        frontmatter, lines = parse_frontmatter(skill_file)
    except ValueError as exc:
        return [str(exc)]

    name = frontmatter.get("name", "").strip()
    description = frontmatter.get("description", "").strip()

    if not name:
        errors.append("frontmatter.name is required")
    elif not NAME_RE.match(name) or "--" in name:
        errors.append(
            "frontmatter.name must use lowercase letters, digits, and single hyphens"
        )
    elif name != skill_dir.name:
        errors.append(f"frontmatter.name {name!r} must match directory {skill_dir.name!r}")

    if not description:
        errors.append("frontmatter.description is required")
    elif len(description) > 1024:
        errors.append("frontmatter.description must be 1024 characters or less")

    if len(lines) > 500:
        errors.append(f"SKILL.md is {len(lines)} lines; keep it below 500 lines")

    errors.extend(validate_links(skill_dir, lines))
    errors.extend(validate_reference_routing(skill_dir, lines))
    errors.extend(validate_agents_metadata(skill_dir))
    return errors


def require_string(data: dict[str, object], key: str, path: Path) -> list[str]:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        return [f"{path}: {key} is required"]
    return []


def require_object(data: dict[str, object], key: str, path: Path) -> tuple[dict[str, object] | None, list[str]]:
    value = data.get(key)
    if not isinstance(value, dict):
        return None, [f"{path}: {key} object is required"]
    return value, []


def require_plugins(data: dict[str, object], path: Path) -> tuple[list[object], list[str]]:
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        return [], [f"{path}: plugins must be a non-empty list"]
    return plugins, []


def load_json_object(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    if not path.is_file():
        return None, [f"{path}: file is required"]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc.msg}"]

    if not isinstance(data, dict):
        return None, [f"{path}: top-level JSON value must be an object"]

    return data, []


def validate_codex_plugin_manifest(repo_root: Path) -> list[str]:
    path = repo_root / "plugins" / "skill-mania" / ".codex-plugin" / "plugin.json"
    data, errors = load_json_object(path)
    if data is None:
        return errors

    for key in ("name", "version", "description", "skills"):
        errors.extend(require_string(data, key, path))

    interface, interface_errors = require_object(data, "interface", path)
    errors.extend(interface_errors)
    if interface is not None:
        for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            errors.extend(require_string(interface, key, path))

    skills_path = data.get("skills")
    plugin_root = path.parent.parent
    if isinstance(skills_path, str) and not (plugin_root / skills_path).exists():
        errors.append(f"{path}: skills path {skills_path!r} does not exist")

    return errors


def validate_claude_plugin_manifest(repo_root: Path) -> list[str]:
    path = repo_root / "plugins" / "skill-mania" / ".claude-plugin" / "plugin.json"
    data, errors = load_json_object(path)
    if data is None:
        return errors

    for key in ("name", "version", "description"):
        errors.extend(require_string(data, key, path))

    author, author_errors = require_object(data, "author", path)
    errors.extend(author_errors)
    if author is not None:
        errors.extend(require_string(author, "name", path))

    return errors


def validate_codex_marketplace(repo_root: Path) -> list[str]:
    path = repo_root / ".agents" / "plugins" / "marketplace.json"
    data, errors = load_json_object(path)
    if data is None:
        return errors

    errors.extend(require_string(data, "name", path))
    plugins, plugin_errors = require_plugins(data, path)
    errors.extend(plugin_errors)

    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            errors.append(f"{path}: plugins[{index}] must be an object")
            continue
        for key in ("name", "category"):
            errors.extend(require_string(plugin, key, path))
        source, source_errors = require_object(plugin, "source", path)
        errors.extend(source_errors)
        if source is not None:
            for key in ("source", "path"):
                errors.extend(require_string(source, key, path))
        policy, policy_errors = require_object(plugin, "policy", path)
        errors.extend(policy_errors)
        if policy is not None:
            for key in ("installation", "authentication"):
                errors.extend(require_string(policy, key, path))

    return errors


def validate_claude_marketplace(repo_root: Path) -> list[str]:
    path = repo_root / ".claude-plugin" / "marketplace.json"
    data, errors = load_json_object(path)
    if data is None:
        return errors

    for key in ("name", "description"):
        errors.extend(require_string(data, key, path))
    owner, owner_errors = require_object(data, "owner", path)
    errors.extend(owner_errors)
    if owner is not None:
        errors.extend(require_string(owner, "name", path))

    plugins, plugin_errors = require_plugins(data, path)
    errors.extend(plugin_errors)
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            errors.append(f"{path}: plugins[{index}] must be an object")
            continue
        for key in ("name", "displayName", "source", "description", "category"):
            errors.extend(require_string(plugin, key, path))

    return errors


def validate_repo_metadata(repo_root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_codex_plugin_manifest(repo_root))
    errors.extend(validate_claude_plugin_manifest(repo_root))
    errors.extend(validate_codex_marketplace(repo_root))
    errors.extend(validate_claude_marketplace(repo_root))
    return errors


def iter_skill_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        child
        for child in root.iterdir()
        if child.is_dir() and not child.name.startswith(".") and (child / "SKILL.md").is_file()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills.")
    parser.add_argument("roots", nargs="*", default=["skills"], help="Skills root directories")
    args = parser.parse_args()

    failed = False
    saw_skills = False
    for root_arg in args.roots:
        root = Path(root_arg)
        skill_dirs = iter_skill_dirs(root)
        if not skill_dirs:
            failed = True
            print(f"No skills found under {root}", file=sys.stderr)
            continue

        saw_skills = True
        for skill_dir in skill_dirs:
            errors = validate_skill(skill_dir)
            if errors:
                failed = True
                print(f"{skill_dir}:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(f"ok {skill_dir}")

    metadata_errors = validate_repo_metadata(Path(__file__).resolve().parents[1])
    if metadata_errors:
        failed = True
        print("repository metadata:")
        for error in metadata_errors:
            print(f"  - {error}")
    else:
        print("ok repository metadata")

    return 1 if failed or not saw_skills else 0


if __name__ == "__main__":
    raise SystemExit(main())
