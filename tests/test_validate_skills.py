from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills", VALIDATOR_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ValidateSkillsTests(unittest.TestCase):
    def test_frontmatter_rejects_nonportable_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_file = Path(tmp) / "demo" / "SKILL.md"
            write(
                skill_file,
                """---
name: demo
description: Demo skill.
version: 1.0.0
---

# Demo
""",
            )

            with self.assertRaises(ValueError) as ctx:
                validator.parse_frontmatter(skill_file)

            self.assertIn("unsupported frontmatter key", str(ctx.exception))

    def test_reference_routing_requires_markdown_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo"
            write(
                skill_dir / "SKILL.md",
                """---
name: demo
description: Demo skill.
---

# Demo

See references/details.md.
""",
            )
            write(skill_dir / "references" / "details.md", "# Details\n")

            errors = validator.validate_skill(skill_dir)

            self.assertIn(
                "reference 'references/details.md' is not linked from SKILL.md as a Markdown link",
                errors,
            )

    def test_links_cannot_escape_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo"
            write(
                skill_dir / "SKILL.md",
                """---
name: demo
description: Demo skill.
---

# Demo

[escape](../outside.md)
""",
            )

            errors = validator.validate_skill(skill_dir)

            self.assertTrue(
                any("relative link escapes skill directory" in error for error in errors),
                errors,
            )

    def test_openai_metadata_requires_prompt_skill_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            metadata_file = Path(tmp) / "openai.yaml"
            write(
                metadata_file,
                """interface:
  display_name: "Demo"
  short_description: "A valid short description"
  default_prompt: "Use this skill for demo work."
""",
            )

            errors = validator.validate_openai_yaml(metadata_file, "demo")

            self.assertIn("interface.default_prompt must include $demo", errors)

    def test_skill_root_flags_stray_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            (root / "stray").mkdir(parents=True)

            errors = validator.validate_skill_root(root)

            self.assertEqual(
                errors,
                [f"{root}: unexpected directory without SKILL.md: stray"],
            )

    def test_string_list_requires_non_empty_strings(self) -> None:
        errors = validator.require_string_list({"items": ["ok", ""]}, "items", Path("file.json"))

        self.assertEqual(
            errors,
            ["file.json: items must contain only non-empty strings"],
        )

    def test_repo_relative_path_cannot_escape_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            base_dir = repo_root / "plugins"
            base_dir.mkdir(parents=True)
            manifest = base_dir / "plugin.json"

            errors = validator.validate_repo_relative_path(
                repo_root,
                base_dir,
                manifest,
                "../../outside",
                "source",
            )

            self.assertEqual(
                errors,
                [f"{manifest}: source must not escape repository"],
            )

    def test_production_skill_requires_evals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo"
            skill_dir.mkdir(parents=True)

            errors = validator.validate_skill_evals(skill_dir)

            self.assertEqual(errors, ["evals/evals.json is required for production skills"])

    def test_eval_exempt_skill_does_not_require_evals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "hip0-mania"
            skill_dir.mkdir(parents=True)

            errors = validator.validate_skill_evals(skill_dir)

            self.assertEqual(errors, [])

    def test_eval_schema_requires_positive_and_near_miss_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo"
            write(
                skill_dir / "evals" / "evals.json",
                """{
  "skill_name": "demo",
  "evals": [
    {
      "id": "one",
      "prompt": "This prompt is long enough to be descriptive.",
      "expected_output": "This expected output is also descriptive enough.",
      "should_trigger": true
    },
    {
      "id": "two",
      "prompt": "This second prompt is long enough to be descriptive.",
      "expected_output": "This second expected output is descriptive enough.",
      "should_trigger": true
    },
    {
      "id": "three",
      "prompt": "This third prompt is long enough to be descriptive.",
      "expected_output": "This third expected output is descriptive enough.",
      "should_trigger": true
    }
  ]
}
""",
            )

            errors = validator.validate_skill_evals(skill_dir)

            self.assertIn(
                "evals/evals.json: include at least 1 should_trigger=false near-miss case",
                errors,
            )

    def test_readme_references_reject_deprecated_openai_skills_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write(
                repo_root / "README.md",
                "https://github.com/openai/skills\n"
                "https://developers.openai.com/codex/skills\n"
                "https://developers.openai.com/codex/plugins/build\n"
                "https://github.com/openai/plugins\n",
            )

            errors = validator.validate_readme_references(repo_root)

            self.assertEqual(
                errors,
                [
                    f"{repo_root / 'README.md'}: replace deprecated openai/skills links with current Codex plugin docs"
                ],
            )

    def test_plugin_versions_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write(
                repo_root / "plugins" / "skill-mania" / ".codex-plugin" / "plugin.json",
                '{"version":"1.0.0"}',
            )
            write(
                repo_root / "plugins" / "skill-mania" / ".claude-plugin" / "plugin.json",
                '{"version":"1.0.1"}',
            )

            errors = validator.validate_plugin_versions_match(repo_root)

            self.assertEqual(len(errors), 1)
            self.assertIn("plugin versions must match", errors[0])


if __name__ == "__main__":
    unittest.main()
