from __future__ import annotations

import json
import subprocess
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = REPO_ROOT / "templates" / "agent-automation"
GUARD = TEMPLATES / "guard-agent-command.py"


class AgentAutomationTemplateTests(unittest.TestCase):
    def run_guard(
        self, command: str, *, tool_name: str = "Bash"
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(GUARD)],
            input=json.dumps(
                {"tool_name": tool_name, "tool_input": {"command": command}}
            ),
            check=False,
            text=True,
            capture_output=True,
        )

    def assert_blocked(self, command: str, reason: str) -> None:
        result = self.run_guard(command)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn(reason, decision["permissionDecisionReason"])

    def test_allows_routine_and_dry_run_commands(self) -> None:
        commands = (
            "git status --short",
            "git clean -nfd",
            "git restore --staged README.md",
            "rm build.log",
            "terraform plan",
            "kubectl get pods",
            "echo 'git reset --hard'",
        )
        for command in commands:
            with self.subTest(command=command):
                result = self.run_guard(command)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_blocks_destructive_filesystem_and_git_commands(self) -> None:
        cases = {
            "rm -rf node_modules": "recursive filesystem deletion",
            "find . -delete": "recursive find deletion",
            "git reset --hard HEAD": "hard git reset",
            "git clean -fdx": "forced git clean",
            "git restore README.md": "git worktree restore",
            "git push --force-with-lease origin main": "forced or deleting git push",
            "git stash clear": "git stash deletion",
        }
        for command, reason in cases.items():
            with self.subTest(command=command):
                self.assert_blocked(command, reason)

    def test_blocks_wrapped_and_compound_destructive_commands(self) -> None:
        cases = {
            "sudo git reset --hard": "hard git reset",
            "bash -lc 'git clean -fd'": "forced git clean",
            "git status && rm -r build": "recursive filesystem deletion",
            "find . -exec rm -rf {} +": "recursive filesystem deletion",
        }
        for command, reason in cases.items():
            with self.subTest(command=command):
                self.assert_blocked(command, reason)

    def test_blocks_destructive_infrastructure_commands(self) -> None:
        cases = {
            "terraform destroy": "infrastructure destruction",
            "kubectl delete namespace production": "destructive Kubernetes operation",
            "helm uninstall production": "Helm release deletion",
            "aws ec2 terminate-instances --instance-ids i-123": "destructive cloud operation",
            "psql -c 'DROP DATABASE production'": "destructive database statement",
        }
        for command, reason in cases.items():
            with self.subTest(command=command):
                self.assert_blocked(command, reason)

    def test_blocks_apply_patch_file_deletion(self) -> None:
        result = self.run_guard(
            "*** Begin Patch\n*** Delete File: important.txt\n*** End Patch",
            tool_name="apply_patch",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("file deletion through apply_patch", decision["permissionDecisionReason"])

    def test_supports_copilot_camel_case_hook_payload(self) -> None:
        result = subprocess.run(
            ["python3", str(GUARD)],
            input=json.dumps(
                {
                    "toolName": "bash",
                    "toolArgs": json.dumps({"command": "git reset --hard"}),
                }
            ),
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("hard git reset", output["permissionDecisionReason"])

    def test_fails_closed_for_invalid_hook_input(self) -> None:
        result = subprocess.run(
            ["python3", str(GUARD)],
            input="not json",
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("expected JSON", result.stderr)

    def test_template_configs_parse_and_enable_hardening(self) -> None:
        claude = json.loads((TEMPLATES / "claude-settings.json").read_text())
        managed_claude = json.loads(
            (TEMPLATES / "claude-managed-settings.json").read_text()
        )
        with (TEMPLATES / "codex-config.toml").open("rb") as handle:
            codex = tomllib.load(handle)
        with (TEMPLATES / "codex-requirements.toml").open("rb") as handle:
            codex_requirements = tomllib.load(handle)

        for settings in (claude, managed_claude):
            self.assertEqual(settings["permissions"]["defaultMode"], "default")
            self.assertEqual(
                settings["permissions"]["disableBypassPermissionsMode"], "disable"
            )
            self.assertTrue(settings["sandbox"]["enabled"])
            self.assertTrue(settings["sandbox"]["failIfUnavailable"])
            self.assertFalse(settings["sandbox"]["allowUnsandboxedCommands"])
        self.assertEqual(codex["approval_policy"], "untrusted")
        self.assertEqual(codex["approvals_reviewer"], "user")
        self.assertFalse(
            codex["permissions"]["agent_safe_workspace"]["network"]["enabled"]
        )
        self.assertEqual(
            codex_requirements["allowed_approval_policies"], ["untrusted"]
        )
        self.assertNotIn(
            ":danger-full-access",
            codex_requirements["allowed_permission_profiles"],
        )

    def test_repo_configs_use_the_shared_guard(self) -> None:
        claude = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text())
        with (REPO_ROOT / ".codex" / "config.toml").open("rb") as handle:
            codex = tomllib.load(handle)

        claude_command = claude["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        codex_command = codex["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertIn("templates/agent-automation/guard-agent-command.py", claude_command)
        self.assertIn("templates/agent-automation/guard-agent-command.py", codex_command)


if __name__ == "__main__":
    unittest.main()
