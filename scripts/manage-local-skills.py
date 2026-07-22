#!/usr/bin/env python3
"""Install, inspect, uninstall, and clean up local Skill Mania skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_groups import available_skills, load_groups, resolve_groups, validate_groups


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "skills"
GROUPS_CONFIG = REPO_ROOT / "config" / "skill-groups.json"
PROFILES_CONFIG = REPO_ROOT / "config" / "install-profiles.json"
MANAGED_MARKER = ".skill-mania-managed.json"
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COPY_IGNORE = shutil.ignore_patterns(
    ".DS_Store",
    "__pycache__",
    "*.pyc",
    ".tmp",
    ".cache",
    "node_modules",
)


def usage_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage portable Skill Mania skills for Agent Skills clients and Claude Code."
    )
    target = parser.add_argument_group("targets")
    target.add_argument("--all", action="store_true", dest="all_targets", help="target agents and Claude Code")
    target.add_argument("--agents", "--codex", action="store_true", dest="agents", help="target the shared Agent Skills directory")
    target.add_argument("--claude", action="store_true", help="target the Claude Code skills directory")

    selection = parser.add_argument_group("selection")
    selection.add_argument("--group", action="append", default=[], help="select a named overlapping skill group; repeatable")
    selection.add_argument("--profile", action="append", default=[], help="select a legacy partition profile; repeatable")
    selection.add_argument("--skill", action="append", default=[], help="select one exact skill; repeatable")
    selection.add_argument("--all-skills", action="store_true", help="select every skill explicitly")
    selection.add_argument("--list-groups", action="store_true", help="print available groups and exit")

    action = parser.add_mutually_exclusive_group()
    action.add_argument("--install", action="store_const", const="install", dest="operation", help="install selected skills; default")
    action.add_argument("--uninstall", "--remove", action="store_const", const="uninstall", dest="operation", help="remove selected managed skills")
    action.add_argument("--cleanup", action="store_const", const="cleanup", dest="operation", help="find stale managed installs and broken repository links")
    action.add_argument("--list", action="store_const", const="list", dest="operation", help="list selected skills and installation state")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--link", action="store_const", const="link", dest="mode", help="symlink from this repository; default")
    mode.add_argument("--copy", action="store_const", const="copy", dest="mode", help="copy a self-contained snapshot")

    parser.add_argument("--force", action="store_true", help="replace an existing managed skill during install")
    parser.add_argument(
        "--force-unmanaged",
        action="store_true",
        help="allow explicit replacement or uninstall of an unmarked skill directory",
    )
    parser.add_argument("--yes", action="store_true", help="confirm removal or cleanup")
    parser.add_argument("--dry-run", action="store_true", help="show changes without modifying targets")
    parser.add_argument("--no-validate", action="store_true", help="skip canonical skill validation before install")
    parser.set_defaults(operation="install", mode="link")
    return parser


def path_contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def safe_target_root(label: str, value: str, *, create: bool) -> Path:
    candidate = Path(value).expanduser().absolute().resolve(strict=False)
    home = Path.home().resolve()
    repo = REPO_ROOT.resolve()
    source = SOURCE_ROOT.resolve()
    if candidate in {Path("/"), home, repo, source}:
        raise ValueError(f"refusing unsafe {label} target directory: {candidate}")
    if (
        path_contains(candidate, home)
        or path_contains(candidate, repo)
        or path_contains(repo, candidate)
    ):
        raise ValueError(f"refusing broad {label} target directory: {candidate}")
    if create:
        candidate.mkdir(parents=True, exist_ok=True)
        candidate = candidate.resolve()
    return candidate


def default_agent_dir() -> Path:
    explicit = os.environ.get("AGENT_SKILLS_DIR") or os.environ.get("CODEX_SKILLS_DIR")
    if explicit:
        return Path(explicit)
    shared = Path.home() / ".agents" / "skills"
    legacy = Path.home() / ".codex" / "skills"
    if contains_skills(shared):
        return shared
    if contains_skills(legacy):
        return legacy
    if shared.is_dir():
        return shared
    if legacy.is_dir():
        return legacy
    return shared


def contains_skills(root: Path) -> bool:
    try:
        return any(
            child.is_dir() and (child / "SKILL.md").is_file()
            for child in root.iterdir()
        )
    except OSError:
        return False


def target_roots(args: argparse.Namespace, *, create: bool) -> list[tuple[str, Path]]:
    agents = args.agents or args.all_targets
    claude = args.claude or args.all_targets
    if not agents and not claude:
        agents = True
        claude = True
    roots: list[tuple[str, Path]] = []
    if agents:
        roots.append(("agents", safe_target_root("agents", str(default_agent_dir()), create=create)))
    if claude:
        claude_dir = os.environ.get("CLAUDE_SKILLS_DIR", str(Path.home() / ".claude" / "skills"))
        roots.append(("claude", safe_target_root("claude", claude_dir, create=create)))
    return roots


def load_profiles() -> dict[str, list[str]]:
    data = json.loads(PROFILES_CONFIG.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("install profiles must be an object")
    profiles: dict[str, list[str]] = {}
    for name, values in data.items():
        if not isinstance(name, str) or not isinstance(values, list):
            raise ValueError("install profiles contain an invalid entry")
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError(f"profile {name!r} contains an invalid skill")
        profiles[name] = values
    return profiles


def selected_skills(args: argparse.Namespace) -> list[str]:
    known = available_skills(SOURCE_ROOT)
    groups = load_groups(GROUPS_CONFIG)
    group_errors = validate_groups(groups, SOURCE_ROOT)
    if group_errors:
        raise ValueError("; ".join(group_errors))
    profiles = load_profiles()

    unknown_profiles = sorted(set(args.profile) - set(profiles))
    if unknown_profiles:
        raise ValueError(f"unknown profiles: {', '.join(unknown_profiles)}")
    unknown_skills = sorted(set(args.skill) - known)
    if unknown_skills:
        raise ValueError(f"unknown skills: {', '.join(unknown_skills)}")

    chosen: list[str] = []
    for profile in args.profile:
        chosen.extend(profiles[profile])
    chosen.extend(resolve_groups(groups, args.group))
    chosen.extend(args.skill)
    if args.all_skills:
        chosen.extend(sorted(known))

    has_selector = bool(args.profile or args.group or args.skill or args.all_skills)
    if not has_selector:
        if args.operation == "uninstall":
            raise ValueError("uninstall requires --group, --profile, --skill, or --all-skills")
        chosen.extend(sorted(known))
    return list(dict.fromkeys(chosen))


def print_groups() -> None:
    groups = load_groups(GROUPS_CONFIG)
    errors = validate_groups(groups, SOURCE_ROOT)
    if errors:
        raise ValueError("; ".join(errors))
    for group in groups:
        aliases = f" aliases={','.join(group.aliases)}" if group.aliases else ""
        print(f"{group.id} ({len(group.skills)} skills){aliases}\n  {group.description}")


def validate_source() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate-skills.py"), str(SOURCE_ROOT)],
        cwd=REPO_ROOT,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("canonical skill validation failed")


def version_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"invalid semantic version: {version}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def assert_claude_link_support() -> None:
    claude = shutil.which("claude")
    if claude is None:
        return
    result = subprocess.run([claude, "--version"], text=True, capture_output=True, check=False)
    match = re.search(r"(\d+\.\d+\.\d+)", result.stdout + result.stderr)
    if match and version_tuple(match.group(1)) < version_tuple("2.1.203"):
        raise RuntimeError(
            f"Claude Code {match.group(1)} does not support symlinked skills; "
            "upgrade to 2.1.203 or newer, or rerun with --copy"
        )


def marker_data(destination: Path) -> dict[str, object] | None:
    marker = destination / MANAGED_MARKER
    if not destination.is_dir() or not marker.is_file():
        return None
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def repo_link(destination: Path, skill: str) -> bool:
    if not destination.is_symlink():
        return False
    link = Path(os.readlink(destination))
    resolved = (destination.parent / link).resolve(strict=False) if not link.is_absolute() else link.resolve(strict=False)
    return resolved == (SOURCE_ROOT / skill).resolve(strict=False)


def installed_state(destination: Path, skill: str) -> str:
    if repo_link(destination, skill):
        return "managed-link"
    marker = marker_data(destination)
    if marker and marker.get("skill") == skill and marker.get("manager") == "skill-mania":
        return "managed-copy"
    if destination.exists() or destination.is_symlink():
        return "unmanaged"
    return "absent"


def remove_destination(destination: Path) -> None:
    if destination.is_symlink():
        destination.unlink()
    elif destination.is_dir():
        shutil.rmtree(destination)
    else:
        destination.unlink()


def reserved_path(root: Path, label: str) -> Path:
    reserved = Path(tempfile.mkdtemp(prefix=f".skill-mania-{label}-", dir=root))
    reserved.rmdir()
    return reserved


def stage_install(root: Path, source: Path, skill: str, mode: str) -> Path:
    staged = reserved_path(root, skill)
    try:
        if mode == "link":
            staged.symlink_to(source, target_is_directory=True)
        else:
            shutil.copytree(source, staged, ignore=COPY_IGNORE)
            (staged / MANAGED_MARKER).write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "manager": "skill-mania",
                        "skill": skill,
                        "mode": "copy",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        return staged
    except Exception:
        if staged.exists() or staged.is_symlink():
            remove_destination(staged)
        raise


def install_one(label: str, root: Path, skill: str, args: argparse.Namespace) -> bool:
    source = SOURCE_ROOT / skill
    destination = root / skill
    state = installed_state(destination, skill)
    if state != "absent" and not args.force:
        print(f"skip {label}:{skill} - {destination} already exists; use --force to replace")
        return True
    if state == "unmanaged" and not args.force_unmanaged:
        print(
            f"refuse {label}:{skill} - unmanaged; use --force and --force-unmanaged "
            "to replace this explicit skill",
            file=sys.stderr,
        )
        return False
    if state == "unmanaged" and not (
        destination.is_dir() and (destination / "SKILL.md").is_file()
    ):
        raise ValueError(f"refusing to replace non-skill path: {destination}")
    if args.dry_run:
        verb = "replace" if state != "absent" else "install"
        print(f"would {verb} {label}:{skill} as {args.mode} -> {destination}")
        return True

    staged = stage_install(root, source, skill, args.mode)
    backup: Path | None = None
    try:
        if state != "absent":
            backup = reserved_path(root, f"{skill}-backup")
            destination.rename(backup)
        try:
            staged.rename(destination)
        except OSError as activation_error:
            if backup is not None:
                try:
                    backup.rename(destination)
                except OSError as restore_error:
                    raise RuntimeError(
                        f"could not activate {destination}: {activation_error}; "
                        f"restore also failed: {restore_error}"
                    ) from restore_error
            raise
        if backup is not None:
            remove_destination(backup)
            backup = None
    finally:
        if staged.exists() or staged.is_symlink():
            remove_destination(staged)
    print(f"installed {label}:{skill} -> {destination}")
    return True


def uninstall_one(label: str, root: Path, skill: str, args: argparse.Namespace) -> bool:
    destination = root / skill
    state = installed_state(destination, skill)
    if state == "absent":
        print(f"skip {label}:{skill} - not installed")
        return True
    if state == "unmanaged" and not args.force_unmanaged:
        print(f"refuse {label}:{skill} - unmanaged; use --force-unmanaged for this explicit skill", file=sys.stderr)
        return False
    if args.dry_run or not args.yes:
        print(f"would remove {label}:{skill} ({state}) -> {destination}")
        return True
    remove_destination(destination)
    print(f"removed {label}:{skill} ({state}) -> {destination}")
    return True


def cleanup_candidates(root: Path) -> list[tuple[Path, str]]:
    if not root.is_dir():
        return []
    known = available_skills(SOURCE_ROOT)
    candidates: list[tuple[Path, str]] = []
    source_root = SOURCE_ROOT.resolve()
    for destination in sorted(root.iterdir()):
        skill = destination.name
        if destination.is_symlink():
            link = Path(os.readlink(destination))
            resolved = (destination.parent / link).resolve(strict=False) if not link.is_absolute() else link.resolve(strict=False)
            if resolved.parent == source_root and (skill not in known or not resolved.exists()):
                candidates.append((destination, "stale repository link"))
            continue
        marker = marker_data(destination)
        if marker and marker.get("manager") == "skill-mania" and skill not in known:
            candidates.append((destination, "managed copy missing from catalog"))
    return candidates


def run_cleanup(roots: list[tuple[str, Path]], args: argparse.Namespace) -> int:
    found = 0
    for label, root in roots:
        for destination, reason in cleanup_candidates(root):
            found += 1
            if args.yes and not args.dry_run:
                remove_destination(destination)
                print(f"cleaned {label}:{destination.name} - {reason}")
            else:
                print(f"would clean {label}:{destination.name} - {reason}")
    if found == 0:
        print("no stale managed skills found")
    elif not args.yes and not args.dry_run:
        print("cleanup preview only; rerun with --yes to apply")
    return 0


def list_state(roots: list[tuple[str, Path]], skills: list[str]) -> None:
    labels = [label for label, _ in roots]
    print("skill\t" + "\t".join(labels))
    for skill in skills:
        states = [installed_state(root / skill, skill) for _, root in roots]
        print(skill + "\t" + "\t".join(states))


def main(argv: list[str] | None = None) -> int:
    parser = usage_parser()
    args = parser.parse_args(argv)
    try:
        if args.list_groups:
            print_groups()
            return 0

        create_targets = args.operation == "install" and not args.dry_run
        roots = target_roots(args, create=create_targets)
        if args.operation == "cleanup":
            return run_cleanup(roots, args)

        skills = selected_skills(args)
        if args.operation == "list":
            list_state(roots, skills)
            return 0

        if args.operation == "install" and not args.no_validate:
            validate_source()
        if args.operation == "install" and args.mode == "link" and any(
            label == "claude" for label, _ in roots
        ):
            assert_claude_link_support()

        if args.operation == "uninstall" and not args.yes and not args.dry_run:
            print("removal preview only; rerun with --yes to apply", file=sys.stderr)

        success = True
        for label, root in roots:
            for skill in skills:
                if args.operation == "install":
                    success = install_one(label, root, skill, args) and success
                else:
                    success = uninstall_one(label, root, skill, args) and success
        return 0 if success else 1
    except RuntimeError as exc:
        print(f"skill manager error: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"skill manager error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
