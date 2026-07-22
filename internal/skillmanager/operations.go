package skillmanager

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
)

var skillNamePattern = regexp.MustCompile(`^[a-z0-9]+(?:-[a-z0-9]+)*$`)

type ActionResult struct {
	Skill   string `json:"skill"`
	Target  string `json:"target"`
	Status  string `json:"status"`
	Message string `json:"message"`
}

type ActionResponse struct {
	Action  string         `json:"action"`
	Target  string         `json:"target"`
	Results []ActionResult `json:"results"`
}

func (r *Repository) Apply(action string, targetID string, names []string) ActionResponse {
	r.mu.Lock()
	defer r.mu.Unlock()

	response := ActionResponse{Action: action, Target: targetID}
	target, ok := r.targetByID(targetID)
	if !ok {
		return ActionResponse{
			Action: action,
			Target: targetID,
			Results: []ActionResult{{
				Target:  targetID,
				Status:  "error",
				Message: "Unknown installation target.",
			}},
		}
	}
	info, err := os.Stat(target.Path)
	if err != nil || !info.IsDir() {
		return ActionResponse{
			Action: action,
			Target: targetID,
			Results: []ActionResult{{
				Target:  targetID,
				Status:  "error",
				Message: "The target directory is not mounted or readable.",
			}},
		}
	}

	selected := r.validSelection(names)
	if len(selected) == 0 {
		response.Results = []ActionResult{{
			Target:  targetID,
			Status:  "error",
			Message: "Select at least one catalog skill.",
		}}
		return response
	}

	for _, name := range selected {
		var operationErr error
		switch action {
		case "install":
			operationErr = r.installCopy(target, name)
		case "remove":
			operationErr = r.removeManaged(target, name)
		default:
			operationErr = fmt.Errorf("unsupported action %q", action)
		}
		result := ActionResult{Skill: name, Target: targetID}
		if operationErr != nil {
			result.Status = "error"
			result.Message = operationErr.Error()
		} else if action == "remove" {
			result.Status = "removed"
			result.Message = "Managed skill removed."
		} else {
			result.Status = "installed"
			result.Message = "Managed copy installed."
		}
		response.Results = append(response.Results, result)
	}
	return response
}

func (r *Repository) targetByID(id string) (TargetConfig, bool) {
	for _, target := range r.targets {
		if target.ID == id {
			return target, true
		}
	}
	return TargetConfig{}, false
}

func (r *Repository) validSelection(names []string) []string {
	seen := make(map[string]bool)
	selected := make([]string, 0, len(names))
	for _, name := range names {
		if !skillNamePattern.MatchString(name) || seen[name] {
			continue
		}
		if _, ok := r.skillIndex[name]; !ok {
			continue
		}
		seen[name] = true
		selected = append(selected, name)
	}
	sort.Strings(selected)
	return selected
}

func (r *Repository) installCopy(target TargetConfig, skill string) error {
	destination := filepath.Join(target.Path, skill)
	state := r.installState(target, skill)
	if state.State == "unmanaged" || state.State == "error" {
		return fmt.Errorf("%s is %s and will not be replaced", skill, strings.ToLower(state.Label))
	}

	temporary, err := os.MkdirTemp(target.Path, ".skill-mania-"+skill+"-")
	if err != nil {
		return fmt.Errorf("create temporary install: %w", err)
	}
	defer os.RemoveAll(temporary)
	if err := os.Remove(temporary); err != nil {
		return fmt.Errorf("prepare temporary install: %w", err)
	}
	if err := copyTree(filepath.Join(r.skillsRoot, skill), temporary); err != nil {
		return fmt.Errorf("copy %s: %w", skill, err)
	}
	marker := struct {
		SchemaVersion int    `json:"schema_version"`
		Manager       string `json:"manager"`
		Skill         string `json:"skill"`
		Mode          string `json:"mode"`
	}{
		SchemaVersion: 1,
		Manager:       "skill-mania",
		Skill:         skill,
		Mode:          "copy",
	}
	markerBytes, err := json.MarshalIndent(marker, "", "  ")
	if err != nil {
		return fmt.Errorf("encode managed marker: %w", err)
	}
	markerBytes = append(markerBytes, '\n')
	if err := os.WriteFile(filepath.Join(temporary, managedMarker), markerBytes, 0o644); err != nil {
		return fmt.Errorf("write managed marker: %w", err)
	}

	if state.State == "absent" {
		if err := os.Rename(temporary, destination); err != nil {
			return fmt.Errorf("activate install: %w", err)
		}
		return nil
	}

	backup, err := temporaryPath(target.Path, skill+"-backup")
	if err != nil {
		return err
	}
	if err := os.Rename(destination, backup); err != nil {
		return fmt.Errorf("stage existing managed install: %w", err)
	}
	if err := os.Rename(temporary, destination); err != nil {
		restoreErr := os.Rename(backup, destination)
		if restoreErr != nil {
			return fmt.Errorf("activate install: %v; restore failed: %v", err, restoreErr)
		}
		return fmt.Errorf("activate install: %w", err)
	}
	if err := os.RemoveAll(backup); err != nil {
		return fmt.Errorf("remove replaced managed install: %w", err)
	}
	return nil
}

func (r *Repository) removeManaged(target TargetConfig, skill string) error {
	destination := filepath.Join(target.Path, skill)
	state := r.installState(target, skill)
	if state.State == "absent" {
		return fmt.Errorf("%s is not installed", skill)
	}
	if !state.Managed {
		return fmt.Errorf("%s is unmanaged and is protected from deletion", skill)
	}
	if err := os.RemoveAll(destination); err != nil {
		return fmt.Errorf("remove %s: %w", skill, err)
	}
	return nil
}

func temporaryPath(root string, label string) (string, error) {
	random := make([]byte, 8)
	if _, err := rand.Read(random); err != nil {
		return "", fmt.Errorf("generate temporary path: %w", err)
	}
	return filepath.Join(root, ".skill-mania-"+label+"-"+hex.EncodeToString(random)), nil
}

func copyTree(source string, destination string) error {
	return filepath.WalkDir(source, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		relative, err := filepath.Rel(source, path)
		if err != nil {
			return err
		}
		if relative == "." {
			return os.MkdirAll(destination, 0o755)
		}
		if skipCopiedPath(entry.Name()) {
			if entry.IsDir() {
				return filepath.SkipDir
			}
			return nil
		}
		if entry.Type()&os.ModeSymlink != 0 {
			return fmt.Errorf("refusing source symlink %s", path)
		}
		target := filepath.Join(destination, relative)
		info, err := entry.Info()
		if err != nil {
			return err
		}
		if entry.IsDir() {
			return os.MkdirAll(target, info.Mode().Perm())
		}
		if !info.Mode().IsRegular() {
			return fmt.Errorf("refusing non-regular source file %s", path)
		}
		return copyFile(path, target, info.Mode().Perm())
	})
}

func skipCopiedPath(name string) bool {
	if name == ".DS_Store" || name == "__pycache__" || name == ".tmp" || name == ".cache" || name == "node_modules" {
		return true
	}
	return strings.HasSuffix(name, ".pyc")
}

func copyFile(source string, destination string, mode fs.FileMode) error {
	input, err := os.Open(source)
	if err != nil {
		return err
	}
	defer input.Close()
	output, err := os.OpenFile(destination, os.O_CREATE|os.O_EXCL|os.O_WRONLY, mode)
	if err != nil {
		return err
	}
	copied := false
	defer func() {
		if !copied {
			os.Remove(destination)
		}
	}()
	if _, err := io.Copy(output, input); err != nil {
		output.Close()
		return err
	}
	if err := output.Close(); err != nil {
		return err
	}
	copied = true
	return nil
}

func responseHasErrors(response ActionResponse) bool {
	for _, result := range response.Results {
		if result.Status == "error" {
			return true
		}
	}
	return false
}
