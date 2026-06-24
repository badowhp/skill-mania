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
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$"
)
FRONTMATTER_KEYS = {"name", "description"}
OPENAI_INTERFACE_KEYS = ("display_name", "short_description", "default_prompt")
ALLOWED_URI_SCHEMES = {"http", "https", "mailto", "data"}
EVAL_EXEMPT_SKILLS = {"hip0-mania"}
EVAL_REQUIRED_KEYS = ("id", "prompt", "expected_output", "should_trigger")


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

    for line_no, raw_line in enumerate(lines[1:end], start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if current_block_key and raw_line.startswith((" ", "\t")):
            current_block.append(raw_line.strip())
            continue

        flush_block()
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if not match:
            raise ValueError(f"line {line_no}: invalid frontmatter line")

        key, value = match.group(1), match.group(2).strip()
        if key not in FRONTMATTER_KEYS:
            allowed = ", ".join(sorted(FRONTMATTER_KEYS))
            raise ValueError(f"line {line_no}: unsupported frontmatter key {key!r}; allowed keys: {allowed}")
        if key in data:
            raise ValueError(f"line {line_no}: duplicate frontmatter key {key!r}")

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


def strip_markdown_link_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    return target


def split_local_link_target(target: str) -> str:
    return strip_markdown_link_target(target).split("#", 1)[0]


def uri_scheme(target: str) -> str | None:
    match = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", target)
    return match.group(1).lower() if match else None


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_links(skill_dir: Path, file_path: Path, lines: list[str]) -> list[str]:
    errors: list[str] = []
    skill_root = skill_dir.resolve()
    base_dir = file_path.parent.resolve()
    relative_file = file_path.relative_to(skill_dir).as_posix()

    for line_no, line in enumerate(lines, start=1):
        for target in LINK_RE.findall(line):
            clean_target = split_local_link_target(target)
            stripped_target = strip_markdown_link_target(target)

            if stripped_target.startswith("#") or not clean_target:
                continue

            scheme = uri_scheme(stripped_target)
            if scheme:
                if scheme not in ALLOWED_URI_SCHEMES:
                    errors.append(
                        f"{relative_file} line {line_no}: unsupported link scheme {scheme!r}"
                    )
                continue

            if clean_target.startswith(("/", "~")):
                errors.append(
                    f"{relative_file} line {line_no}: nonportable absolute link {target!r}"
                )
                continue

            resolved = (base_dir / clean_target).resolve()
            if not path_is_within(resolved, skill_root):
                errors.append(
                    f"{relative_file} line {line_no}: relative link escapes skill directory {target!r}"
                )
                continue

            if not resolved.exists():
                errors.append(
                    f"{relative_file} line {line_no}: broken relative link {target!r}"
                )
    return errors


def validate_reference_routing(skill_dir: Path, skill_lines: list[str]) -> list[str]:
    errors: list[str] = []
    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        return errors

    linked_references: set[str] = set()
    skill_root = skill_dir.resolve()
    for target in LINK_RE.findall("\n".join(skill_lines)):
        clean_target = split_local_link_target(target)
        if not clean_target or uri_scheme(strip_markdown_link_target(target)):
            continue
        if clean_target.startswith(("/", "~")):
            continue
        resolved = (skill_dir / clean_target).resolve()
        if path_is_within(resolved, skill_root) and resolved.is_file():
            relative_path = resolved.relative_to(skill_root).as_posix()
            if relative_path.startswith("references/"):
                linked_references.add(relative_path)

    for reference_file in sorted(path for path in references_dir.rglob("*") if path.is_file()):
        relative_path = reference_file.relative_to(skill_dir).as_posix()
        if relative_path not in linked_references:
            errors.append(f"reference {relative_path!r} is not linked from SKILL.md as a Markdown link")

    return errors


def strip_yaml_quotes(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def validate_openai_yaml(path: Path, skill_name: str) -> list[str]:
    errors: list[str] = []
    interface: dict[str, str] = {}
    current_section: str | None = None
    seen_sections: set[str] = set()

    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if not raw_line.startswith((" ", "\t")):
            if not raw_line.endswith(":"):
                errors.append(f"line {line_no}: expected top-level section")
                continue
            current_section = raw_line[:-1].strip()
            if current_section in seen_sections:
                errors.append(f"line {line_no}: duplicate top-level key {current_section!r}")
            seen_sections.add(current_section)
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
        if key not in OPENAI_INTERFACE_KEYS:
            errors.append(f"line {line_no}: unsupported interface key {key!r}")
            continue
        if key in interface:
            errors.append(f"line {line_no}: duplicate interface key {key!r}")
            continue
        interface[key] = value

    for key in OPENAI_INTERFACE_KEYS:
        if not interface.get(key):
            errors.append(f"interface.{key} is required")

    short_description = interface.get("short_description", "")
    if short_description and not 25 <= len(short_description) <= 64:
        errors.append("interface.short_description must be 25-64 characters")

    default_prompt = interface.get("default_prompt", "")
    if default_prompt and f"${skill_name}" not in default_prompt:
        errors.append(f"interface.default_prompt must include ${skill_name}")

    return errors


def validate_agents_metadata(skill_dir: Path) -> list[str]:
    metadata_file = skill_dir / "agents" / "openai.yaml"
    if not metadata_file.exists():
        return []

    errors = validate_openai_yaml(metadata_file, skill_dir.name)
    return [f"agents/openai.yaml: {error}" for error in errors]


def validate_skill_evals(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    evals_file = skill_dir / "evals" / "evals.json"

    if skill_dir.name in EVAL_EXEMPT_SKILLS:
        return errors

    if not evals_file.is_file():
        return ["evals/evals.json is required for production skills"]

    data, load_errors = load_json_object(evals_file)
    if data is None:
        return [f"evals/evals.json: {error}" for error in load_errors]

    skill_name = data.get("skill_name")
    if skill_name != skill_dir.name:
        errors.append("evals/evals.json: skill_name must match skill directory")

    evals = data.get("evals")
    if not isinstance(evals, list) or len(evals) < 3:
        errors.append("evals/evals.json: evals must contain at least 3 cases")
        return errors

    seen_ids: set[str] = set()
    should_trigger_count = 0
    should_not_trigger_count = 0
    for index, item in enumerate(evals):
        prefix = f"evals/evals.json: evals[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue

        for key in EVAL_REQUIRED_KEYS:
            if key not in item:
                errors.append(f"{prefix}.{key} is required")

        eval_id = item.get("id")
        if not isinstance(eval_id, str) or not eval_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif eval_id in seen_ids:
            errors.append(f"{prefix}.id {eval_id!r} is duplicated")
        else:
            seen_ids.add(eval_id)

        for key in ("prompt", "expected_output"):
            value = item.get(key)
            if not isinstance(value, str) or len(value.strip()) < 20:
                errors.append(f"{prefix}.{key} must be a descriptive string")

        should_trigger = item.get("should_trigger")
        if not isinstance(should_trigger, bool):
            errors.append(f"{prefix}.should_trigger must be boolean")
        elif should_trigger:
            should_trigger_count += 1
        else:
            should_not_trigger_count += 1

        tags = item.get("tags")
        if tags is not None:
            if not isinstance(tags, list) or not tags:
                errors.append(f"{prefix}.tags must be a non-empty list when present")
            elif not all(isinstance(tag, str) and tag.strip() for tag in tags):
                errors.append(f"{prefix}.tags must contain only non-empty strings")

    if should_trigger_count < 2:
        errors.append("evals/evals.json: include at least 2 should_trigger=true cases")
    if should_not_trigger_count < 1:
        errors.append("evals/evals.json: include at least 1 should_trigger=false near-miss case")

    return errors


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

    errors.extend(validate_links(skill_dir, skill_file, lines))

    for markdown_file in sorted(skill_dir.rglob("*.md")):
        if markdown_file == skill_file:
            continue
        markdown_lines = markdown_file.read_text(encoding="utf-8").splitlines()
        errors.extend(validate_links(skill_dir, markdown_file, markdown_lines))

    errors.extend(validate_reference_routing(skill_dir, lines))
    errors.extend(validate_agents_metadata(skill_dir))
    errors.extend(validate_skill_evals(skill_dir))
    return errors


def require_string(data: dict[str, object], key: str, path: Path) -> list[str]:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        return [f"{path}: {key} is required"]
    return []


def require_string_list(data: dict[str, object], key: str, path: Path) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        return [f"{path}: {key} must be a non-empty list"]
    if not all(isinstance(item, str) and item.strip() for item in value):
        return [f"{path}: {key} must contain only non-empty strings"]
    return []


def require_semver(data: dict[str, object], key: str, path: Path) -> list[str]:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        return [f"{path}: {key} is required"]
    if not SEMVER_RE.match(value):
        return [f"{path}: {key} must be semver"]
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


def validate_repo_relative_path(
    repo_root: Path, base_dir: Path, path: Path, value: object, label: str
) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{path}: {label} is required"]
    if value.startswith(("/", "~")):
        return [f"{path}: {label} must be repo-relative"]

    resolved = (base_dir / value).resolve()
    repo_root_resolved = repo_root.resolve()
    if not path_is_within(resolved, repo_root_resolved):
        return [f"{path}: {label} must not escape repository"]
    if not resolved.exists():
        return [f"{path}: {label} {value!r} does not exist"]
    return []


def validate_codex_plugin_manifest(repo_root: Path) -> list[str]:
    path = repo_root / "plugins" / "skill-mania" / ".codex-plugin" / "plugin.json"
    data, errors = load_json_object(path)
    if data is None:
        return errors

    for key in ("name", "description", "skills"):
        errors.extend(require_string(data, key, path))
    errors.extend(require_semver(data, "version", path))
    errors.extend(require_string_list(data, "keywords", path))

    interface, interface_errors = require_object(data, "interface", path)
    errors.extend(interface_errors)
    if interface is not None:
        for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            errors.extend(require_string(interface, key, path))
        errors.extend(require_string_list(interface, "capabilities", path))
        errors.extend(require_string_list(interface, "defaultPrompt", path))

    skills_path = data.get("skills")
    plugin_root = path.parent.parent
    errors.extend(validate_repo_relative_path(repo_root, plugin_root, path, skills_path, "skills"))

    return errors


def validate_claude_plugin_manifest(repo_root: Path) -> list[str]:
    path = repo_root / "plugins" / "skill-mania" / ".claude-plugin" / "plugin.json"
    data, errors = load_json_object(path)
    if data is None:
        return errors

    for key in ("name", "description"):
        errors.extend(require_string(data, key, path))
    errors.extend(require_semver(data, "version", path))

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
            source_path = source.get("path")
            if isinstance(source_path, str) and source.get("source") == "local":
                errors.extend(
                    validate_repo_relative_path(
                        repo_root,
                        path.parent.parent.parent,
                        path,
                        source_path,
                        f"plugins[{index}].source.path",
                    )
                )
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
        source_path = plugin.get("source")
        errors.extend(
            validate_repo_relative_path(
                repo_root,
                path.parent.parent,
                path,
                source_path,
                f"plugins[{index}].source",
            )
        )
        if "tags" in plugin:
            errors.extend(require_string_list(plugin, "tags", path))

    return errors


def readme_skill_names(repo_root: Path) -> set[str]:
    path = repo_root / "README.md"
    if not path.is_file():
        return set()

    names: set[str] = set()
    in_section = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "## Included Skills":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            match = re.match(r"^- `([^`]+)`\s+-", line)
            if match:
                names.add(match.group(1))
    return names


def validate_readme_references(repo_root: Path) -> list[str]:
    path = repo_root / "README.md"
    if not path.is_file():
        return [f"{path}: file is required"]

    body = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "github.com/openai/skills" in body:
        errors.append(f"{path}: replace deprecated openai/skills links with current Codex plugin docs")
    for required_url in (
        "https://developers.openai.com/codex/skills",
        "https://developers.openai.com/codex/plugins/build",
        "https://github.com/openai/plugins",
    ):
        if required_url not in body:
            errors.append(f"{path}: missing current reference {required_url}")
    return errors


def validate_readme_skill_list(repo_root: Path) -> list[str]:
    errors: list[str] = []
    canonical_names = {path.name for path in iter_skill_dirs(repo_root / "skills")}
    listed_names = readme_skill_names(repo_root)

    if not listed_names:
        return [f"{repo_root / 'README.md'}: Included Skills list is missing or empty"]

    missing = sorted(canonical_names - listed_names)
    extra = sorted(listed_names - canonical_names)
    if missing:
        errors.append(f"{repo_root / 'README.md'}: missing skills in Included Skills: {', '.join(missing)}")
    if extra:
        errors.append(f"{repo_root / 'README.md'}: unknown skills in Included Skills: {', '.join(extra)}")
    return errors


def validate_plugin_versions_match(repo_root: Path) -> list[str]:
    codex_path = repo_root / "plugins" / "skill-mania" / ".codex-plugin" / "plugin.json"
    claude_path = repo_root / "plugins" / "skill-mania" / ".claude-plugin" / "plugin.json"
    codex_data, codex_errors = load_json_object(codex_path)
    claude_data, claude_errors = load_json_object(claude_path)
    if codex_data is None or claude_data is None:
        return codex_errors + claude_errors

    if codex_data.get("version") != claude_data.get("version"):
        return [
            f"{codex_path} and {claude_path}: plugin versions must match for a release"
        ]
    return []


def validate_repo_metadata(repo_root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_codex_plugin_manifest(repo_root))
    errors.extend(validate_claude_plugin_manifest(repo_root))
    errors.extend(validate_codex_marketplace(repo_root))
    errors.extend(validate_claude_marketplace(repo_root))
    errors.extend(validate_readme_skill_list(repo_root))
    errors.extend(validate_readme_references(repo_root))
    errors.extend(validate_plugin_versions_match(repo_root))
    return errors


def validate_skill_root(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.exists():
        return [f"{root}: skills root does not exist"]

    for child in sorted(root.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir() and not (child / "SKILL.md").is_file():
            errors.append(f"{root}: unexpected directory without SKILL.md: {child.name}")

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
        root_errors = validate_skill_root(root)
        if root_errors:
            failed = True
            for error in root_errors:
                print(error)

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
