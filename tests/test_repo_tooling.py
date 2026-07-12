from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


budgets = load_module("report_skill_budgets", REPO_ROOT / "scripts" / "report-skill-budgets.py")
links = load_module("check_external_links", REPO_ROOT / "scripts" / "check-external-links.py")
eval_summary = load_module(
    "summarize_eval_workspace", REPO_ROOT / "scripts" / "summarize-eval-workspace.py"
)
validator = load_module("validate_skills", REPO_ROOT / "scripts" / "validate-skills.py")
routing = load_module("validate_routing_evals", REPO_ROOT / "scripts" / "validate-routing-evals.py")
model_matrix = load_module("validate_model_matrix", REPO_ROOT / "scripts" / "validate-model-matrix.py")
helper_syntax = load_module("check_helper_syntax", REPO_ROOT / "scripts" / "check-helper-syntax.py")
secret_patterns = load_module("check_secret_patterns", REPO_ROOT / "scripts" / "check-secret-patterns.py")
workflow_security = load_module(
    "check_workflow_security", REPO_ROOT / "scripts" / "check-workflow-security.py"
)
skill_evals = load_module("run_skill_evals", REPO_ROOT / "scripts" / "run-skill-evals.py")
benchmark_compare = load_module(
    "compare_skill_benchmarks", REPO_ROOT / "scripts" / "compare-skill-benchmarks.py"
)
install_profiles = load_module(
    "list_profile_skills", REPO_ROOT / "scripts" / "list-profile-skills.py"
)


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

    def test_release_content_has_a_version_newer_than_the_latest_tag(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "scripts" / "check-release-version.py"),
                "--require-bump",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class StaticSafetyTests(unittest.TestCase):
    def test_current_helpers_have_valid_syntax(self) -> None:
        self.assertEqual(helper_syntax.check(REPO_ROOT), [])

    def test_current_workflows_pin_actions_and_declare_permissions(self) -> None:
        for workflow in (REPO_ROOT / ".github" / "workflows").glob("*.yml"):
            self.assertEqual(workflow_security.validate(workflow), [], workflow)

    def test_full_model_gate_has_fixed_release_comparison_settings(self) -> None:
        workflow = (
            REPO_ROOT / ".github" / "workflows" / "skill-regression-gate.yml"
        ).read_text(encoding="utf-8")

        self.assertNotIn("inputs:", workflow)
        for marker in (
            "--skills all",
            "--model-route balanced",
            "--judge-route quality",
            "--routing-route throughput",
            "--max-cases-per-skill 0",
            "--baseline-commit",
        ):
            self.assertIn(marker, workflow)

    def test_unpinned_action_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / "bad.yml"
            workflow.write_text(
                "name: Bad\non: push\npermissions:\n  contents: read\njobs:\n"
                "  test:\n    steps:\n      - uses: actions/checkout@v4\n",
                encoding="utf-8",
            )

            errors = workflow_security.validate(workflow)

        self.assertTrue(any("full commit SHA" in error for error in errors), errors)
        self.assertTrue(any("must not persist" in error for error in errors), errors)

    def test_pull_request_secret_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / "bad.yml"
            workflow.write_text(
                "name: Bad\non:\n  pull_request:\npermissions:\n  contents: read\n"
                "jobs:\n  test:\n    steps:\n      - run: tool\n"
                "        env:\n          TOKEN: ${{ secrets.DEPLOY_TOKEN }}\n",
                encoding="utf-8",
            )

            errors = workflow_security.validate(workflow)

        self.assertTrue(any("must not reference" in error for error in errors), errors)

    def test_manual_secret_workflow_requires_default_branch_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / "bad.yml"
            workflow.write_text(
                "name: Bad\non:\n  workflow_dispatch:\npermissions:\n  contents: read\n"
                "jobs:\n  test:\n    steps:\n      - run: tool\n"
                "        env:\n          TOKEN: ${{ secrets.MODEL_TOKEN }}\n",
                encoding="utf-8",
            )

            errors = workflow_security.validate(workflow)

        self.assertTrue(any("default-branch job guard" in error for error in errors), errors)
        self.assertTrue(any("default-branch checkout" in error for error in errors), errors)
        self.assertTrue(any("evaluation environment" in error for error in errors), errors)

    def test_secret_scanner_detects_high_confidence_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.txt").write_text("key=" + "sk-" + ("A" * 32), encoding="utf-8")

            findings = secret_patterns.scan(root)

        self.assertEqual(len(findings), 1)
        self.assertIn("OpenAI API key", findings[0])

    def test_secret_scanner_rejects_non_template_env_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.production").write_text("DEBUG=false\n", encoding="utf-8")
            (root / ".env.example").write_text("API_KEY=\n", encoding="utf-8")

            findings = secret_patterns.scan(root)

        self.assertEqual(findings, [".env.production: tracked .env-style file"])

    def test_non_release_workflow_cannot_request_write_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / "validate.yml"
            workflow.write_text(
                "name: Bad\non: push\npermissions:\n  contents: write\njobs:\n"
                "  test:\n    steps:\n      - run: true\n",
                encoding="utf-8",
            )

            errors = workflow_security.validate(workflow)

        self.assertIn("contents: write is reserved for release.yml", errors)


class InstallerTests(unittest.TestCase):
    def test_profiles_partition_the_current_inventory(self) -> None:
        profiles = install_profiles.load_profiles(
            REPO_ROOT / "config" / "install-profiles.json"
        )

        self.assertEqual(
            install_profiles.validate_inventory(profiles, REPO_ROOT / "skills"), []
        )

    def test_content_profile_installs_only_content_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            env = {**os.environ, "AGENT_SKILLS_DIR": str(target)}
            result = subprocess.run(
                [
                    str(REPO_ROOT / "scripts" / "install-local.sh"),
                    "--agents",
                    "--copy",
                    "--profile",
                    "content",
                    "--no-validate",
                ],
                env=env,
                check=False,
                text=True,
                capture_output=True,
            )

            installed = sorted(path.name for path in target.iterdir())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(installed, ["seo-geo", "writing-assistant"])

    def test_old_claude_requires_copy_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            fake_claude = bin_dir / "claude"
            fake_claude.write_text(
                "#!/usr/bin/env bash\nprintf '%s\\n' '2.1.197 (Claude Code)'\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            env = {
                **os.environ,
                "PATH": f"{bin_dir}:{os.environ['PATH']}",
                "CLAUDE_SKILLS_DIR": str(root / "skills"),
            }
            result = subprocess.run(
                [
                    str(REPO_ROOT / "scripts" / "install-local.sh"),
                    "--claude",
                    "--link",
                    "--no-validate",
                ],
                env=env,
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("does not support symlinked skills", result.stderr)


class ModelMatrixTests(unittest.TestCase):
    def test_current_model_matrix_is_reviewed_and_valid(self) -> None:
        data = json.loads((REPO_ROOT / "evals" / "model-matrix.json").read_text())

        self.assertEqual(model_matrix.validate(data, dt.date(2026, 7, 12)), [])
        self.assertEqual(data["evaluation"]["routing_route"], "throughput")

    def test_expired_model_matrix_is_rejected(self) -> None:
        data = json.loads((REPO_ROOT / "evals" / "model-matrix.json").read_text())

        errors = model_matrix.validate(data, dt.date(2026, 9, 13))

        self.assertTrue(any("review expired" in error for error in errors), errors)


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


class ModelEvalRunnerTests(unittest.TestCase):
    def test_model_endpoint_rejects_credential_exfiltration_hosts(self) -> None:
        self.assertEqual(
            skill_evals.validate_base_url("https://api.openai.com/v1"),
            "https://api.openai.com/v1",
        )
        with self.assertRaisesRegex(ValueError, "must use HTTPS"):
            skill_evals.validate_base_url("https://attacker.example/v1")

    def test_output_text_is_extracted_from_response_items(self) -> None:
        response = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": "first"},
                        {"type": "output_text", "text": "second"},
                    ],
                }
            ]
        }

        self.assertEqual(skill_evals.extract_output_text(response), "first\nsecond")

    def test_responses_client_sends_safe_non_stored_request(self) -> None:
        received: dict[str, object] = {}

        payload = {
            "id": "resp_test",
            "model": "gpt-test",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "ok"}],
                }
            ],
            "usage": {
                "input_tokens": 10,
                "input_tokens_details": {"cached_tokens": 2},
                "output_tokens": 4,
                "output_tokens_details": {"reasoning_tokens": 1},
                "total_tokens": 14,
            },
        }

        class Response:
            def __enter__(self) -> "Response":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps(payload).encode()

        def fake_urlopen(request, timeout):  # type: ignore[no-untyped-def]
            received["url"] = request.full_url
            received["authorization"] = request.headers["Authorization"]
            received["body"] = json.loads(request.data)
            return Response()

        with patch.object(skill_evals.urllib.request, "urlopen", side_effect=fake_urlopen):
            client = skill_evals.OpenAIResponsesClient("test-key", retries=0)
            result = client.call(
                model="gpt-test",
                reasoning_effort="low",
                instructions="instructions",
                input_text="task",
                max_output_tokens=100,
            )

        self.assertEqual(result.output, "ok")
        self.assertEqual(result.cache_write_tokens, 0)
        self.assertEqual(received["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(received["authorization"], "Bearer test-key")
        body = received["body"]
        assert isinstance(body, dict)
        self.assertFalse(body["store"])
        self.assertEqual(body["reasoning"], {"effort": "low"})

        with patch.object(skill_evals.urllib.request, "urlopen", side_effect=fake_urlopen):
            budgeted = skill_evals.OpenAIResponsesClient(
                "test-key", retries=0, maximum_total_tokens=13
            )
            with self.assertRaisesRegex(RuntimeError, "token budget exceeded"):
                budgeted.call(
                    model="gpt-test",
                    reasoning_effort="low",
                    instructions="instructions",
                    input_text="task",
                    max_output_tokens=100,
                )

        self.assertEqual(budgeted.calls_completed, 1)
        self.assertEqual(budgeted.requests_attempted, 1)
        self.assertEqual(budgeted.total_tokens_used, 14)

    def test_codex_jsonl_usage_is_parsed(self) -> None:
        thread_id, usage = skill_evals.parse_codex_jsonl(
            '{"type":"thread.started","thread_id":"thread-1"}\n'
            '{"type":"turn.completed","usage":{"input_tokens":10,'
            '"cached_input_tokens":2,"output_tokens":4,"reasoning_output_tokens":1}}\n'
        )

        self.assertEqual(thread_id, "thread-1")
        self.assertEqual(usage["input_tokens"], 10)
        self.assertEqual(usage["reasoning_output_tokens"], 1)

    def test_codex_client_uses_isolated_ephemeral_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth_home = Path(tmp) / "source-home"
            auth_home.mkdir()
            (auth_home / "auth.json").write_text("{}", encoding="utf-8")
            with patch.object(skill_evals.shutil, "which", return_value="/usr/bin/codex"):
                client = skill_evals.CodexExecClient(
                    codex_bin="codex",
                    auth_home=auth_home,
                    maximum_total_tokens=100,
                    maximum_api_requests=1,
                )
            received: dict[str, object] = {}

            def fake_run(command, **kwargs):  # type: ignore[no-untyped-def]
                received["command"] = command
                received["environment"] = kwargs["env"]
                received["prompt"] = kwargs["input"]
                output = Path(command[command.index("--output-last-message") + 1])
                output.write_text('{"result":"ok"}', encoding="utf-8")
                schema = Path(command[command.index("--output-schema") + 1])
                received["schema"] = json.loads(schema.read_text(encoding="utf-8"))
                stdout = (
                    '{"type":"thread.started","thread_id":"thread-1"}\n'
                    '{"type":"turn.completed","usage":{"input_tokens":10,'
                    '"cached_input_tokens":2,"output_tokens":4,'
                    '"reasoning_output_tokens":1}}\n'
                )
                return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

            try:
                with patch.object(skill_evals.subprocess, "run", side_effect=fake_run):
                    result = client.call(
                        model="gpt-test",
                        reasoning_effort="low",
                        instructions="instructions",
                        input_text="task",
                        max_output_tokens=100,
                        schema_name="result",
                        schema={"type": "object"},
                    )
            finally:
                client.close()

        command = received["command"]
        assert isinstance(command, list)
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn("read-only", command)
        environment = received["environment"]
        assert isinstance(environment, dict)
        self.assertNotEqual(environment["CODEX_HOME"], str(auth_home))
        self.assertIn("Do not use\ntools", received["prompt"])
        self.assertEqual(received["schema"], {"type": "object"})
        self.assertEqual(result.total_tokens, 14)
        self.assertEqual(result.response_id, "thread-1")

    def test_blind_grade_is_mapped_back_to_runs(self) -> None:
        raw = {
            "results": [
                {
                    "assertion_index": 0,
                    "candidate_a_passed": True,
                    "candidate_a_evidence": "A evidence",
                    "candidate_b_passed": False,
                    "candidate_b_evidence": "B evidence",
                }
            ]
        }

        result = skill_evals.normalize_grade(
            raw,
            ["Observable assertion"],
            {"a": "with_skill", "b": "baseline"},
        )

        self.assertTrue(result["with_skill"][0]["passed"])
        self.assertFalse(result["baseline"][0]["passed"])

    def test_generation_order_is_deterministic_and_paired(self) -> None:
        first = skill_evals.paired_generation_order("commit", "focused-local-commit")
        second = skill_evals.paired_generation_order("commit", "focused-local-commit")

        self.assertEqual(first, second)
        self.assertEqual(set(first), {"baseline", "with_skill"})

    def test_routing_schema_uses_supported_strict_json_subset(self) -> None:
        schema = skill_evals.routing_schema(["commit"], ["caveman"])

        self.assertNotIn("uniqueItems", json.dumps(schema))

    def test_skill_package_includes_text_resources_and_skips_binary_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo"
            (skill / "references").mkdir(parents=True)
            (skill / "scripts").mkdir()
            (skill / "assets").mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo skill.\n---\n# Demo\nUse the resources.\n",
                encoding="utf-8",
            )
            (skill / "references" / "policy.md").write_text("Policy text.\n", encoding="utf-8")
            (skill / "scripts" / "check.py").write_text("print('ok')\n", encoding="utf-8")
            (skill / "assets" / "image.png").write_bytes(b"\x00binary")

            package = skill_evals.load_skill_package(skill)

        self.assertIn("Policy text.", package.instructions)
        self.assertIn("print('ok')", package.instructions)
        self.assertIn("references/policy.md", package.included_files)
        self.assertIn("assets/image.png", package.skipped_files)
        self.assertEqual(len(package.sha256), 64)

    def test_skill_package_rejects_symlinked_resources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "demo"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo skill.\n---\n# Demo\n",
                encoding="utf-8",
            )
            outside = root / "credentials.txt"
            outside.write_text("private material\n", encoding="utf-8")
            link = skill / "references" / "credentials.txt"
            link.symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "symlinked evaluation input"):
                skill_evals.load_skill_package(skill)

    def test_artifact_component_rejects_path_traversal(self) -> None:
        with self.assertRaisesRegex(ValueError, "lowercase hyphenated"):
            skill_evals.safe_artifact_component("../../outside", "evaluation case id")

    def test_skill_verdict_separates_lift_from_regression(self) -> None:
        lift = skill_evals.skill_verdict(2, 1, 2, 0.8, 0.05)
        regression = skill_evals.skill_verdict(1, 2, 2, 0.4, 0.05)

        self.assertEqual(lift["verdict"], "measurable-lift")
        self.assertEqual(regression["verdict"], "regressed")
        self.assertFalse(regression["gate_passed"])

    def test_routing_grades_near_misses_and_per_skill_trigger_boundaries(self) -> None:
        cross_cases = [
            {
                "id": "commit-vs-code",
                "lead_skill": "commit",
                "near_miss_skills": ["senior-developer"],
            }
        ]
        cross = skill_evals.grade_cross_skill_routing(
            cross_cases,
            [
                {
                    "id": "commit-vs-code",
                    "lead_skill": "commit",
                    "overlay_skills": [],
                    "reason": "Local commit requested.",
                }
            ],
            ["commit", "senior-developer"],
        )
        trigger_cases = [
            {
                "key": "commit:positive",
                "skill": "commit",
                "case": "positive",
                "should_trigger": True,
            },
            {
                "key": "commit:negative",
                "skill": "commit",
                "case": "negative",
                "should_trigger": False,
            },
        ]
        triggers = skill_evals.grade_trigger_routing(
            trigger_cases,
            [
                {"key": "commit:positive", "should_trigger": True, "reason": "yes"},
                {"key": "commit:negative", "should_trigger": False, "reason": "no"},
            ],
            ["commit"],
        )
        report = {
            "cross_skill": cross,
            "triggers": triggers,
            "summary": {"accuracy": 1.0},
        }

        self.assertEqual(cross["by_skill"]["senior-developer"]["total"], 1)
        self.assertEqual(triggers["by_skill"]["commit"]["positive_recall"], 1.0)
        self.assertEqual(triggers["by_skill"]["commit"]["negative_specificity"], 1.0)
        self.assertTrue(skill_evals.routing_gate_passed(report, 0.85))

    def test_routing_gate_cannot_hide_one_failed_skill_in_global_accuracy(self) -> None:
        report = {
            "summary": {"accuracy": 0.95},
            "cross_skill": {
                "by_skill": {
                    "commit": {"total": 2, "accuracy": 1.0},
                    "senior-developer": {"total": 1, "accuracy": 0.0},
                }
            },
            "triggers": {
                "by_skill": {
                    "commit": {
                        "positive_total": 1,
                        "negative_total": 1,
                        "positive_recall": 1.0,
                        "negative_specificity": 1.0,
                    },
                    "senior-developer": {
                        "positive_total": 1,
                        "negative_total": 1,
                        "positive_recall": 1.0,
                        "negative_specificity": 1.0,
                    },
                }
            },
        }

        self.assertFalse(skill_evals.routing_gate_passed(report, 0.85))

    def test_dry_run_covers_every_skill_without_an_api_key(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "scripts" / "run-skill-evals.py"),
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            env={key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"},
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(len(plan["skills"]), 18)
        self.assertEqual(plan["output_cases"], 18)
        self.assertEqual(plan["estimated_model_calls"], 56)
        self.assertEqual(plan["routing_model"], "gpt-5.6-luna")
        self.assertEqual(plan["maximum_api_requests"], 600)
        self.assertEqual(plan["provider"], "codex-cli")
        self.assertEqual(plan["baseline"]["kind"], "without_skill")
        self.assertFalse(plan["tool_execution"])

    def test_benchmark_comparison_reports_quality_regression(self) -> None:
        base_config = {
            "provider": "codex-cli",
            "model": "generator",
            "reasoning_effort": "medium",
            "judge_model": "judge",
            "judge_reasoning_effort": "high",
            "routing_model": "router",
            "routing_reasoning_effort": "low",
            "case_offset": 0,
            "context_mode": "bundled-context",
            "baseline": {"kind": "without_skill", "label": "without-skill"},
        }
        baseline = {
            "configuration": base_config,
            "cases": [{"skill": "commit", "case": "focused"}],
            "skills": {
                "commit": {
                    "with_skill_pass_rate": 1.0,
                    "baseline_pass_rate": 0.5,
                    "token_delta": 10,
                    "duration_delta_ms": 20,
                    "verdict": "measurable-lift",
                    "gate_passed": True,
                }
            },
            "output_summary": {"with_skill_pass_rate": 1.0},
            "routing": {"summary": {"accuracy": 1.0}},
            "gate": {"passed": True},
        }
        current = json.loads(json.dumps(baseline))
        current["skills"]["commit"]["with_skill_pass_rate"] = 0.5
        current["skills"]["commit"]["verdict"] = "below-quality-bar"
        current["skills"]["commit"]["gate_passed"] = False
        current["output_summary"]["with_skill_pass_rate"] = 0.5
        current["gate"]["passed"] = False

        comparison = benchmark_compare.compare_reports(baseline, current)

        self.assertTrue(comparison["comparable"])
        self.assertEqual(
            comparison["skills"]["commit"]["with_skill_pass_rate_delta"], -0.5
        )
        self.assertIn("commit", comparison["regressions"])
        self.assertIn("overall-gate", comparison["regressions"])

    def test_model_call_cap_rejects_an_accidental_full_run(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "scripts" / "run-skill-evals.py"),
                "--dry-run",
                "--max-cases-per-skill",
                "0",
                "--maximum-model-calls",
                "1",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("above the cap", result.stderr)


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
