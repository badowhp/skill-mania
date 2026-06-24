#!/usr/bin/env python3
"""Scan reader-facing prose for common AI-slop text tells."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXTS = {".html", ".htm", ".markdown", ".md", ".mdx", ".rst", ".text", ".txt"}
SKIP_DIRS = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "vendor",
    "venv",
}
SEVERITY_RANK = {"off": 99, "low": 1, "medium": 2, "high": 3}
WEIGHT = {"low": 1, "medium": 2, "high": 3}


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    message: str
    remediation: str
    patterns: tuple[re.Pattern[str], ...]
    raw: bool = False


def compile_patterns(*patterns: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)


RULES = (
    Rule(
        id="dash-punctuation",
        severity="high",
        message="real em dash or spaced en dash",
        remediation="Use a comma, period, or parentheses unless the mark is an intentional voice choice.",
        patterns=compile_patterns(r"\u2014", r"\s\u2013\s", r"\u2013\u2013"),
        raw=True,
    ),
    Rule(
        id="assistant-boilerplate",
        severity="high",
        message="leftover assistant boilerplate",
        remediation="Delete model disclaimers, cutoff references, refusals, and meta-commentary.",
        patterns=compile_patterns(
            r"\bas an?\s+(ai|a\.i\.)\s+(language\s+)?model\b",
            r"\bas a large language model\b",
            r"\bknowledge cut[- ]?off\b",
            r"\bas of my last (knowledge )?(update|training)\b",
            r"\bi (cannot|can't|am unable to)\s+(assist|help|fulfil|fulfill|comply|provide)\b",
            r"\bi (do not|don't) have (personal|the ability|access|feelings|opinions)\b",
        ),
    ),
    Rule(
        id="not-just-x-y",
        severity="high",
        message="manufactured antithesis cadence",
        remediation="State the actual point plainly instead of negating one claim to elevate another.",
        patterns=compile_patterns(
            r"\b(it'?s|it is|this is|that'?s|that is|they'?re|they are)\s+not\s+(just|only|merely|simply)\b[^.?!\n]{0,80}\b(it'?s|it is|they'?re|they are)\b",
            r"\bnot\s+(just|only|merely|simply)\s+(a |an |the )?[\w-]+,?\s+but\b",
            r"\bisn'?t\s+(just|only|merely)\b[^.?!\n]{0,80}\b(it'?s|it is|they'?re|they are)\b",
        ),
    ),
    Rule(
        id="sycophancy-opener",
        severity="high",
        message="sycophantic or reflexively agreeable opener",
        remediation="Open with the point. Cut flattery and agree only when the substance warrants it.",
        patterns=compile_patterns(
            r"\b(great|good|excellent|fascinating)\s+question\b",
            r"(^|[\"'`(]\s*)(certainly|absolutely|sure thing|of course)\s*[!,]",
            r"\bi'?d be (happy|glad|delighted) to\b",
            r"\bhappy to help\b",
            r"\byou'?re absolutely right\b",
        ),
    ),
    Rule(
        id="assistant-offer",
        severity="high",
        message="trailing assistant offer or chat sign-off",
        remediation="End on the final useful sentence. Remove meta-offers to revise or continue.",
        patterns=compile_patterns(
            r"\bwould you like me to\b",
            r"\blet me know if you'?d?\s*(like|need|want|have)\b",
            r"\bi hope this helps\b",
            r"\bfeel free to (ask|reach|let me)\b",
            r"\bis there anything else\b",
        ),
    ),
    Rule(
        id="bolded-lead-in",
        severity="medium",
        message="standalone bolded lead-in label or mini-heading",
        remediation="Use a normal sentence unless the format genuinely needs labeled fields.",
        patterns=compile_patterns(r"^\s{0,3}\*\*[^*\n]{2,40}:?\*\*\s*:?\s"),
    ),
    Rule(
        id="ai-diction",
        severity="medium",
        message="cluster-prone AI diction",
        remediation="Swap to the plain word the speaker would actually use.",
        patterns=compile_patterns(
            r"\bdelv(e|es|ing|ed)\b",
            r"\btapestr(y|ies)\b",
            r"\bleverag(e|es|ing|ed)\b",
            r"\bseamless(ly)?\b",
            r"\bgame[- ]?chang(er|ers|ing)\b",
            r"\bunleash(es|ing|ed)?\b",
            r"\bunderscore(s|d|ing)?\b",
            r"\bmeticulous(ly)?\b",
            r"\belevat(e|es|ing|ed)\b",
            r"\bharness(es|ing|ed)?\b",
            r"\bever[- ]?(evolving|changing)\b",
        ),
    ),
    Rule(
        id="dive-in",
        severity="medium",
        message="announced start instead of starting",
        remediation="Cut the metaphor and begin with the topic or claim.",
        patterns=compile_patterns(r"\b(deep dive|dives? in(to)?|let'?s dive|diving in|dive deep)\b"),
    ),
    Rule(
        id="hollow-opener",
        severity="medium",
        message="broad scene-setting opener",
        remediation="Start with a specific claim, fact, scene, or pressure point.",
        patterns=compile_patterns(
            r"\bin today'?s\s+(fast[- ]?paced|digital|ever[- ]?changing|modern|competitive)?\s*(world|age|landscape|era|society|market)\b",
            r"\bin (the|this) (modern|digital) (world|age|era)\b",
        ),
    ),
    Rule(
        id="unlock-potential",
        severity="medium",
        message="generic unlock or unleash hype",
        remediation="Say what the thing does, with a concrete object or outcome.",
        patterns=compile_patterns(
            r"\b(unlock|unleash|harness|tap into)\w*\s+(the\s+|your\s+|its\s+|their\s+|full\s+)*(power|potential|capabilities|secrets)\b",
            r"\b(supercharge|revolutioni[sz]e|transform your|take .* to the next level)\b",
        ),
    ),
    Rule(
        id="listicle-scaffold",
        severity="medium",
        message="listicle scaffold",
        remediation="Use prose unless the material is genuinely a list of steps, parts, or options.",
        patterns=compile_patterns(
            r"(^|\s)#{0,4}\s*\d+\s+(ways|tips|signs|reasons|things|steps|tricks|secrets|lessons|mistakes|rules)\b"
        ),
    ),
    Rule(
        id="emoji-structure",
        severity="medium",
        message="decorative emoji used as structure",
        remediation="Use plain headings, normal bullets, or a real visual system.",
        patterns=compile_patterns(
            r"^\s{0,3}#{1,6}\s*[\U0001f300-\U0001faff\u2600-\u27bf]",
            r"^\s{0,3}[\U0001f300-\U0001faff\u2600-\u27bf]\s+\S",
            r"[\U0001f300-\U0001faff\u2600-\u27bf]\s*\*\*",
        ),
    ),
    Rule(
        id="signposted-recap",
        severity="medium",
        message="signposted recap ending",
        remediation="End on the final substantive point instead of announcing a conclusion.",
        patterns=compile_patterns(
            r"\bin (conclusion|summary)\b",
            r"\bto (summari[sz]e|conclude|wrap (this |it )?up)\b",
            r"\bin closing\b",
        ),
    ),
    Rule(
        id="forced-casual",
        severity="low",
        message="forced casual opener",
        remediation="Use casual markers only when they belong to the speaker and context.",
        patterns=compile_patterns(r"\b(here'?s the thing|look,|real talk|honestly[,?])\b"),
    ),
    Rule(
        id="transition-stack",
        severity="low",
        message="formal connective scaffold",
        remediation="Let the ideas connect directly unless the formal register needs the connective.",
        patterns=compile_patterns(r"\b(moreover|furthermore|additionally|consequently)\b"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="file or directory to scan")
    parser.add_argument("--json", action="store_true", help="print JSON output")
    parser.add_argument(
        "--fail-on",
        choices=SEVERITY_RANK.keys(),
        default="off",
        help="exit 1 when findings at or above this severity are present",
    )
    parser.add_argument("--max-findings", type=int, default=0, help="cap findings; 0 means unlimited")
    return parser.parse_args()


def iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() in EXTS else []

    files: list[Path] = []
    for current_root, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        for name in names:
            path = Path(current_root) / name
            if path.suffix.lower() in EXTS:
                files.append(path)
    return sorted(files)


def strip_examples(line: str) -> str:
    line = re.sub(r"`[^`]*`", "", line)
    return re.sub(r'"[^"]*"', "", line)


def scan_file(path: Path, root: Path, max_findings: int) -> tuple[list[dict[str, object]], int]:
    findings: list[dict[str, object]] = []
    word_count = 0
    in_fence = False

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except (FileNotFoundError, IsADirectoryError, OSError):
            return findings, word_count
    except (FileNotFoundError, IsADirectoryError, OSError):
        return findings, word_count

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or "ai-slop-ignore" in line or "unslop-ignore" in line:
            continue

        word_count += len(re.findall(r"\b[\w'-]+\b", line))
        normal_text = "" if stripped.startswith(">") else strip_examples(line)

        for rule in RULES:
            text = line if rule.raw else normal_text
            if not text:
                continue
            for pattern in rule.patterns:
                match = pattern.search(text)
                if not match:
                    continue
                findings.append(
                    {
                        "file": str(path.relative_to(root)) if path != root else path.name,
                        "line": line_number,
                        "id": rule.id,
                        "severity": rule.severity,
                        "match": match.group(0)[:80],
                        "message": rule.message,
                        "remediation": rule.remediation,
                    }
                )
                break
            if max_findings and len(findings) >= max_findings:
                return findings, word_count

    return findings, word_count


def main() -> int:
    args = parse_args()
    target = Path(args.path).resolve()
    if not target.exists():
        print(f"path not found: {target}", file=sys.stderr)
        return 2
    if args.max_findings < 0:
        print("--max-findings must be non-negative", file=sys.stderr)
        return 2

    files = iter_files(target)
    root = target if target.is_dir() else target.parent
    findings: list[dict[str, object]] = []
    word_count = 0

    for path in files:
        remaining = 0 if args.max_findings == 0 else max(args.max_findings - len(findings), 0)
        if args.max_findings and remaining == 0:
            break
        file_findings, file_words = scan_file(path, root, remaining)
        findings.extend(file_findings)
        word_count += file_words

    score = sum(WEIGHT[str(finding["severity"])] for finding in findings)
    density = round((score / max(word_count, 1)) * 1000, 2)
    failing = [
        finding
        for finding in findings
        if SEVERITY_RANK[str(finding["severity"])] >= SEVERITY_RANK[args.fail_on]
    ]

    if args.json:
        print(
            json.dumps(
                {
                    "root": str(target),
                    "words": word_count,
                    "score": score,
                    "density_per_1000_words": density,
                    "fail_on": args.fail_on,
                    "findings": findings,
                    "failing_findings": len(failing),
                },
                indent=2,
            )
        )
        return 1 if failing else 0

    if not findings:
        print("No common AI-slop text tells found.")
        return 0

    for finding in findings:
        print(
            f"{finding['file']}:{finding['line']} {finding['severity']} "
            f"{finding['id']} - {finding['message']}"
        )
        print(f"  match: {finding['match']}")
        print(f"  fix: {finding['remediation']}")

    print(
        f"\n{len(findings)} finding(s). score={score}. "
        f"density={density} per 1,000 words. {len(failing)} meet --fail-on={args.fail_on}."
    )
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
