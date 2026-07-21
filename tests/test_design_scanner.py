from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "skills" / "design-engineer" / "scripts" / "scan-design-tells.mjs"
REFERENCE_SPEC = (
    REPO_ROOT / "skills" / "design-engineer" / "evals" / "fixtures" / "reference-spec.txt"
)


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

    def test_reviewed_exception_comment_suppresses_only_named_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Brand.tsx"
            fixture.write_text(
                "export const className = 'from-purple-500 rounded-3xl'; // design-tell-ignore: purple-gradient -- established brand\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", tmp],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            ids = {finding["id"] for finding in json.loads(result.stdout)["findings"]}
            self.assertNotIn("purple-gradient", ids)
            self.assertIn("oversized-radius", ids)

    def test_unscoped_exception_comment_does_not_suppress_checks(self) -> None:
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
            ids = {finding["id"] for finding in json.loads(result.stdout)["findings"]}
            self.assertIn("purple-gradient", ids)
            self.assertIn("oversized-radius", ids)

    def test_additional_ai_ui_tells_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Hero.tsx"
            fixture.write_text(
                "\n".join(
                    [
                        "window.addEventListener('scroll', () => {})",
                        "export const name = 'John Doe'",
                        "export const eyebrow = '001 / Platform'",
                        "export const media = 'fake screenshot'",
                        "export const className = 'h-screen cursor-none transition-all border-l-4'",
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
            ids = {finding["id"] for finding in json.loads(result.stdout)["findings"]}
            self.assertIn("scroll-listener", ids)
            self.assertIn("placeholder-persona", ids)
            self.assertIn("section-number-eyebrow", ids)
            self.assertIn("fake-screenshot", ids)
            self.assertIn("viewport-height-hero", ids)
            self.assertIn("custom-cursor", ids)
            self.assertIn("transition-all", ids)
            self.assertIn("side-accent-border", ids)


    def test_design_md_traceability_flags_untraced_colors_and_fails_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "DESIGN.md"
            design.write_text(
                "## 2. Colors\n- Primary ink: `#0a1f44`\n- Accent: `#e4572e`\n",
                encoding="utf-8",
            )
            fixture = Path(tmp) / "Hero.css"
            fixture.write_text(
                ".hero { color: #0a1f44; background: #ff00aa; border-color: #E4572E; }\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "node",
                    str(SCANNER),
                    "--json",
                    "--fail-on",
                    "medium",
                    "--design-md",
                    str(design),
                    str(fixture),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            findings = json.loads(result.stdout)["findings"]
            untraced = [f for f in findings if f["id"] == "untraced-color"]
            self.assertEqual(len(untraced), 1)
            self.assertIn("#ff00aa", untraced[0]["message"])

    def test_prohibited_design_colors_are_not_approved_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "DESIGN.md"
            design.write_text(
                "\n".join(
                    [
                        "## 2. Colors",
                        "- Primary ink: `#0a1f44`",
                        "",
                        "Reference screenshot contains `#c0ffee`.",
                        "",
                        "### Deprecated colors",
                        "- Deprecated accent: `#ff00aa`",
                        "",
                        "## 6. Do's And Don'ts",
                        "- Do not use `#bada55`.",
                    ]
                ),
                encoding="utf-8",
            )
            fixture = Path(tmp) / "Hero.css"
            fixture.write_text(
                ".hero { color: #0a1f44; background: #ff00aa; border-color: #bada55; outline-color: #c0ffee; }\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", "--design-md", str(design), str(fixture)],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            messages = {
                finding["message"]
                for finding in json.loads(result.stdout)["findings"]
                if finding["id"] == "untraced-color"
            }
            self.assertEqual(
                messages,
                {
                    "color #ff00aa does not trace to the design token source",
                    "color #bada55 does not trace to the design token source",
                    "color #c0ffee does not trace to the design token source",
                },
            )

    def test_css_color_functions_are_traced_in_extended_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "DESIGN.md"
            design.write_text(
                "\n".join(
                    [
                        "## Color Tokens",
                        "- Canvas: `oklch(96% 0.02 250)`",
                        "- Ink: `rgb(10, 20, 30)`",
                        "- Accent: `hsl(210 80% 45% / 0.8)`",
                    ]
                ),
                encoding="utf-8",
            )
            scss = Path(tmp) / "theme.scss"
            scss.write_text(
                "$canvas: oklch(96% 0.02 250);\n$ink: rgb(10 20 30);\n",
                encoding="utf-8",
            )
            svg = Path(tmp) / "mark.svg"
            svg.write_text(
                '<svg><path fill="hsl(210 80% 45% / 0.8)" stroke="oklch(60% 0.2 20)"/></svg>\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", "--design-md", str(design), tmp],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            untraced = [
                finding
                for finding in json.loads(result.stdout)["findings"]
                if finding["id"] == "untraced-color"
            ]
            self.assertEqual(len(untraced), 1)
            self.assertEqual(untraced[0]["file"], "mark.svg")
            self.assertIn("oklch(60% 0.2 20)", untraced[0]["message"])

    def test_pixel_perfect_extraction_fixture_is_a_valid_token_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "PricingCard.css"
            fixture.write_text(
                "\n".join(
                    [
                        ".card {",
                        "  color: #0e1a2b;",
                        "  background: #ffffff;",
                        "  border-color: #e2e8f0;",
                        "  box-shadow: 0 8px 24px rgba(14, 26, 43, 0.18);",
                        "}",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "node",
                    str(SCANNER),
                    "--json",
                    "--design-md",
                    str(REFERENCE_SPEC),
                    str(fixture),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(
                "untraced-color",
                {finding["id"] for finding in json.loads(result.stdout)["findings"]},
            )

    def test_color_inside_an_explicit_elevation_token_is_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "DESIGN.md"
            design.write_text(
                "## 4. Elevation\n- Raised shadow: `0 8px 24px rgba(14, 26, 43, 0.18)`\n",
                encoding="utf-8",
            )
            fixture = Path(tmp) / "Card.css"
            fixture.write_text(
                ".card { box-shadow: 0 8px 24px rgb(14 26 43 / .18); }\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", "--design-md", str(design), str(fixture)],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(
                "untraced-color",
                {finding["id"] for finding in json.loads(result.stdout)["findings"]},
            )

    def test_design_md_requires_a_nonempty_path(self) -> None:
        for args in (["--design-md"], ["--design-md="], ["--design-md", "--json"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    ["node", str(SCANNER), *args],
                    check=False,
                    text=True,
                    capture_output=True,
                )

                self.assertEqual(result.returncode, 2)
                self.assertIn("--design-md requires a path", result.stderr)

    def test_ignore_for_heuristic_does_not_hide_untraced_color(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "DESIGN.md"
            design.write_text("## 2. Colors\n- Ink: `#0a1f44`\n", encoding="utf-8")
            fixture = Path(tmp) / "Brand.css"
            fixture.write_text(
                ".brand { color: #ff00aa; background: linear-gradient(purple, white); } /* design-tell-ignore: purple-gradient -- approved treatment */\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", "--design-md", str(design), str(fixture)],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            ids = [finding["id"] for finding in json.loads(result.stdout)["findings"]]
            self.assertNotIn("purple-gradient", ids)
            self.assertIn("untraced-color", ids)

    def test_untraced_color_requires_an_explicit_scoped_ignore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "DESIGN.md"
            design.write_text("## 2. Colors\n- Ink: `#0a1f44`\n", encoding="utf-8")
            fixture = Path(tmp) / "Prototype.css"
            fixture.write_text(
                ".prototype { color: #ff00aa; } /* design-tell-ignore: untraced-color -- temporary reviewed prototype */\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", "--design-md", str(design), str(fixture)],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(
                "untraced-color",
                {finding["id"] for finding in json.loads(result.stdout)["findings"]},
            )

    def test_default_blandness_rules_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "Card.tsx"
            fixture.write_text(
                "export const className = 'shadow-md ease-in-out';\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(SCANNER), "--json", tmp],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            ids = {finding["id"] for finding in json.loads(result.stdout)["findings"]}
            self.assertIn("default-shadow", ids)
            self.assertIn("generic-easing", ids)


if __name__ == "__main__":
    unittest.main()
