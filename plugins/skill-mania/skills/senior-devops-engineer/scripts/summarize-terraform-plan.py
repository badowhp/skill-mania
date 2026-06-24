#!/usr/bin/env python3
"""Summarize high-risk changes from `terraform show -json plan.out` output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RISK_RESOURCE_TERMS = {
    "iam": ("iam", "binding", "member", "policy", "service_account"),
    "network": ("firewall", "route", "nat", "network", "subnetwork", "address"),
    "database": ("sql", "database", "postgres", "mysql", "redis", "memorystore"),
    "secret": ("secret", "kms", "key_ring", "crypto_key"),
    "public": ("load_balancer", "forwarding_rule", "ssl", "dns", "certificate"),
}


def load_plan(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"plan file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON plan: {exc}")


def classify(resource_type: str, address: str) -> list[str]:
    haystack = f"{resource_type} {address}".lower()
    return [
        label
        for label, terms in RISK_RESOURCE_TERMS.items()
        if any(term in haystack for term in terms)
    ]


def summarize(plan: dict[str, Any]) -> list[dict[str, Any]]:
    changes = []
    for change in plan.get("resource_changes", []):
        resource_type = change.get("type", "")
        address = change.get("address", "")
        actions = change.get("change", {}).get("actions", [])
        if actions == ["no-op"]:
            continue
        risk = classify(resource_type, address)
        destructive = any(action in actions for action in ("delete", "replace"))
        if destructive or risk:
            changes.append(
                {
                    "address": address,
                    "type": resource_type,
                    "actions": actions,
                    "risk": risk or ["general-change"],
                    "destructive": destructive,
                }
            )
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize risky Terraform plan changes from JSON output."
    )
    parser.add_argument("plan_json", help="Path to `terraform show -json` output")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    findings = summarize(load_plan(Path(args.plan_json)))
    if args.json:
        print(json.dumps(findings, indent=2))
        return 0

    if not findings:
        print("No destructive or high-signal resource changes found.")
        return 0

    for finding in findings:
        actions = ",".join(finding["actions"])
        risk = ",".join(finding["risk"])
        marker = "DESTRUCTIVE" if finding["destructive"] else "REVIEW"
        print(f"{marker} {finding['address']} [{actions}] risk={risk}")

    print(f"\n{len(findings)} change(s) need senior review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
