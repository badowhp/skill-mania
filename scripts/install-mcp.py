#!/usr/bin/env python3
"""Register one curated MCP server with Codex or Claude Code."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "mcp-servers.json"
ENV_REFERENCE_RE = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]*")
SERVER_NAME_RE = re.compile(r"[a-z][a-z0-9-]*")


class InstallerError(ValueError):
    """Raised when an MCP definition cannot be installed safely."""


def load_servers(path: Path = DEFAULT_CONFIG) -> dict[str, dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallerError(f"could not read MCP config {path}: {exc}") from exc

    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        raise InstallerError("MCP config must contain a non-empty mcpServers object")

    for name, server in servers.items():
        if not isinstance(name, str) or SERVER_NAME_RE.fullmatch(name) is None:
            raise InstallerError(f"invalid MCP server name: {name!r}")
        if not isinstance(server, dict):
            raise InstallerError(f"MCP server {name!r} must be an object")

        has_url = isinstance(server.get("url"), str) and bool(server["url"])
        has_command = isinstance(server.get("command"), str) and bool(server["command"])
        if has_url == has_command:
            raise InstallerError(
                f"MCP server {name!r} must define exactly one of url or command"
            )

        args = server.get("args", [])
        env = server.get("env", {})
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            raise InstallerError(f"MCP server {name!r} args must be strings")
        if not isinstance(env, dict) or not all(
            isinstance(key, str)
            and ENV_NAME_RE.fullmatch(key)
            and isinstance(value, str)
            for key, value in env.items()
        ):
            raise InstallerError(
                f"MCP server {name!r} env must map uppercase names to strings"
            )

    return servers


def server_values(server: dict[str, Any]) -> list[str]:
    values = [str(server.get("command", "")), *server.get("args", [])]
    values.extend(server.get("env", {}).values())
    return values


def environment_references(server: dict[str, Any]) -> list[str]:
    return sorted(
        {
            match.group(1)
            for value in server_values(server)
            for match in ENV_REFERENCE_RE.finditer(value)
        }
    )


def shell_value(value: str) -> str:
    """Quote a value while preserving only ${UPPER_CASE} runtime expansion."""

    pieces: list[str] = []
    offset = 0
    for match in ENV_REFERENCE_RE.finditer(value):
        if match.start() > offset:
            pieces.append(shlex.quote(value[offset : match.start()]))
        pieces.append(f'"${{{match.group(1)}}}"')
        offset = match.end()
    if offset < len(value):
        pieces.append(shlex.quote(value[offset:]))
    return "".join(pieces) or "''"


def stdio_definition(server: dict[str, Any]) -> tuple[str, list[str], dict[str, str]]:
    command = server["command"]
    args = list(server.get("args", []))
    env = dict(server.get("env", {}))
    references = environment_references(server)
    if not references:
        return command, args, env

    checks = [
        f': "${{{name}:?{name} must be exported before starting the MCP client}}"'
        for name in references
    ]
    assignments = [f"{key}={shell_value(value)}" for key, value in env.items()]
    invocation = [shell_value(command), *(shell_value(arg) for arg in args)]
    script = "; ".join(checks)
    script += "; exec env " + " ".join([*assignments, *invocation])
    return "/bin/sh", ["-c", script], {}


def registration_command(
    client: str, name: str, server: dict[str, Any], scope: str
) -> list[str]:
    if "url" in server:
        if client == "codex":
            return ["codex", "mcp", "add", "--url", server["url"], name]
        return [
            "claude",
            "mcp",
            "add",
            "--scope",
            scope,
            "--transport",
            "http",
            name,
            server["url"],
        ]

    command, args, env = stdio_definition(server)
    if client == "codex":
        result = ["codex", "mcp", "add"]
        for key, value in env.items():
            result.extend(["--env", f"{key}={value}"])
        return [*result, name, "--", command, *args]

    result = [
        "claude",
        "mcp",
        "add",
        "--scope",
        scope,
        "--transport",
        "stdio",
        name,
    ]
    for key, value in env.items():
        result.extend(["--env", f"{key}={value}"])
    return [*result, "--", command, *args]


def prerequisite_hint(command: str) -> str:
    if command == "uvx":
        return "install uv first (macOS: brew install uv; other systems: https://docs.astral.sh/uv/getting-started/installation/)"
    if command in {"node", "npx"}:
        return "install a current Node.js release first"
    if command in {"codex", "claude"}:
        return f"install or update {command} before using this target"
    return f"install {command!r} and ensure it is on PATH"


def check_prerequisites(client: str, name: str, server: dict[str, Any]) -> None:
    required_commands = [client]
    if "command" in server:
        required_commands.append(server["command"])
    for command in required_commands:
        if shutil.which(command) is None:
            raise InstallerError(
                f"missing prerequisite {command!r}: {prerequisite_hint(command)}"
            )

    missing_env = [
        variable
        for variable in environment_references(server)
        if not os.environ.get(variable)
    ]
    if missing_env:
        raise InstallerError(
            "export required environment variables before installing: "
            + ", ".join(missing_env)
        )

    if name == "godot":
        server_path = Path(os.environ["GODOT_MCP_PATH"]).expanduser()
        entrypoint = server_path / "build" / "index.js"
        if not entrypoint.is_file():
            raise InstallerError(
                f"Godot MCP entrypoint not found at {entrypoint}; build Coding-Solo/godot-mcp first"
            )
        binary = Path(os.environ["GODOT_BINARY_PATH"]).expanduser()
        if not binary.is_file():
            raise InstallerError(f"Godot binary not found at {binary}")


def post_install_notes(name: str) -> list[str]:
    if name != "blender":
        return []
    return [
        "Blender also needs the matching addon.py from https://github.com/ahujasid/blender-mcp.",
        "In Blender: Edit > Preferences > Add-ons > Install, enable Blender MCP, then use N > BlenderMCP > Connect.",
        "Save the .blend file before agent-driven work: this server can execute arbitrary Blender Python.",
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("server", nargs="?", help="one server name from --list")
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--codex",
        dest="client",
        action="store_const",
        const="codex",
        help="install for Codex (default)",
    )
    target.add_argument(
        "--claude",
        dest="client",
        action="store_const",
        const="claude",
        help="install for Claude Code",
    )
    parser.set_defaults(client="codex")
    parser.add_argument(
        "--scope",
        choices=("local", "user", "project"),
        default="user",
        help="Claude Code scope; ignored for Codex (default: user)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the exact registration command without running it",
    )
    parser.add_argument("--list", action="store_true", help="list curated server names")
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG, help=argparse.SUPPRESS
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        servers = load_servers(args.config)
        if args.list:
            if args.server:
                raise InstallerError("--list does not accept a server name")
            print("\n".join(sorted(servers)))
            return 0
        if not args.server:
            raise InstallerError("choose one MCP server name or use --list")
        if args.server not in servers:
            choices = ", ".join(sorted(servers))
            raise InstallerError(
                f"unknown MCP server {args.server!r}; choose one of: {choices}"
            )

        server = servers[args.server]
        command = registration_command(args.client, args.server, server, args.scope)
        if args.dry_run:
            print(shlex.join(command))
            return 0

        check_prerequisites(args.client, args.server, server)
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
        print(f"registered MCP server {args.server!r} for {args.client}")
        for note in post_install_notes(args.server):
            print(f"next: {note}")
        return 0
    except InstallerError as exc:
        print(f"MCP install error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
