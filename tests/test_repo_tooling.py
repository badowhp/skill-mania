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
validator = load_module("validate_skills", REPO_ROOT / "scripts" / "validate-skills.py")
routing = load_module("validate_routing_evals", REPO_ROOT / "scripts" / "validate-routing-evals.py")


class SkillBudgetTests(unittest.TestCase):
    def test_current_skills_fit_context_budgets(self) -> None:
        report = budgets.collect(REPO_ROOT / "skills")

        self.assertEqual(budgets.failures(report), [])
        self.assertTrue(report["startup"]["within_budget"])
        self.assertEqual(len(report["skills"]), 18)

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

    def test_oversized_nested_references_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo"
            reference = skill / "references" / "nested"
            reference.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo.\n---\n",
                encoding="utf-8",
            )
            (reference / "large.md").write_text("x" * 50001, encoding="utf-8")

            report = budgets.collect(Path(tmp))

        self.assertIn("references exceed the total reference budget", budgets.failures(report)[0])


class RtkGuidanceTests(unittest.TestCase):
    def test_current_skills_include_rtk_guidance(self) -> None:
        for skill_file in REPO_ROOT.glob("skills/*/SKILL.md"):
            lines = skill_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(validator.validate_rtk_guidance(lines), [], skill_file)

    def test_missing_rtk_guidance_is_reported(self) -> None:
        self.assertEqual(
            validator.validate_rtk_guidance(["# Demo"]),
            ["include optional RTK guidance for noisy, non-destructive command output"],
        )


class ExternalLinkTests(unittest.TestCase):
    def test_collect_links_strips_sentence_punctuation_and_skips_localhost(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "See https://example.com/docs. Local http://localhost:4000/health.\n"
                "Bot-protected https://www.pmi.org/standards/pmbok.\n"
                "Do not skip the lookalike https://www.pmi.org.example/standards.\n"
                "```bash\ncurl https://example.com/api\n```\n",
                encoding="utf-8",
            )

            result = links.collect_links(root)

        self.assertEqual(
            list(result),
            ["https://example.com/docs", "https://www.pmi.org.example/standards"],
        )


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


class RoutingEvalTests(unittest.TestCase):
    def test_current_routing_matrix_covers_the_skill_inventory(self) -> None:
        matrix, errors = routing.load_matrix(REPO_ROOT / "evals" / "routing-matrix.json")

        self.assertEqual(errors, [])
        assert matrix is not None
        self.assertEqual(
            routing.validate_matrix(matrix, routing.skill_names(REPO_ROOT / "skills")),
            [],
        )

    def test_unknown_routing_skill_is_rejected(self) -> None:
        data = {
            "cases": [
                {
                    "id": "bad-case",
                    "prompt": "This is a sufficiently descriptive routing prompt.",
                    "lead_skill": "missing-skill",
                    "near_miss_skills": ["senior-developer"],
                    "why": "This must be rejected because the lead does not exist.",
                }
            ]
        }

        errors = routing.validate_matrix(data, {"senior-developer"})

        self.assertIn("lead_skill must name a production skill", errors[0])

    def test_overlay_cannot_own_a_domain_routing_case(self) -> None:
        data = {
            "cases": [
                {
                    "id": "overlay-as-lead",
                    "prompt": "Use the smallest correct implementation for this application bug.",
                    "lead_skill": "ponytail",
                    "near_miss_skills": ["senior-developer"],
                    "why": "This deliberately invalid case verifies the overlay routing boundary.",
                }
            ]
        }

        errors = routing.validate_matrix(data, {"ponytail", "senior-developer"})

        self.assertTrue(
            any("lead_skill must name a domain skill" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
