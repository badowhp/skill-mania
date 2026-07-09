from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VISUAL_QA = REPO_ROOT / "skills" / "visual-qa" / "scripts" / "visual-qa.mjs"


class VisualQaTests(unittest.TestCase):
    def test_help_is_available_without_browser_dependencies(self) -> None:
        result = subprocess.run(
            ["node", str(VISUAL_QA), "--help"],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Requires an existing local playwright", result.stdout)

    def test_dry_run_resolves_default_evidence_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "node",
                    str(VISUAL_QA),
                    "--url",
                    "http://localhost:3000",
                    "--path",
                    "/settings",
                    "--output",
                    tmp,
                    "--dry-run",
                ],
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["routes"], ["http://localhost:3000/settings"])
        self.assertEqual({item["name"] for item in payload["viewports"]}, {"desktop", "mobile"})

    def test_rejects_relative_route_path(self) -> None:
        result = subprocess.run(
            [
                "node",
                str(VISUAL_QA),
                "--url",
                "http://localhost:3000",
                "--path",
                "settings",
                "--output",
                "/tmp/visual-qa",
                "--dry-run",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("must start with /", result.stderr)


if __name__ == "__main__":
    unittest.main()
