package skillmanager

import (
	"os"
	"path/filepath"
	"testing"
)

const testSkillName = "demo-skill"

func writeTestFile(t *testing.T, path string, contents string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatalf("create parent directory for %s: %v", path, err)
	}
	if err := os.WriteFile(path, []byte(contents), 0o644); err != nil {
		t.Fatalf("write %s: %v", path, err)
	}
}

func createTestCatalog(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	skillRoot := filepath.Join(root, "skills", testSkillName)
	writeTestFile(t, filepath.Join(skillRoot, "SKILL.md"), `---
name: demo-skill
description: Test skill for manager behavior.
---

# Demo
`)
	writeTestFile(t, filepath.Join(skillRoot, "agents", "openai.yaml"), `interface:
  display_name: "Demo Skill"
  short_description: "Test manager operations"
`)
	writeTestFile(t, filepath.Join(skillRoot, "evals", "evals.json"), `{
  "evals": [
    {"should_trigger": true, "assertions": ["observable"]},
    {"should_trigger": false, "assertions": []}
  ]
}
`)
	writeTestFile(t, filepath.Join(root, "config", "skill-groups.json"), `{
  "schema_version": 1,
  "groups": [
    {
      "id": "demo",
      "name": "Demo",
      "description": "Test package.",
      "aliases": [],
      "skills": ["demo-skill"]
    }
  ]
}
`)
	return root
}

func createTestRepository(t *testing.T) (*Repository, string, string) {
	t.Helper()
	catalogRoot := createTestCatalog(t)
	targetRoot := t.TempDir()
	repository, err := Open(catalogRoot, []TargetConfig{
		{ID: "agents", Name: "Codex", Path: targetRoot},
	})
	if err != nil {
		t.Fatalf("open test repository: %v", err)
	}
	return repository, catalogRoot, targetRoot
}
