from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "skills" / "design-engineer" / "scripts" / "scan-design-tells.mjs"


class DesignScannerTests(unittest.TestCase):
    def test_json_output_reports_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Component.tsx"
            fixture.write_text(
                "export function Hero(){return <div className=\"from-purple-500 rounded-3xl\">Transform your workflow</div>}\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", tmp],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertGreaterEqual(len(payload["findings"]), 3)
            self.assertEqual(payload["failingFindings"], 0)

    def test_fail_on_medium_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Hero.tsx"
            fixture.write_text(
                "export const copy = 'Supercharge your team';\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--fail-on", "medium", tmp],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("generic-copy", result.stdout)

    def test_single_file_input_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Hero.tsx"
            fixture.write_text(
                "export const copy = 'Supercharge your team';\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", str(fixture)],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["findings"][0]["file"], "Hero.tsx")
            self.assertEqual(payload["findings"][0]["id"], "generic-copy")

    def test_production_ui_tells_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Landing.tsx"
            fixture.write_text(
                "\n".join(
                    [
                        "export const hero = 'next-generation hardware';",
                        "export const className = 'bg-amber-50 font-serif bg-clip-text text-[8vw]';",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", tmp],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            ids = {finding["id"] for finding in payload["findings"]}
            self.assertIn("cream-default", ids)
            self.assertIn("default-display-serif", ids)
            self.assertIn("gradient-text", ids)
            self.assertIn("viewport-scaled-type", ids)
            self.assertIn("generic-copy", ids)

    def test_reviewed_exception_comment_suppresses_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Brand.tsx"
            fixture.write_text(
                "export const className = 'from-purple-500 rounded-3xl'; // design-tell-ignore: established brand\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", tmp],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["findings"], [])


if __name__ == "__main__":
    unittest.main()
