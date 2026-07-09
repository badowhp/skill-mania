from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


budgets = load_module("report_skill_budgets", REPO_ROOT / "scripts" / "report-skill-budgets.py")
links = load_module("check_external_links", REPO_ROOT / "scripts" / "check-external-links.py")
eval_summary = load_module(
    "summarize_eval_workspace", REPO_ROOT / "scripts" / "summarize-eval-workspace.py"
)


class SkillBudgetTests(unittest.TestCase):
    def test_current_skills_fit_context_budgets(self) -> None:
        report = budgets.collect(REPO_ROOT / "skills")

        self.assertEqual(budgets.failures(report), [])
        self.assertTrue(report["startup"]["within_budget"])
        self.assertEqual(len(report["skills"]), 13)

    def test_oversized_skill_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo.\n---\n" + ("x" * 18000),
                encoding="utf-8",
            )

            report = budgets.collect(Path(tmp))

        self.assertIn("exceeds the SKILL.md budget", budgets.failures(report)[0])


class ExternalLinkTests(unittest.TestCase):
    def test_collect_links_strips_sentence_punctuation_and_skips_localhost(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "See https://example.com/docs. Local http://localhost:4000/health.\n"
                "```bash\ncurl https://example.com/api\n```\n",
                encoding="utf-8",
            )

            result = links.collect_links(root)

        self.assertEqual(list(result), ["https://example.com/docs"])


class ReleaseVersionTests(unittest.TestCase):
    def test_current_release_versions_match(self) -> None:
        result = subprocess.run(
            ["python3", str(REPO_ROOT / "scripts" / "check-release-version.py")],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class EvalWorkspaceTests(unittest.TestCase):
    def test_paired_runs_are_aggregated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = root / "eval-authz"
            for name, passed, tokens, duration in (
                ("with_skill", 2, 1200, 900),
                ("without_skill", 1, 800, 600),
            ):
                run = case / name
                run.mkdir(parents=True)
                (run / "grading.json").write_text(
                    json.dumps({"summary": {"passed": passed, "total": 2}}),
                    encoding="utf-8",
                )
                (run / "timing.json").write_text(
                    json.dumps({"total_tokens": tokens, "duration_ms": duration}),
                    encoding="utf-8",
                )

            report = eval_summary.summarize(root)

        self.assertEqual(report["summary"]["pass_rate_delta"], 0.5)
        self.assertEqual(report["summary"]["median_token_delta"], 400)
        self.assertEqual(report["summary"]["median_duration_delta_ms"], 300)


if __name__ == "__main__":
    unittest.main()
