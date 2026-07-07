from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WRITING_SCANNER = (
    REPO_ROOT / "skills" / "writing-assistant" / "scripts" / "scan-ai-slop-text.py"
)
TERRAFORM_SUMMARIZER = (
    REPO_ROOT
    / "skills"
    / "senior-devops-engineer"
    / "scripts"
    / "summarize-terraform-plan.py"
)
DEVOPS_CONTEXT = (
    REPO_ROOT / "skills" / "senior-devops-engineer" / "scripts" / "devops-context.sh"
)


class WritingScannerTests(unittest.TestCase):
    def run_scanner(self, text: str, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "prose.md"
            fixture.write_text(text, encoding="utf-8")
            return subprocess.run(
                ["python3", str(WRITING_SCANNER), "--json", *args, str(fixture)],
                check=False,
                text=True,
                capture_output=True,
            )

    def test_em_dash_is_contextual_low_severity(self) -> None:
        result = self.run_scanner("She stopped—then opened the door.\n", "--fail-on", "medium")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"][0]["id"], "dash-punctuation")
        self.assertEqual(payload["findings"][0]["severity"], "low")

    def test_ignore_comment_suppresses_intentional_phrase(self) -> None:
        result = self.run_scanner("Transform your workflow. <!-- ai-slop-ignore -->\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["findings"], [])

    def test_assistant_residue_remains_high_severity(self) -> None:
        result = self.run_scanner("As an AI language model, I cannot help.\n", "--fail-on", "high")

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"][0]["id"], "assistant-boilerplate")


class DevOpsHelperTests(unittest.TestCase):
    def test_terraform_summary_reports_destructive_and_sensitive_changes(self) -> None:
        plan = {
            "resource_changes": [
                {
                    "address": "google_sql_database_instance.main",
                    "type": "google_sql_database_instance",
                    "change": {"actions": ["delete", "create"]},
                },
                {
                    "address": "google_project_iam_member.viewer",
                    "type": "google_project_iam_member",
                    "change": {"actions": ["create"]},
                },
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "plan.json"
            fixture.write_text(json.dumps(plan), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(TERRAFORM_SUMMARIZER), "--json", str(fixture)],
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        findings = json.loads(result.stdout)
        self.assertTrue(findings[0]["destructive"])
        self.assertIn("database", findings[0]["risk"])
        self.assertIn("iam", findings[1]["risk"])

    def test_devops_context_is_read_only_and_finds_ci(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github" / "workflows" / "validate.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("name: test\n", encoding="utf-8")
            result = subprocess.run(
                ["bash", str(DEVOPS_CONTEXT), str(root)],
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(".github/workflows/validate.yml", result.stdout)


if __name__ == "__main__":
    unittest.main()
