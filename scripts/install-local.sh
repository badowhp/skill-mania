#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/install-local.sh [--all|--codex|--claude] [--link|--copy] [--force] [--no-validate]

Options:
  --all      Install for Codex and Claude Code. Default when no target is set.
  --codex    Install into Codex skills directory.
  --claude   Install into Claude Code skills directory.
  --link     Symlink skills from this repo. Default.
  --copy     Copy skills into the target directory.
  --force    Replace existing destination skill directories or symlinks.
  --no-validate
            Skip repository validation before installing.

Environment:
  CODEX_SKILLS_DIR   Override Codex target directory.
  CLAUDE_SKILLS_DIR  Override Claude Code target directory.
USAGE
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
mode="link"
install_codex=0
install_claude=0
force=0
validate_before_install=1

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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      install_codex=1
      install_claude=1
      ;;
    --codex)
      install_codex=1
      ;;
    --claude)
      install_claude=1
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

if [[ "$install_codex" -eq 0 && "$install_claude" -eq 0 ]]; then
  install_codex=1
  install_claude=1
fi

if [[ "$validate_before_install" -eq 1 ]]; then
  python3 "$repo_root/scripts/validate-skills.py" "$repo_root/skills" >/dev/null
fi

default_codex_dir="$HOME/.agents/skills"
if [[ -z "${CODEX_SKILLS_DIR:-}" && -d "$HOME/.codex/skills" && ! -d "$HOME/.agents/skills" ]]; then
  default_codex_dir="$HOME/.codex/skills"
fi

codex_dir="${CODEX_SKILLS_DIR:-$default_codex_dir}"
claude_dir="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

install_to() {
  local label="$1"
  local target_root="$2"

  target_root="$(assert_safe_target_root "$label" "$target_root")"

  local skill_src skill_name skill_dest
  for skill_src in "$repo_root"/skills/*; do
    [[ -d "$skill_src" && -f "$skill_src/SKILL.md" ]] || continue
    skill_name="$(basename "$skill_src")"
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
      cp -R "$skill_src" "$skill_dest"
    fi

    echo "installed $label:$skill_name -> $skill_dest"
  done
}

if [[ "$install_codex" -eq 1 ]]; then
  install_to "codex" "$codex_dir"
fi

if [[ "$install_claude" -eq 1 ]]; then
  install_to "claude" "$claude_dir"
fi
