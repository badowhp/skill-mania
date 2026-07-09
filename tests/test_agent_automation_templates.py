from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD = REPO_ROOT / "templates" / "agent-automation" / "guard-agent-command.py"


class AgentAutomationTemplateTests(unittest.TestCase):
    def run_guard(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(GUARD)],
            input=json.dumps({"tool_input": {"command": command}}),
            check=False,
            text=True,
            capture_output=True,
        )

    def test_allows_non_destructive_command(self) -> None:
        result = self.run_guard("git status --short")

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_blocks_unmistakably_destructive_command(self) -> None:
        result = self.run_guard("git reset --hard")

        self.assertEqual(result.returncode, 2)
        self.assertIn("blocked hard git reset", result.stderr)


if __name__ == "__main__":
    unittest.main()
