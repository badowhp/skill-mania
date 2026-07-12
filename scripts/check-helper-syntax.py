#!/usr/bin/env python3
"""Check repository helper syntax without creating generated cache files."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


PYTHON_SUFFIXES = frozenset((".py",))
NODE_SUFFIXES = frozenset((".js", ".cjs", ".mjs"))
SHELL_SUFFIXES = frozenset((".sh",))


def helper_files(root: Path) -> list[Path]:
    candidates = list((root / "scripts").glob("*"))
    candidates.extend((root / "skills").glob("*/scripts/*"))
    return sorted(
        path
        for path in candidates
        if path.is_file()
        and path.suffix in PYTHON_SUFFIXES | NODE_SUFFIXES | SHELL_SUFFIXES
    )


def check(root: Path) -> list[str]:
    errors: list[str] = []
    node = shutil.which("node")
    bash = shutil.which("bash")

    for path in helper_files(root):
        relative = path.relative_to(root)
        if path.suffix in PYTHON_SUFFIXES:
            try:
                compile(path.read_text(encoding="utf-8"), str(relative), "exec")
            except (OSError, SyntaxError, UnicodeError) as exc:
                errors.append(f"{relative}: Python syntax error: {exc}")
        elif path.suffix in NODE_SUFFIXES:
            if node is None:
                errors.append(f"{relative}: node is required for syntax validation")
                continue
            result = subprocess.run(
                [node, "--check", str(path)], text=True, capture_output=True, check=False
            )
            if result.returncode:
                detail = (result.stderr or result.stdout).strip()
                errors.append(f"{relative}: Node syntax error: {detail}")
        elif path.suffix in SHELL_SUFFIXES:
            if bash is None:
                errors.append(f"{relative}: bash is required for syntax validation")
                continue
            result = subprocess.run(
                [bash, "-n", str(path)], text=True, capture_output=True, check=False
            )
            if result.returncode:
                detail = (result.stderr or result.stdout).strip()
                errors.append(f"{relative}: shell syntax error: {detail}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    root = args.root.resolve()
    files = helper_files(root)
    errors = check(root)
    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"helper syntax passed for {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
