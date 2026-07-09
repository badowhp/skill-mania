# Skill Mania README Surface

## Direction

- Register: calm technical brand, not dashboard UI.
- Audience: developers deciding whether to trust, install, or contribute skills.
- First task: recognize the project and find the right skill quickly.
- North star: one clear wordmark, one distinctive icon, generous negative space, and no decorative product mockup.

## Header Rules

- Use a light neutral field, near-black wordmark, and one restrained blue accent family with the existing line-and-node icon.
- Keep only the icon and `Skill Mania` text in the header artwork. The README supplies the descriptive copy in accessible HTML text.
- Size the wordmark so it remains readable when a 1200px SVG scales to a 360px mobile viewport.
- Use a system-font stack. Do not embed proprietary font files.
- Avoid gradients, glass panels, faux browser chrome, grids, pill badges, diagrams, shadows, and ornamental dots.

## Visual System

- Canvas: `#F5F5F7`; ink: `#1D1D1F`; divider: `#D2D2D7`; primary accent: `#007AFF`; highlight: `#5AC8FA`.
- Use the system stack `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif` without embedding a font.
- Use a single 88px/700 wordmark on the 1200px artboard with `-3` tracking. It scales to about 26px at a 360px width.
- Use one 136px rounded icon with a 32px radius. Keep a 42px visual gap between icon and wordmark.
- Do not use text smaller than the wordmark in the artwork; supporting copy belongs in the README body.

## README Information Architecture

- Put a task-to-skill chooser before the full inventory.
- Group the inventory by job instead of listing every skill as a flat catalog.
- Keep overlays separate from domain roles.
- State canonical-source and trust boundaries plainly.

## Source Of Truth

- Header asset: `assets/readme-header.svg`.
- README structure: `README.md`.
- Plugin icon and logo remain separate package assets.
- Review the rendered SVG at its native 1200px width and a 360px-equivalent width before changing the header.

## Review Criteria

- At desktop and 360px-equivalent width, the wordmark remains the dominant readable element.
- The artwork supports repository discovery rather than competing with it.
- The image has an accurate text alternative and does not carry essential instructions.
