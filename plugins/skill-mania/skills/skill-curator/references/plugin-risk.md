# Plugin Risk

Plugins and MCP servers can change the agent's authority. Review them as code plus permissions, not just instructions.

## Manifest Review
- name, publisher, repository, homepage, version, license, and update channel
- skills, tools, commands, hooks, resources, and assets exposed
- default prompts or system overlays that could change behavior globally
- install scripts, postinstall hooks, binary downloads, or opaque bundles
- requested file-system, shell, network, browser, and credential access

## Trust Boundaries
- Can the plugin read secrets, dotfiles, repos, browser state, or CI tokens?
- Can it write outside the workspace?
- Can it run arbitrary shell commands or download code?
- Does it proxy user data to a third-party service?
- Is the update source pinned, signed, reviewed, or mutable?
- Does it include code that can run during install or task execution?

## Licensing And Provenance
- Confirm license compatibility before copying instructions, code, or assets.
- Preserve required notices and upstream commit references.
- Avoid adopting unclear or missing-license content into production skills.
- Prefer adapting behavior in your own words when licensing is restrictive or unclear.

## Safe Recommendation Defaults
- Prefer local skill adaptation over installing a broad tool plugin when only instructions are needed.
- Prefer read-only tools for audit workflows.
- Recommend sandboxed testing before enabling write, shell, browser, or network authority.
- Reject plugins that hide install behavior, request broad credentials without need, or blur user data boundaries.
