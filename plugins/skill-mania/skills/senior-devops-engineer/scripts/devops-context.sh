#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

if [[ ! -d "$root" ]]; then
  echo "path not found: $root" >&2
  exit 2
fi

cd "$root"

section() {
  printf '\n## %s\n' "$1"
}

section "Repository"
pwd
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git status --short
fi

section "CI"
find .github .gitlab-ci.yml Jenkinsfile cloudbuild.yaml cloudbuild.yml \
  -maxdepth 3 -type f 2>/dev/null | sort || true

section "Infrastructure"
find . -path './.git' -prune -o -path './node_modules' -prune -o \
  \( -name '*.tf' -o -name 'terragrunt.hcl' -o -name 'ansible.cfg' -o -name 'site.yml' -o -name 'playbook*.yml' \) \
  -type f -print | sort | head -200

section "Containers"
find . -path './.git' -prune -o -path './node_modules' -prune -o \
  \( -name 'Dockerfile*' -o -name 'docker-compose*.yml' -o -name 'compose.yml' \) \
  -type f -print | sort | head -200

section "Runtime Hints"
find . -maxdepth 3 \( -path './.git' -o -path './node_modules' \) -prune -o -type f \
  \( -name 'package.json' -o -name 'requirements*.txt' -o -name 'pyproject.toml' -o -name 'go.mod' -o -name 'go.work' -o -name 'pom.xml' -o -name 'build.gradle' -o -name 'build.gradle.kts' -o -name 'settings.gradle' -o -name 'settings.gradle.kts' -o -name 'gradlew' -o -name 'mvnw' -o -name 'Cargo.toml' \) \
  -print | sort
