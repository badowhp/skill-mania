#!/usr/bin/env python3
"""Deny high-confidence destructive agent commands from pre-tool hook input."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from collections.abc import Iterable
from typing import Any


SHELLS = {"bash", "dash", "fish", "ksh", "sh", "zsh"}
SHELL_SEPARATORS = {"&", "&&", "(", ")", ";", "|", "||"}
COMMAND_KEYS = {"cmd", "command", "script", "shell_command"}
GIT_COMMANDS = {
    "branch",
    "checkout",
    "clean",
    "commit",
    "filter-branch",
    "filter-repo",
    "gc",
    "merge",
    "push",
    "rebase",
    "reflog",
    "reset",
    "restore",
    "stash",
    "tag",
}


def _command_values(value: Any, key: str | None = None) -> list[str]:
    """Return command-shaped strings without scanning arbitrary prompt text."""
    if isinstance(value, str):
        return [value] if key in COMMAND_KEYS else []
    if isinstance(value, list):
        return [item for child in value for item in _command_values(child, key)]
    if isinstance(value, dict):
        return [
            item
            for child_key, child in value.items()
            for item in _command_values(child, str(child_key).lower())
        ]
    return []


def _extract_command(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, str):
        return tool_input
    if isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str):
        return tool_input["command"]
    tool_args = payload.get("toolArgs")
    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
        except json.JSONDecodeError:
            tool_args = {"command": tool_args}
    if isinstance(tool_args, dict) and isinstance(tool_args.get("command"), str):
        return tool_args["command"]
    commands = _command_values(payload)
    return "\n".join(commands)


def _shell_segments(command: str) -> Iterable[list[str]]:
    # A backslash-newline is one logical shell line. Treat other newlines as
    # boundaries so a destructive second command cannot hide behind the first.
    command = command.replace("\\\n", " ")
    for line in command.splitlines() or [command]:
        lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|()")
        lexer.commenters = ""
        lexer.whitespace_split = True
        tokens = list(lexer)
        segment: list[str] = []
        for token in tokens:
            if token in SHELL_SEPARATORS:
                if segment:
                    yield segment
                    segment = []
                continue
            segment.append(token)
        if segment:
            yield segment


def _basename(token: str) -> str:
    return os.path.basename(token).lower()


def _strip_wrappers(tokens: list[str]) -> list[str]:
    tokens = list(tokens)
    while tokens:
        while tokens and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[0]):
            tokens.pop(0)
        if not tokens:
            break
        command = _basename(tokens[0])
        if command in {"command", "exec", "nohup"}:
            tokens.pop(0)
            continue
        if command == "env":
            tokens.pop(0)
            while tokens and (tokens[0].startswith("-") or "=" in tokens[0]):
                tokens.pop(0)
            continue
        if command in {"doas", "sudo"}:
            tokens.pop(0)
            options_with_values = {"-C", "-g", "-h", "-p", "-T", "-u"}
            while tokens and tokens[0].startswith("-"):
                option = tokens.pop(0)
                if option in options_with_values and tokens:
                    tokens.pop(0)
            continue
        break
    return tokens


def _short_flag(args: list[str], flag: str) -> bool:
    return any(
        arg.startswith("-")
        and not arg.startswith("--")
        and flag in arg[1:]
        for arg in args
    )


def _git_reason(args: list[str]) -> str | None:
    verb_index = next(
        (index for index, token in enumerate(args) if token.lower() in GIT_COMMANDS),
        None,
    )
    if verb_index is None:
        return None
    verb = args[verb_index].lower()
    rest = args[verb_index + 1 :]
    lowered = [arg.lower() for arg in rest]

    if verb == "reset" and "--hard" in lowered:
        return "hard git reset"
    if verb == "clean":
        dry_run = "--dry-run" in lowered or _short_flag(rest, "n")
        forced = "--force" in lowered or _short_flag(rest, "f")
        if forced and not dry_run:
            return "forced git clean"
    if verb == "restore" and ("--staged" not in lowered or "--worktree" in lowered):
        return "git worktree restore"
    if verb == "checkout" and (
        "--" in rest or "--force" in lowered or _short_flag(rest, "f")
    ):
        return "destructive git checkout"
    if verb == "push" and (
        any(arg in {"--delete", "--force", "--force-with-lease", "--mirror"} for arg in lowered)
        or _short_flag(rest, "f")
        or any(arg.startswith(":") for arg in rest)
    ):
        return "forced or deleting git push"
    if verb == "branch" and (
        "-D" in rest or ("--delete" in lowered and "--force" in lowered)
    ):
        return "forced git branch deletion"
    if verb == "tag" and ("-d" in rest or "--delete" in lowered):
        return "git tag deletion"
    if verb == "stash" and any(arg in {"clear", "drop"} for arg in lowered):
        return "git stash deletion"
    if verb == "reflog" and any(arg in {"delete", "expire"} for arg in lowered):
        return "git reflog deletion"
    if verb == "gc" and any(arg == "--prune=now" for arg in lowered):
        return "immediate git object pruning"
    if verb in {"filter-branch", "filter-repo"}:
        return "git history rewrite"
    return None


def _classify(tokens: list[str], depth: int = 0) -> str | None:
    if depth > 3:
        return "nested shell command beyond guard parsing limit"
    tokens = _strip_wrappers(tokens)
    if not tokens:
        return None
    command = _basename(tokens[0])
    args = tokens[1:]
    lowered = [arg.lower() for arg in args]

    if command in SHELLS:
        command_flag_index = next(
            (
                index
                for index, arg in enumerate(args)
                if arg == "--command"
                or (arg.startswith("-") and not arg.startswith("--") and "c" in arg[1:])
            ),
            None,
        )
        if command_flag_index is not None and command_flag_index + 1 < len(args):
            return _classify_command(args[command_flag_index + 1], depth + 1)

    if command == "rm" and (
        "--recursive" in lowered or _short_flag(args, "r") or _short_flag(args, "R")
    ):
        return "recursive filesystem deletion"
    if command == "remove-item" and any(arg in {"-recurse", "-r"} for arg in lowered):
        return "recursive PowerShell deletion"
    if command == "find" and "-delete" in lowered:
        return "recursive find deletion"
    if command in {"find", "xargs"}:
        nested_index = next(
            (index for index, token in enumerate(args) if _basename(token) == "rm"),
            None,
        )
        if nested_index is not None:
            reason = _classify(args[nested_index:], depth + 1)
            if reason:
                return reason

    if command == "git":
        reason = _git_reason(args)
        if reason:
            return reason

    if command in {"mkfs", "newfs", "shred", "wipefs"}:
        return "filesystem or device destruction"
    if command == "dd" and any(arg.lower().startswith("of=/dev/") for arg in args):
        return "raw write to a device"
    if command == "diskutil" and any(
        arg.lower() in {"erasedisk", "erasevolume", "partitiondisk", "secureerase", "zerodisk"}
        for arg in args
    ):
        return "disk erase or repartition"
    if command in {"halt", "poweroff", "reboot", "shutdown"}:
        return "host shutdown or reboot"

    if command in {"terraform", "tofu"}:
        if "destroy" in lowered:
            return "infrastructure destruction"
        if "apply" in lowered and any(arg.startswith("-auto-approve") for arg in lowered):
            return "unattended infrastructure apply"
    if command == "kubectl" and (
        "delete" in lowered
        or "drain" in lowered
        or ("replace" in lowered and "--force" in lowered)
    ):
        return "destructive Kubernetes operation"
    if command == "helm" and any(arg in {"delete", "uninstall"} for arg in lowered):
        return "Helm release deletion"
    if command in {"docker", "podman"} and (
        "prune" in lowered
        or any(arg in {"rm", "rmi"} for arg in lowered[:2])
    ):
        return "container or image deletion"

    destructive_verbs = ("delete", "destroy", "purge", "remove", "terminate")
    if command in {"aws", "az", "doctl", "gcloud", "heroku"} and any(
        token == verb or token.startswith(f"{verb}-")
        for token in lowered
        for verb in destructive_verbs
    ):
        return "destructive cloud operation"
    if command == "gh" and (
        any(
            lowered[index : index + 2] in (["repo", "delete"], ["release", "delete"], ["pr", "merge"])
            for index in range(max(0, len(lowered) - 1))
        )
        or ("api" in lowered and "delete" in lowered)
    ):
        return "destructive GitHub operation"

    if command in {"npm", "pnpm", "yarn"} and "unpublish" in lowered:
        return "package removal from a registry"
    if command in {"cargo", "gem"} and "yank" in lowered:
        return "package version yanking"

    if command in {"mysql", "mariadb", "psql", "sqlite3", "sqlcmd"}:
        sql = " ".join(args)
        if re.search(r"\b(?:DROP\s+(?:DATABASE|SCHEMA|TABLE)|TRUNCATE\s+TABLE)\b", sql, re.IGNORECASE):
            return "destructive database statement"
    return None


def _classify_command(command: str, depth: int = 0) -> str | None:
    try:
        for segment in _shell_segments(command):
            reason = _classify(segment, depth)
            if reason:
                return reason
    except ValueError:
        return "unparseable shell command"
    return None


def _deny(payload: dict[str, Any], reason: str) -> int:
    message = f"Destructive command blocked: {reason}."
    if "toolArgs" in payload or ("toolName" in payload and "tool_input" not in payload):
        # GitHub Copilot CLI's camelCase preToolUse contract.
        output = {
            "permissionDecision": "deny",
            "permissionDecisionReason": message,
        }
    else:
        # Shared Claude Code and Codex PreToolUse contract.
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message,
            }
        }
    print(json.dumps(output, separators=(",", ":")))
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print("agent command guard: expected JSON hook input", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("agent command guard: expected a JSON object", file=sys.stderr)
        return 2

    tool_name = str(payload.get("tool_name", payload.get("toolName", ""))).lower()
    command = _extract_command(payload)
    if tool_name == "apply_patch" and "*** Delete File:" in command:
        reason = "file deletion through apply_patch"
    elif command:
        reason = _classify_command(command)
    elif tool_name in {"bash", "powershell"}:
        reason = "shell hook input without a command"
    else:
        reason = None

    if reason:
        return _deny(payload, reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
