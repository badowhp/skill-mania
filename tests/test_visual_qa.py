from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VISUAL_QA = REPO_ROOT / "skills" / "visual-qa" / "scripts" / "visual-qa.mjs"
REPORT_POLICY = REPO_ROOT / "skills" / "visual-qa" / "scripts" / "report-policy.mjs"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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

    def test_dry_run_redacts_path_query_values(self) -> None:
        result = subprocess.run(
            [
                "node",
                str(VISUAL_QA),
                "--url",
                "http://localhost:3000",
                "--path",
                "/settings?token=secret-value",
                "--output",
                "/tmp/visual-qa",
                "--dry-run",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("secret-value", result.stdout)
        self.assertEqual(json.loads(result.stdout)["paths"], ["/settings?redacted"])

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
        self.assertIn("same-origin absolute paths", result.stderr)

    def test_rejects_non_http_and_cross_origin_routes(self) -> None:
        for arguments in (
            ["--url", "file:///tmp/demo.html"],
            ["--url", "http://localhost:3000", "--path", "//attacker.example/demo"],
            ["--url", "http://user:pass@localhost:3000"],
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [
                        "node",
                        str(VISUAL_QA),
                        *arguments,
                        "--output",
                        "/tmp/visual-qa",
                        "--dry-run",
                    ],
                    check=False,
                    text=True,
                    capture_output=True,
                )

                self.assertEqual(result.returncode, 2)

    def test_runtime_policy_includes_capture_and_page_errors(self) -> None:
        source = f"""
import {{ shouldFail }} from {json.dumps(REPORT_POLICY.as_uri())};
const reports = [
  {{ pages: [{{ error: "navigation failed", consoleErrors: [], pageErrors: [], failedRequests: [] }}] }},
  {{ pages: [{{ consoleErrors: [], pageErrors: ["uncaught"], failedRequests: [] }}] }},
  {{ pages: [{{ consoleErrors: [], pageErrors: [], failedRequests: [], horizontalOverflow: true }}] }},
  {{ pages: [{{ consoleErrors: [], pageErrors: [], failedRequests: [] }}] }}
];
console.log(JSON.stringify([
  shouldFail(reports[0], "runtime"),
  shouldFail(reports[1], "runtime"),
  shouldFail(reports[2], "runtime"),
  shouldFail(reports[2], "overflow"),
  shouldFail(reports[3], "all")
]));
"""
        result = subprocess.run(
            ["node", "--input-type=module", "--eval", source],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [True, True, False, True, False])

    def test_evidence_redaction_removes_queries_and_common_secrets(self) -> None:
        source = f"""
import {{ redactEvidenceText, sanitizeUrl }} from {json.dumps(REPORT_POLICY.as_uri())};
console.log(JSON.stringify({{
  url: sanitizeUrl("https://user:pass@example.test/path?token=secret#fragment"),
  text: redactEvidenceText("failed https://example.test/api?key=secret Bearer abc123 api_key=xyz")
}}));
"""
        result = subprocess.run(
            ["node", "--input-type=module", "--eval", source],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["url"], "https://example.test/path?redacted")
        self.assertNotIn("secret", payload["text"])
        self.assertNotIn("abc123", payload["text"])
        self.assertNotIn("xyz", payload["text"])

    def test_capture_writes_separate_keyboard_focus_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "evidence"
            write(
                root / "node_modules" / "playwright" / "index.js",
                """const fs = require("node:fs");

function makePage() {
  let pressed = false;
  let evaluations = 0;
  return {
    on() {},
    keyboard: {
      async press(key) {
        if (key !== "Tab") throw new Error("expected Tab");
        pressed = true;
      }
    },
    async goto() {},
    async screenshot({ path }) {
      if (path.endsWith("-focus.png") && !pressed) {
        throw new Error("focus screenshot captured before keyboard step");
      }
      fs.writeFileSync(path, "mock image");
    },
    async evaluate() {
      evaluations += 1;
      if (evaluations === 1) {
        return { title: "Demo", hasPrimaryContent: true, horizontalOverflow: false };
      }
      if (!pressed) throw new Error("focus inspected before keyboard step");
      return { tag: "button", visible: true };
    }
  };
}

module.exports = {
  chromium: {
    async launch() {
      return {
        async newContext() {
          return {
            async newPage() { return makePage(); },
            async close() {}
          };
        },
        async close() {}
      };
    }
  }
};
""",
            )
            result = subprocess.run(
                [
                    "node",
                    str(VISUAL_QA),
                    "--url",
                    "http://localhost:3000",
                    "--output",
                    str(output),
                    "--json",
                ],
                cwd=root,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(len(report["pages"]), 2)
            for page in report["pages"]:
                self.assertTrue((output / page["screenshot"]).is_file())
                self.assertTrue((output / page["focusScreenshot"]).is_file())
                self.assertEqual(page["focusedElement"], {"tag": "button", "visible": True})


if __name__ == "__main__":
    unittest.main()
