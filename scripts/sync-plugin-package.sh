#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
canonical_skills="$repo_root/skills"
plugin_skills="$repo_root/plugins/skill-mania/skills"

if [[ "${1:-}" == "--check" ]]; then
  diff -qr "$canonical_skills" "$plugin_skills"
  exit 0
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required to sync the plugin package" >&2
  exit 1
fi

mkdir -p "$plugin_skills"
rsync -a --delete "$canonical_skills"/ "$plugin_skills"/
echo "synced $canonical_skills -> $plugin_skills"

