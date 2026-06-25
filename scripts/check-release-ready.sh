#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

python3 scripts/validate-skills.py skills plugins/skill-mania/skills
./scripts/sync-plugin-package.sh --check
python3 -m unittest discover -s tests
bash -n scripts/*.sh

placeholder_hits="$(
  find skills plugins/skill-mania/skills -path '*/hip0-mania/*' -prune -o -type f -print0 \
    | xargs -0 grep -En '(^|[^[:alnum:]_])TODO([^[:alnum:]_]|$)|^## Fill In' || true
)"
if [[ -n "$placeholder_hits" ]]; then
  echo "placeholder text found outside hip0-mania:" >&2
  printf '%s\n' "$placeholder_hits" >&2
  exit 1
fi

node skills/design-engineer/scripts/scan-design-tells.mjs --fail-on high skills/design-engineer
python3 skills/writing-assistant/scripts/scan-ai-slop-text.py --json README.md >/dev/null

plan_json="$(mktemp)"
trap 'rm -f "$plan_json"' EXIT
printf '%s\n' '{"resource_changes":[{"address":"google_project_iam_member.viewer","type":"google_project_iam_member","change":{"actions":["create"]}},{"address":"google_sql_database_instance.main","type":"google_sql_database_instance","change":{"actions":["delete","create"]}}]}' > "$plan_json"
python3 skills/senior-devops-engineer/scripts/summarize-terraform-plan.py "$plan_json" >/dev/null

install_tmp="$(mktemp -d)"
trap 'rm -rf "$install_tmp" "$plan_json"' EXIT
CODEX_SKILLS_DIR="$install_tmp/codex" CLAUDE_SKILLS_DIR="$install_tmp/claude" ./scripts/install-local.sh --all --copy >/dev/null
for skill_dir in skills/*; do
  [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]] || continue
  skill_name="$(basename "$skill_dir")"
  test -f "$install_tmp/codex/$skill_name/SKILL.md"
  test -f "$install_tmp/claude/$skill_name/SKILL.md"
done

generated_hits="$(
  find "$install_tmp" \( -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store' -o -name '.tmp' -o -name '.cache' \) -print
)"
if [[ -n "$generated_hits" ]]; then
  echo "generated files found in copied local install:" >&2
  printf '%s\n' "$generated_hits" >&2
  exit 1
fi

echo "release readiness checks passed"
