# Verification Checklist

Run the deterministic floor first when an engine binary is available; otherwise report exactly which checks are blocked and why.

## Deterministic Floor
1. Parse check: `godot --headless --check-only --script <changed>.gd` for every changed script, or a headless editor open (`godot --headless --editor --quit`) to surface parse and missing-resource errors project-wide.
2. Scene integrity: load each changed scene headlessly and confirm no missing node paths, broken signals, or missing resources in the output.
3. Run the project's test scene or GUT/GdUnit suite when one exists: `godot --headless -s <test-runner>`.
4. For export-affecting changes: validate the export preset and run a headless export to a scratch directory.

## Evidence Checklist
- The changed behavior was observed, not inferred: a run log, printed assertion, or test output shows the new behavior for the specific input that previously failed.
- Node paths, signal connections, and autoload references touched by the change are traced to their definitions in the project files, not assumed from naming.
- Input handling changes are checked against the project's InputMap, and physics changes against the affected collision layers/masks.
- Anything that needs a display, controller, or platform SDK to verify is listed as a residual gap with the concrete manual test to run.
