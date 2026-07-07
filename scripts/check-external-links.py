#!/usr/bin/env python3
"""Check external HTTP links in repository Markdown files."""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import shutil
import subprocess
import sys
from pathlib import Path


URL_RE = re.compile(r"https?://[^\s<>()`\"]+")
TRAILING_PUNCTUATION = ".,;:!?]}"
SKIP_HOSTS = {"localhost", "127.0.0.1"}


def collect_links(root: Path) -> dict[str, list[str]]:
    links: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", "node_modules", "plugins"} for part in path.parts):
            continue
        in_fence = False
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line = re.sub(r"`[^`]*`", "", line)
            for raw_url in URL_RE.findall(line):
                url = raw_url.rstrip(TRAILING_PUNCTUATION)
                if any(f"//{host}" in url for host in SKIP_HOSTS):
                    continue
                links.setdefault(url, []).append(path.as_posix())
    return links


def check_link(url: str, timeout: float) -> tuple[str, int | None, str | None]:
    curl = shutil.which("curl")
    if not curl:
        return url, None, "curl is required for bounded external link checks"
    try:
        result = subprocess.run(
            [
                curl,
                "--location",
                "--silent",
                "--show-error",
                "--output",
                "/dev/null",
                "--write-out",
                "%{http_code}",
                "--connect-timeout",
                str(min(timeout, 5.0)),
                "--max-time",
                str(timeout),
                "--user-agent",
                "skill-mania-link-check/1.0",
                url,
            ],
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout + 2,
        )
    except subprocess.TimeoutExpired:
        return url, None, f"request exceeded {timeout} seconds"
    try:
        status = int(result.stdout[-3:])
    except ValueError:
        status = None
    error = result.stderr.strip() or None
    return url, status, error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--list", action="store_true", help="list links without network access")
    args = parser.parse_args()

    links = collect_links(args.root.resolve())
    if args.list:
        print("\n".join(sorted(links)))
        return 0

    failed = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = executor.map(lambda url: check_link(url, args.timeout), sorted(links))
        for url, status, error in results:
            if status is not None and 200 <= status < 400:
                print(f"ok {status} {url}")
                continue
            failed = True
            locations = ", ".join(links[url])
            print(f"broken {status or '-'} {url} ({locations}): {error}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
