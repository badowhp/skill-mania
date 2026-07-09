#!/usr/bin/env python3
"""Inspect cache and routing headers for one explicit HTTP URL."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


INTERESTING_HEADERS = (
    "age",
    "cache-control",
    "cdn-cache-status",
    "cf-cache-status",
    "etag",
    "last-modified",
    "location",
    "server-timing",
    "set-cookie",
    "vary",
    "x-cache",
)


def inspect(url: str, method: str, timeout: float) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "skill-mania-http-cache-inspector/1.0"},
    )
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        response = error

    with response:
        headers = {
            name.lower(): value
            for name, value in response.headers.items()
            if name.lower() in INTERESTING_HEADERS
        }
        notes: list[str] = []
        cache_control = headers.get("cache-control", "").lower()
        if not cache_control:
            notes.append("no Cache-Control header observed")
        if "set-cookie" in headers and "public" in cache_control:
            notes.append("public cache response also sets a cookie; review personalization boundaries")
        if headers.get("vary", "").strip() == "*":
            notes.append("Vary: * prevents shared-cache reuse")
        if 300 <= response.status < 400 and "location" not in headers:
            notes.append("redirect status has no Location header")

        return {
            "requested_url": url,
            "final_url": response.url,
            "method": method,
            "status": response.status,
            "headers": headers,
            "notes": notes,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--method", choices=("GET", "HEAD"), default="GET")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    try:
        report = inspect(args.url, args.method, args.timeout)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"HTTP cache inspection failed: {error}")
        return 1

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
