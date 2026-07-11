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

    def test_frontmatter_rejects_unquoted_colon_space_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_file = Path(tmp) / "demo" / "SKILL.md"
            write(
                skill_file,
                """---
name: demo
description: Demo skill: invalid for portable YAML.
---

# Demo
""",
            )

            with self.assertRaises(ValueError) as ctx:
                validator.parse_frontmatter(skill_file)

            self.assertIn("quote frontmatter values containing colon-space", str(ctx.exception))

    def test_frontmatter_accepts_standard_optional_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_file = Path(tmp) / "demo" / "SKILL.md"
            write(
                skill_file,
                """---
name: demo
description: Demo skill.
license: MIT
compatibility: Requires git.
allowed-tools: "Bash(git:*) Read"
metadata:
  owner: platform
  maturity: stable
---

# Demo
""",
            )

            frontmatter, _ = validator.parse_frontmatter(skill_file)

            self.assertEqual(frontmatter["license"], "MIT")
            self.assertEqual(frontmatter["allowed-tools"], "Bash(git:*) Read")
            self.assertEqual(frontmatter["metadata"], {"owner": "platform", "maturity": "stable"})

    def test_frontmatter_rejects_empty_allowed_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo"
            write(
                skill_dir / "SKILL.md",
                """---
name: demo
description: Demo skill.
allowed-tools:
---

# Demo
""",
            )

            errors = validator.validate_skill(skill_dir)

            self.assertIn("frontmatter.allowed-tools must be a non-empty string", errors)

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

    def test_openai_metadata_accepts_policy_and_tool_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo"
            metadata_file = skill_dir / "agents" / "openai.yaml"
            write(
                metadata_file,
                """interface:
  display_name: "Demo"
  short_description: "A valid short description"
  default_prompt: "Use $demo for this task."
policy:
  allow_implicit_invocation: false
dependencies:
  tools:
    - type: "mcp"
      value: "docs"
      description: "Documentation server"
""",
            )

            errors = validator.validate_openai_yaml(metadata_file, "demo")

            self.assertEqual(errors, [])

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

    def test_plugin_component_path_requires_dot_slash_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            base_dir = repo_root / "plugins"
            base_dir.mkdir(parents=True)
            manifest = base_dir / "plugin.json"

            errors = validator.validate_repo_relative_path(
                repo_root,
                base_dir,
                manifest,
                "skills",
                "skills",
                require_dot_slash=True,
            )

            self.assertEqual(
                errors,
                [f"{manifest}: skills must start with './'"],
            )

    def test_production_skill_requires_evals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo"
            skill_dir.mkdir(parents=True)

            errors = validator.validate_skill_evals(skill_dir)

            self.assertEqual(errors, ["evals/evals.json is required for production skills"])

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
      "should_trigger": true,
      "assertions": ["The first behavior is present", "The first output is valid"]
    },
    {
      "id": "two",
      "prompt": "This second prompt is long enough to be descriptive.",
      "expected_output": "This second expected output is descriptive enough.",
      "should_trigger": true,
      "assertions": ["The second behavior is present", "The second output is valid"]
    },
    {
      "id": "three",
      "prompt": "This third prompt is long enough to be descriptive.",
      "expected_output": "This third expected output is descriptive enough.",
      "should_trigger": true,
      "assertions": ["The third behavior is present", "The third output is valid"]
    },
    {
      "id": "four",
      "prompt": "This fourth prompt is long enough to be descriptive.",
      "expected_output": "This fourth expected output is descriptive enough.",
      "should_trigger": true,
      "assertions": ["The fourth behavior is present", "The fourth output is valid"]
    },
    {
      "id": "five",
      "prompt": "This near miss prompt is long enough to be descriptive.",
      "expected_output": "This near miss should not trigger the skill at all.",
      "should_trigger": false
    }
  ]
}
""",
            )

            errors = validator.validate_skill_evals(skill_dir)

            self.assertIn(
                "evals/evals.json: include at least 2 should_trigger=false near-miss cases",
                errors,
            )

    def test_honest_opinion_block_is_required_for_production_skills(self) -> None:
        errors = validator.validate_honest_opinion(Path("demo"), ["# Demo"])

        self.assertEqual(
            errors,
            ["standard ## Honest Opinion block is required for production skills"],
        )

    def test_caveman_requires_honest_opinion_block(self) -> None:
        errors = validator.validate_honest_opinion(Path("caveman"), ["# Caveman"])

        self.assertEqual(
            errors,
            ["standard ## Honest Opinion block is required for production skills"],
        )

    def test_standard_honest_opinion_block_is_accepted(self) -> None:
        errors = validator.validate_honest_opinion(
            Path("demo"), validator.HONEST_OPINION_BLOCK.splitlines()
        )

        self.assertEqual(errors, [])

    def test_readme_references_reject_deprecated_openai_skills_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            write(
                repo_root / "README.md",
                "https://github.com/openai/skills\n"
                "https://developers.openai.com/codex/skills\n"
                "https://developers.openai.com/codex/plugins/build\n"
                "https://github.com/openai/plugins\n"
                "https://docs.github.com/en/copilot/concepts/agents/about-agent-skills\n",
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

    def test_codex_default_prompt_limits_match_ui_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "plugins" / "skill-mania" / "skills").mkdir(parents=True)
            write(
                repo_root / "plugins" / "skill-mania" / ".codex-plugin" / "plugin.json",
                """{
  "name": "skill-mania",
  "version": "0.1.0",
  "description": "Personal Agent Skills collection.",
  "keywords": ["skills"],
  "skills": "./skills/",
  "interface": {
    "displayName": "Skill Mania",
    "shortDescription": "Personal reusable skills.",
    "longDescription": "Personal reusable skills for Codex.",
    "developerName": "Hipolit Badowski",
    "category": "Productivity",
    "capabilities": ["Interactive"],
    "defaultPrompt": [
      "This prompt is intentionally longer than one hundred twenty eight characters so the validator catches UI truncation before release.",
      "Second prompt.",
      "Third prompt.",
      "Fourth prompt."
    ]
  }
}
""",
            )

            errors = validator.validate_codex_plugin_manifest(repo_root)

            joined_errors = "\n".join(errors)
            self.assertIn("interface.defaultPrompt includes 4 entries; maximum is 3", joined_errors)
            self.assertIn("interface.defaultPrompt[0] must be 128 characters or less", joined_errors)


if __name__ == "__main__":
    unittest.main()
