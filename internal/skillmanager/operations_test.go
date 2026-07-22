package skillmanager

import (
	"os"
	"path/filepath"
	"testing"
)

func resultStatus(response ActionResponse) string {
	if len(response.Results) != 1 {
		return ""
	}
	return response.Results[0].Status
}

func TestInstallAndRemoveManagedCopy(t *testing.T) {
	repository, _, targetRoot := createTestRepository(t)

	installed := repository.Apply("install", "agents", []string{testSkillName})
	if status := resultStatus(installed); status != "installed" {
		t.Fatalf("install status = %q, response = %#v", status, installed)
	}
	destination := filepath.Join(targetRoot, testSkillName)
	if _, err := os.Stat(filepath.Join(destination, managedMarker)); err != nil {
		t.Fatalf("managed marker missing: %v", err)
	}
	state := repository.Snapshot().Skills[0].Installed["agents"]
	if !state.Managed || state.State != "managed-copy" {
		t.Fatalf("installed state = %#v", state)
	}

	removed := repository.Apply("remove", "agents", []string{testSkillName})
	if status := resultStatus(removed); status != "removed" {
		t.Fatalf("remove status = %q, response = %#v", status, removed)
	}
	if _, err := os.Lstat(destination); !os.IsNotExist(err) {
		t.Fatalf("managed destination still exists or could not be inspected: %v", err)
	}
}

func TestUnmanagedInstallIsProtected(t *testing.T) {
	repository, _, targetRoot := createTestRepository(t)
	destination := filepath.Join(targetRoot, testSkillName)
	writeTestFile(t, filepath.Join(destination, "SKILL.md"), "local skill\n")
	writeTestFile(t, filepath.Join(destination, "local-notes.txt"), "preserve me\n")

	installed := repository.Apply("install", "agents", []string{testSkillName})
	if status := resultStatus(installed); status != "error" {
		t.Fatalf("unmanaged install replacement status = %q", status)
	}
	removed := repository.Apply("remove", "agents", []string{testSkillName})
	if status := resultStatus(removed); status != "error" {
		t.Fatalf("unmanaged remove status = %q", status)
	}
	contents, err := os.ReadFile(filepath.Join(destination, "local-notes.txt"))
	if err != nil || string(contents) != "preserve me\n" {
		t.Fatalf("unmanaged content changed: %q, %v", contents, err)
	}
}

func TestInstallRefusesSourceSymlink(t *testing.T) {
	repository, catalogRoot, targetRoot := createTestRepository(t)
	sourceLink := filepath.Join(catalogRoot, "skills", testSkillName, "linked-file")
	if err := os.Symlink("SKILL.md", sourceLink); err != nil {
		t.Skipf("symlinks unavailable: %v", err)
	}

	response := repository.Apply("install", "agents", []string{testSkillName})
	if status := resultStatus(response); status != "error" {
		t.Fatalf("symlinked source install status = %q, response = %#v", status, response)
	}
	if _, err := os.Lstat(filepath.Join(targetRoot, testSkillName)); !os.IsNotExist(err) {
		t.Fatalf("failed install left destination behind: %v", err)
	}
}

func TestOpenRejectsTargetInsideCatalog(t *testing.T) {
	catalogRoot := createTestCatalog(t)
	_, err := Open(catalogRoot, []TargetConfig{
		{ID: "agents", Name: "Codex", Path: filepath.Join(catalogRoot, "targets")},
	})
	if err == nil {
		t.Fatal("expected catalog overlap to be rejected")
	}
}
