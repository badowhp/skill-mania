#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/install-local.sh [--all|--agents|--codex|--claude] [--profile <name>]... [--link|--copy] [--force] [--no-validate]

Options:
  --all      Install for Codex and Claude Code. Default when no target is set.
  --agents   Install into the shared Codex and GitHub Copilot skills directory.
  --codex    Alias for --agents for backward compatibility.
  --claude   Install into Claude Code skills directory.
  --profile  Install one named skill profile. Repeat to combine profiles:
             core, content, games, or regional. Without this option, install all skills.
  --link     Symlink skills from this repo. Default.
  --copy     Copy skills into the target directory.
  --force    Replace existing destination skill directories or symlinks.
  --no-validate
            Skip repository validation before installing.

Environment:
  AGENT_SKILLS_DIR   Override shared Codex and GitHub Copilot target directory.
  CODEX_SKILLS_DIR   Backward-compatible alias when AGENT_SKILLS_DIR is unset.
  CLAUDE_SKILLS_DIR  Override Claude Code target directory.
USAGE
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
mode="link"
install_codex=0
install_claude=0
force=0
validate_before_install=1
profiles=()
selected_skills=()
rsync_options=(
  --exclude '.DS_Store'
  --exclude '__pycache__/'
  --exclude '*.pyc'
  --exclude '.tmp/'
  --exclude '.cache/'
  --exclude 'node_modules/'
)

resolve_path() {
  local path="$1"
  mkdir -p "$path"
  (cd "$path" && pwd -P)
}

assert_safe_target_root() {
  local label="$1"
  local target_root="$2"
  local target_root_abs home_abs repo_skills_abs

  target_root_abs="$(resolve_path "$target_root")"
  home_abs="$(cd "$HOME" && pwd -P)"
  repo_skills_abs="$(cd "$repo_root/skills" && pwd -P)"

  case "$target_root_abs" in
    "/"|"$home_abs"|"$repo_root"|"$repo_skills_abs")
      echo "refusing unsafe $label target directory: $target_root_abs" >&2
      exit 1
      ;;
  esac

  printf '%s\n' "$target_root_abs"
}

remove_existing_skill() {
  local label="$1"
  local skill_name="$2"
  local skill_dest="$3"

  if [[ -L "$skill_dest" ]]; then
    rm "$skill_dest"
    return
  fi

  if [[ -d "$skill_dest" && -f "$skill_dest/SKILL.md" ]]; then
    rm -rf "$skill_dest"
    return
  fi

  echo "refusing to replace $label:$skill_name - $skill_dest is not a skill directory or symlink" >&2
  exit 1
}

version_at_least() {
  local actual="$1"
  local required="$2"
  local actual_major actual_minor actual_patch required_major required_minor required_patch
  IFS=. read -r actual_major actual_minor actual_patch <<<"$actual"
  IFS=. read -r required_major required_minor required_patch <<<"$required"
  if (( actual_major != required_major )); then
    (( actual_major > required_major ))
    return
  fi
  if (( actual_minor != required_minor )); then
    (( actual_minor > required_minor ))
    return
  fi
  (( actual_patch >= required_patch ))
}

assert_claude_link_support() {
  command -v claude >/dev/null 2>&1 || return 0
  local output version
  output="$(claude --version 2>/dev/null || true)"
  version="$(printf '%s\n' "$output" | sed -nE 's/.*([0-9]+\.[0-9]+\.[0-9]+).*/\1/p' | head -n 1)"
  [[ -n "$version" ]] || return 0
  if ! version_at_least "$version" "2.1.203"; then
    echo "Claude Code $version does not support symlinked skills; upgrade to 2.1.203 or newer, or rerun with --copy" >&2
    exit 1
  fi
}

skill_selected() {
  local candidate="$1"
  local selected
  [[ "${#selected_skills[@]}" -eq 0 ]] && return 0
  for selected in "${selected_skills[@]}"; do
    [[ "$selected" == "$candidate" ]] && return 0
  done
  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      install_codex=1
      install_claude=1
      ;;
    --agents|--codex)
      install_codex=1
      ;;
    --claude)
      install_claude=1
      ;;
    --profile)
      if [[ $# -lt 2 ]]; then
        echo "--profile requires a profile name" >&2
        exit 2
      fi
      shift
      profiles+=("$1")
      ;;
    --link)
      mode="link"
      ;;
    --copy)
      mode="copy"
      ;;
    --force)
      force=1
      ;;
    --no-validate)
      validate_before_install=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "${#profiles[@]}" -gt 0 ]]; then
  profile_output="$(python3 "$repo_root/scripts/list-profile-skills.py" "${profiles[@]}")" || exit 2
  while IFS= read -r selected_skill; do
    [[ -n "$selected_skill" ]] && selected_skills+=("$selected_skill")
  done <<<"$profile_output"
fi

if [[ "$install_codex" -eq 0 && "$install_claude" -eq 0 ]]; then
  install_codex=1
  install_claude=1
fi

if [[ "$mode" == "copy" ]] && ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required for copy installs" >&2
  exit 1
fi

if [[ "$install_claude" -eq 1 && "$mode" == "link" ]]; then
  assert_claude_link_support
fi

if [[ "$validate_before_install" -eq 1 ]]; then
  python3 "$repo_root/scripts/validate-skills.py" "$repo_root/skills" >/dev/null
fi

default_codex_dir="$HOME/.agents/skills"
if [[ -z "${AGENT_SKILLS_DIR:-}" && -z "${CODEX_SKILLS_DIR:-}" && -d "$HOME/.codex/skills" && ! -d "$HOME/.agents/skills" ]]; then
  default_codex_dir="$HOME/.codex/skills"
fi

codex_dir="${AGENT_SKILLS_DIR:-${CODEX_SKILLS_DIR:-$default_codex_dir}}"
claude_dir="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

install_to() {
  local label="$1"
  local target_root="$2"

  target_root="$(assert_safe_target_root "$label" "$target_root")"

  local skill_src skill_name skill_dest
  for skill_src in "$repo_root"/skills/*; do
    [[ -d "$skill_src" && -f "$skill_src/SKILL.md" ]] || continue
    skill_name="$(basename "$skill_src")"
    skill_selected "$skill_name" || continue
    skill_dest="$target_root/$skill_name"

    if [[ -e "$skill_dest" || -L "$skill_dest" ]]; then
      if [[ "$force" -eq 1 ]]; then
        remove_existing_skill "$label" "$skill_name" "$skill_dest"
      else
        echo "skip $label:$skill_name - $skill_dest already exists; use --force to replace"
        continue
      fi
    fi

    if [[ "$mode" == "link" ]]; then
      ln -s "$skill_src" "$skill_dest"
    else
      rsync -a "${rsync_options[@]}" "$skill_src"/ "$skill_dest"/
    fi

    echo "installed $label:$skill_name -> $skill_dest"
  done
}

if [[ "$install_codex" -eq 1 ]]; then
  install_to "agents" "$codex_dir"
fi

if [[ "$install_claude" -eq 1 ]]; then
  install_to "claude" "$claude_dir"
fi
