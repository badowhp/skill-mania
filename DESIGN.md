# Design System: Skill Mania

## 1. Overview

- Creative north star: **skill ledger** — a calm technical workbench that makes ownership, installation state, and evidence immediately inspectable.
- Register: mixed. `README.md` is a restrained technical brand surface; the Skill Manager is a dense product surface for repeated package-management work.
- Audience: developers evaluating, installing, auditing, and maintaining Agent Skills for Codex, Claude Code, and GitHub Copilot.
- Primary jobs: understand what the repository provides, choose a role package, inspect individual skill evidence, install it to an explicit target, and safely remove managed installs.
- Tone: direct, evidence-led, compact, and trustworthy. Avoid celebratory marketing language and vague claims.
- Technology: GitHub Markdown and SVG for the repository surface; Go standard-library HTTP/templates plus dependency-free CSS and JavaScript for the manager UI; Docker and Compose for optional distribution.
- Manager information architecture: compact header and global search; package rail; central skill ledger; contextual evidence inspector; persistent selection/action bar; explicit confirmation dialog for removal.
- Source of truth: `assets/readme-header.svg`, `README.md`, `cmd/skill-manager/`, `internal/skillmanager/web/`, and this file.
- Reference: native package managers and technical catalog tools that privilege scanability over decoration. Anti-references: generic SaaS landing pages, identical feature-card grids, oversized icon tiles, fake terminal screenshots, and ornamental dashboards.
- Freshness: 2026-07-21 implementation contract. UI tokens remain provisional until browser evidence passes desktop and narrow-mobile review.

## 2. Colors

- `--surface-page: #F5F5F7` — quiet repository and application canvas.
- `--surface-raised: #FFFFFF` — header, inspector, modal, and focused work areas.
- `--surface-inset: #ECECF0` — filters, code, metrics, and subdued selected regions.
- `--text-primary: #1D1D1F`; `--text-muted: #5E5E68`; `--text-disabled: #8E8E98`.
- `--action-primary: #0068D9`; `--action-hover: #0058B8`; `--focus: #007AFF`.
- `--border: #D2D2D7`; `--divider: #E5E5E9`.
- `--success: #197A4A`; `--warning: #9A6200`; `--danger: #B4232C`; `--info: #1769AA`.
- Benchmark deltas use success, warning, or muted text plus an explicit label; color never carries the result alone.
- No gradients, glass effects, ambient glows, or decorative color fields.

## 3. Typography

- Body and headings: `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`.
- Data, versions, paths, commands, and benchmark metrics: `ui-monospace, "SFMono-Regular", Consolas, monospace`.
- Manager scale: 24/30 page title, 18/24 section title, 15/22 body, 13/18 labels and metadata, 12/16 compact metrics.
- README uses native GitHub typography; do not simulate application typography with HTML styling.
- Skill names and group labels wrap at natural hyphen boundaries. Descriptions clamp to two lines in the ledger and remain complete in the inspector.
- Numbers use tabular alignment where the platform supports it. Never abbreviate pass rates or benchmark deltas so aggressively that meaning is lost.

## 4. Elevation

- Depth model: mostly flat and divided. Use one-pixel borders and surface changes before shadow.
- Radius scale: 6px controls, 10px panels and dialogs, fully rounded only for small status indicators.
- Shadow: one restrained modal shadow; no card shadows or floating decoration.
- Motion: 120–180ms opacity or transform for inspector and dialog state only. Disable nonessential motion under `prefers-reduced-motion`.
- Focus: visible two-pixel focus ring with offset on every interactive element.
- Hover must reinforce clickability without moving layout. Loading preserves stable dimensions.

## 5. Components

- Header: compact brand mark, repository context, health state, and documentation link. It must not consume the first viewport.
- Package rail: named groups with descriptions and skill counts. Active state uses weight, border, and background, not color alone.
- Search and filters: one descriptive search field, target selector, installed-state filter, and visible-selection toggle.
- Skill ledger: checkbox, skill name, concise description, selected-target state, eval coverage, and latest saved benchmark result. The inspector carries group membership and all-target state. Rows are dividers, not nested cards.
- Evidence inspector: full trigger description, group membership, positive and near-miss eval counts, latest benchmark provenance and delta, install state, and source path.
- Selection bar: selected count plus install and remove actions. Removal is danger-styled and unavailable for unmanaged entries.
- Confirmation dialog: names the target and every skill to remove, explains that only managed installs are eligible, supports Escape, traps focus, and requires an explicit confirmation action.
- Feedback: inline loading, success, partial-success, and error summaries with an `aria-live` region. Operations report per-skill results rather than collapsing partial failure.
- Empty states: no catalog, no matching skills, no saved benchmark, target not mounted, and no managed install.
- Responsive behavior: three columns above 1100px; package rail plus ledger between 760px and 1099px with inspector as dialog; single-column ledger below 760px with package filters in a horizontal scroll region and detail as a full-width dialog.
- Long content: paths and identifiers wrap; package and skill lists scroll within the page only where focus remains reachable; no accidental horizontal page scrolling.
- Touch targets are at least 44px high on narrow screens. Controls have hover, focus-visible, disabled, loading, selected, and error states.

## 6. Do’s And Don’ts

- Do use the central skill ledger as the dominant surface and expose benchmark provenance beside every quality claim.
- Do keep repository source read-only in the container and mount only the two explicit installation targets read-write.
- Do make safe state obvious: managed, unmanaged, missing mount, no benchmark, and operation failure must look and read differently.
- Do use real skill descriptions, eval manifests, saved benchmark data, and installation state. Screenshots must use the running product.
- Do preserve keyboard operation, semantic landmarks, labels, focus order, reduced motion, and narrow-screen access to every primary action.
- Do keep `README.md` focused on value, fastest install paths, one manager screenshot, and links to detailed guides.
- Don’t use gradients, glass, side-accent cards, nested cards, huge icons, fake screenshots, generic feature grids, or decorative charts.
- Don’t expose arbitrary filesystem paths, shell commands, Docker socket access, or deletion of unmanaged directories through the UI.
- Don’t hide destructive consequences behind an icon-only control or rely on a browser confirmation as the only server-side safeguard.
- Don’t claim benchmark coverage when only eval fixtures exist; label missing saved results explicitly.
