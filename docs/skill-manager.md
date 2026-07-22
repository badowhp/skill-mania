# Local Skill Manager

The Skill Mania Manager is a local Go web application for browsing the repository catalog, selecting workflow packages, installing one or many skills, reviewing saved benchmark evidence, and removing manager-owned copies.

## Start with Docker Compose

Docker Desktop or Docker Engine with Compose v2 is required.

```bash
docker compose up --build --detach
```

Open <http://127.0.0.1:8787>.

The build creates the local image `skill-mania:local`. Compose does not pull or push an application image. Docker may download the pinned Go builder image when it is not already available locally.

Stop the manager without deleting installed skills:

```bash
docker compose down
```

## Skill directories

The container receives only the exact skill directories it needs. The repository and Docker socket are not mounted.

| Target | Default host directory | Container directory |
| --- | --- | --- |
| Codex compatibility install | `~/.codex/skills` | `/targets/agents` |
| Claude Code personal skills | `~/.claude/skills` | `/targets/claude` |

The Codex compatibility default matches installations created by older Skill Mania releases. Current Codex documentation uses `~/.agents/skills` for personal skills. Point the manager at that location when applicable:

```bash
CODEX_SKILLS_DIR="$HOME/.agents/skills" docker compose up --build --detach
```

Use a different Claude directory in the same way:

```bash
CLAUDE_SKILLS_DIR="/absolute/path/to/skills" docker compose up --build --detach
```

On Linux, pass the host user and group when bind-mount permissions require it:

```bash
SKILL_MANAGER_UID="$(id -u)" \
SKILL_MANAGER_GID="$(id -g)" \
docker compose up --build --detach
```

## Ownership and deletion

Copies installed by the current manager contain `.skill-mania-managed.json`. They can be updated or removed from the UI.

Older copies without that marker appear as **Unmanaged install**. The manager displays them but does not overwrite or delete them. To adopt one exact catalog skill, review the existing directory first and then use the command-line installer with both explicit replacement flags:

```bash
./scripts/install-local.sh --agents --copy --skill seo-geo --force --force-unmanaged
```

The installer stages the replacement before moving the old directory and restores the previous install if activation fails. The standard replacement flag alone never replaces an unmanaged directory.

Claude plugin skills remain owned by Claude Code. Manage those through `/plugin` or `claude plugin` rather than deleting plugin cache files from this UI.

## Benchmark information

The image contains `benchmarks/catalog.json`, a static aggregate of compact benchmark summaries. It records every catalog skill, all saved runs, the latest result, model provenance, pass-rate deltas, and explicit `not-saved` entries. Raw prompts, model responses, credentials, and machine-specific workspace paths are not included.

Refresh the catalog after adding a compact snapshot:

```bash
python3 scripts/build-benchmark-catalog.py
```

Import a local benchmark summary without committing its raw workspace:

```bash
python3 scripts/build-benchmark-catalog.py \
  --include release-label=/absolute/path/to/benchmark.json
```

## Troubleshooting

### Codex skills show as not installed

Check which directory contains the copies:

```bash
find "$HOME/.codex/skills" "$HOME/.agents/skills" \
  -maxdepth 2 -name SKILL.md -print 2>/dev/null
```

Set `CODEX_SKILLS_DIR` to the populated directory and recreate the container.

### A copied skill shows as unmanaged

This is expected for copies created before ownership markers were introduced. The protection prevents accidental deletion of user-maintained or third-party directories.

### View service health and logs

```bash
docker compose ps
docker compose logs --follow skill-manager
curl --fail http://127.0.0.1:8787/healthz
```
