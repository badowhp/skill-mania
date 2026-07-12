#!/usr/bin/env python3
"""Inspect cache and routing headers for one explicit HTTP URL."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
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

SENSITIVE_HEADERS = frozenset(("set-cookie",))


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Return redirect responses so the caller chooses every network target."""

    def redirect_request(self, request, response, code, message, headers, new_url):  # type: ignore[no-untyped-def]
        return None


def validate_http_url(url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("URL scheme must be http or https")
    if not parsed.hostname:
        raise ValueError("URL must include a host")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URL credentials are not allowed")


def redact_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = "redacted" if parsed.query else ""
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, ""))


def open_url(request: urllib.request.Request, timeout: float):  # type: ignore[no-untyped-def]
    opener = urllib.request.build_opener(NoRedirectHandler())
    try:
        return opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        return error


def inspect(url: str, method: str, timeout: float) -> dict[str, object]:
    validate_http_url(url)
    request = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "skill-mania-http-cache-inspector/1.0"},
    )
    response = open_url(request, timeout)

    with response:
        headers: dict[str, str] = {}
        observed_headers: set[str] = set()
        for name, value in response.headers.items():
            normalized_name = name.lower()
            if normalized_name not in INTERESTING_HEADERS:
                continue
            observed_headers.add(normalized_name)
            if normalized_name in SENSITIVE_HEADERS:
                headers[normalized_name] = "<redacted>"
            elif normalized_name == "location":
                absolute = urllib.parse.urljoin(response.url, value)
                headers[normalized_name] = redact_url(absolute)
            else:
                headers[normalized_name] = value

        notes: list[str] = []
        cache_control = headers.get("cache-control", "").lower()
        if not cache_control:
            notes.append("no Cache-Control header observed")
        if "set-cookie" in observed_headers and "public" in cache_control:
            notes.append("public cache response also sets a cookie; review personalization boundaries")
        if headers.get("vary", "").strip() == "*":
            notes.append("Vary: * prevents shared-cache reuse")
        if 300 <= response.status < 400 and "location" not in headers:
            notes.append("redirect status has no Location header")
        elif 300 <= response.status < 400:
            notes.append("redirect not followed; inspect the redacted Location target explicitly")

        return {
            "requested_url": redact_url(url),
            "final_url": redact_url(response.url),
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
