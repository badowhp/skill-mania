#!/usr/bin/env python3
"""Extract basic SEO signals from local HTML files."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path


class SeoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.json_ld_count = 0
        self.headings: list[dict[str, str]] = []
        self._heading: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.meta.append(attr)
        elif tag == "link":
            self.links.append(attr)
        elif tag == "script" and attr.get("type", "").lower() == "application/ld+json":
            self.json_ld_count += 1
        elif tag in {"h1", "h2"}:
            self._heading = tag
            self._heading_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif self._heading == tag:
            text = " ".join("".join(self._heading_parts).split())
            if text:
                self.headings.append({"tag": tag, "text": text})
            self._heading = None
            self._heading_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self._heading:
            self._heading_parts.append(data)


def extract(path: Path) -> dict[str, object]:
    parser = SeoParser()
    parser.feed(path.read_text(encoding="utf-8"))
    title = " ".join("".join(parser.title_parts).split())
    meta_by_key: dict[str, str] = {}
    for item in parser.meta:
        key = item.get("name") or item.get("property") or item.get("http-equiv")
        if key:
            meta_by_key[key] = item.get("content", "")
    links_by_rel: dict[str, list[dict[str, str]]] = {}
    for item in parser.links:
        rel = item.get("rel")
        if rel:
            links_by_rel.setdefault(rel, []).append(item)
    return {
        "file": str(path),
        "title": title,
        "meta": meta_by_key,
        "links": links_by_rel,
        "jsonLdScripts": parser.json_ld_count,
        "headings": parser.headings[:10],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract basic SEO signals from local HTML files.")
    parser.add_argument("paths", nargs="+", help="HTML files to inspect")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    payload = [extract(Path(path)) for path in args.paths]
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    for page in payload:
        print(f"{page['file']}")
        print(f"  title: {page['title'] or '<missing>'}")
        meta = page["meta"]
        if isinstance(meta, dict):
            print(f"  description: {meta.get('description', '<missing>')}")
            print(f"  robots: {meta.get('robots', '<missing>')}")
        links = page["links"]
        if isinstance(links, dict):
            canonicals = links.get("canonical", [])
            hreflang = links.get("alternate", [])
            print(f"  canonical: {canonicals[0].get('href', '<missing>') if canonicals else '<missing>'}")
            print(f"  alternate links: {len(hreflang)}")
        print(f"  json-ld scripts: {page['jsonLdScripts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
