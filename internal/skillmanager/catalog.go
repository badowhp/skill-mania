package skillmanager

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

const managedMarker = ".skill-mania-managed.json"

type Group struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Aliases     []string `json:"aliases"`
	Skills      []string `json:"skills"`
}

type TargetConfig struct {
	ID   string
	Name string
	Path string
}

type Target struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Path    string `json:"path"`
	Mounted bool   `json:"mounted"`
}

type InstallState struct {
	State   string `json:"state"`
	Managed bool   `json:"managed"`
	Label   string `json:"label"`
}

type EvalSummary struct {
	Positive   int `json:"positive"`
	NearMiss   int `json:"near_miss"`
	Assertions int `json:"assertions"`
}

type Benchmark struct {
	ID              string  `json:"id"`
	Source          string  `json:"source"`
	GeneratedAt     string  `json:"generated_at"`
	Provider        string  `json:"provider"`
	Model           string  `json:"model"`
	ReasoningEffort string  `json:"reasoning_effort"`
	JudgeModel      string  `json:"judge_model"`
	RoutingModel    string  `json:"routing_model"`
	GitSHA          string  `json:"git_sha"`
	BaselineKind    string  `json:"baseline_kind"`
	BaselineLabel   string  `json:"baseline_label"`
	RunnerVersion   int     `json:"runner_version"`
	ContextMode     string  `json:"context_mode"`
	Cases           int     `json:"cases"`
	Assertions      int     `json:"assertions"`
	WithSkillRate   float64 `json:"with_skill_rate"`
	BaselineRate    float64 `json:"baseline_rate"`
	PassRateDelta   float64 `json:"pass_rate_delta"`
	Verdict         string  `json:"verdict"`
	GatePassed      bool    `json:"gate_passed"`
	WithSkillTokens int     `json:"with_skill_tokens"`
	BaselineTokens  int     `json:"baseline_tokens"`
	WithSkillTimeMS int64   `json:"with_skill_duration_ms"`
	BaselineTimeMS  int64   `json:"baseline_duration_ms"`
}

type Skill struct {
	Name             string                  `json:"name"`
	DisplayName      string                  `json:"display_name"`
	ShortDescription string                  `json:"short_description"`
	Description      string                  `json:"description"`
	Groups           []string                `json:"groups"`
	Evals            EvalSummary             `json:"evals"`
	Benchmark        *Benchmark              `json:"benchmark,omitempty"`
	BenchmarkRuns    int                     `json:"benchmark_runs"`
	Installed        map[string]InstallState `json:"installed"`
	SourcePath       string                  `json:"source_path"`
}

type Snapshot struct {
	GeneratedAt string   `json:"generated_at"`
	Groups      []Group  `json:"groups"`
	Skills      []Skill  `json:"skills"`
	Targets     []Target `json:"targets"`
}

type Repository struct {
	mu         sync.Mutex
	skillsRoot string
	groups     []Group
	skills     []Skill
	skillIndex map[string]int
	targets    []TargetConfig
}

type groupsFile struct {
	SchemaVersion int     `json:"schema_version"`
	Groups        []Group `json:"groups"`
}

type evalFile struct {
	Evals []struct {
		ShouldTrigger bool     `json:"should_trigger"`
		Assertions    []string `json:"assertions"`
	} `json:"evals"`
}

type benchmarkFile struct {
	Configuration struct {
		GeneratedAt     string `json:"generated_at"`
		Provider        string `json:"provider"`
		Model           string `json:"model"`
		ReasoningEffort string `json:"reasoning_effort"`
		JudgeModel      string `json:"judge_model"`
		RoutingModel    string `json:"routing_model"`
		GitSHA          string `json:"git_sha"`
		RunnerVersion   int    `json:"runner_version"`
		ContextMode     string `json:"context_mode"`
		Baseline        struct {
			Kind  string `json:"kind"`
			Label string `json:"label"`
		} `json:"baseline"`
	} `json:"configuration"`
	Skills map[string]struct {
		Cases               int     `json:"cases"`
		Assertions          int     `json:"assertions"`
		WithSkillPassRate   float64 `json:"with_skill_pass_rate"`
		BaselinePassRate    float64 `json:"baseline_pass_rate"`
		PassRateDelta       float64 `json:"pass_rate_delta"`
		Verdict             string  `json:"verdict"`
		GatePassed          bool    `json:"gate_passed"`
		WithSkillTokens     int     `json:"with_skill_tokens"`
		BaselineTokens      int     `json:"baseline_tokens"`
		WithSkillDurationMS int64   `json:"with_skill_duration_ms"`
		BaselineDurationMS  int64   `json:"baseline_duration_ms"`
	} `json:"skills"`
}

type benchmarkSeries struct {
	Latest *Benchmark
	Runs   []Benchmark
}

type benchmarkCatalogFile struct {
	SchemaVersion int `json:"schema_version"`
	Skills        map[string]struct {
		Status string      `json:"status"`
		Latest *Benchmark  `json:"latest"`
		Runs   []Benchmark `json:"runs"`
	} `json:"skills"`
}

func Open(catalogRoot string, targets []TargetConfig) (*Repository, error) {
	root, err := filepath.Abs(catalogRoot)
	if err != nil {
		return nil, fmt.Errorf("resolve catalog root: %w", err)
	}
	skillsRoot := filepath.Join(root, "skills")
	if info, statErr := os.Stat(skillsRoot); statErr != nil || !info.IsDir() {
		return nil, fmt.Errorf("catalog skills directory is unavailable: %s", skillsRoot)
	}
	if resolved, resolveErr := filepath.EvalSymlinks(root); resolveErr == nil {
		root = resolved
		skillsRoot = filepath.Join(root, "skills")
	}
	targets, err = normalizeTargets(root, targets)
	if err != nil {
		return nil, err
	}

	groups, err := readGroups(filepath.Join(root, "config", "skill-groups.json"))
	if err != nil {
		return nil, err
	}
	benchmarks, foundCatalog, err := readBenchmarkCatalog(filepath.Join(root, "benchmarks", "catalog.json"))
	if err != nil {
		return nil, err
	}
	if !foundCatalog {
		benchmarks, err = readBenchmarks(filepath.Join(root, "benchmarks", "baselines"))
		if err != nil {
			return nil, err
		}
	}
	skills, err := readSkills(skillsRoot, groups, benchmarks)
	if err != nil {
		return nil, err
	}
	index := make(map[string]int, len(skills))
	for i := range skills {
		index[skills[i].Name] = i
	}
	for _, group := range groups {
		for _, skill := range group.Skills {
			if _, ok := index[skill]; !ok {
				return nil, fmt.Errorf("group %s references unknown skill %s", group.ID, skill)
			}
		}
	}

	return &Repository{
		skillsRoot: skillsRoot,
		groups:     groups,
		skills:     skills,
		skillIndex: index,
		targets:    targets,
	}, nil
}

func normalizeTargets(catalogRoot string, targets []TargetConfig) ([]TargetConfig, error) {
	if len(targets) == 0 {
		return nil, errors.New("at least one installation target is required")
	}
	seenIDs := make(map[string]bool, len(targets))
	seenPaths := make(map[string]bool, len(targets))
	result := make([]TargetConfig, 0, len(targets))
	for _, target := range targets {
		if !skillNamePattern.MatchString(target.ID) || strings.TrimSpace(target.Name) == "" {
			return nil, fmt.Errorf("invalid installation target %q", target.ID)
		}
		if seenIDs[target.ID] {
			return nil, fmt.Errorf("duplicate installation target ID %q", target.ID)
		}
		path, err := filepath.Abs(target.Path)
		if err != nil {
			return nil, fmt.Errorf("resolve target %s: %w", target.ID, err)
		}
		path, err = resolvePath(path)
		if err != nil {
			return nil, fmt.Errorf("resolve target %s: %w", target.ID, err)
		}
		path = filepath.Clean(path)
		if filepath.Dir(path) == path {
			return nil, fmt.Errorf("target %s must not be a filesystem root", target.ID)
		}
		if pathsContainEachOther(path, catalogRoot) {
			return nil, fmt.Errorf("target %s must not overlap the catalog", target.ID)
		}
		if seenPaths[path] {
			return nil, fmt.Errorf("installation targets must use distinct directories: %s", path)
		}
		seenIDs[target.ID] = true
		seenPaths[path] = true
		target.Path = path
		result = append(result, target)
	}
	return result, nil
}

func resolvePath(path string) (string, error) {
	current := filepath.Clean(path)
	var suffix []string
	for {
		resolved, err := filepath.EvalSymlinks(current)
		if err == nil {
			for i := len(suffix) - 1; i >= 0; i-- {
				resolved = filepath.Join(resolved, suffix[i])
			}
			return resolved, nil
		}
		if !errors.Is(err, fs.ErrNotExist) {
			return "", err
		}
		parent := filepath.Dir(current)
		if parent == current {
			return path, nil
		}
		suffix = append(suffix, filepath.Base(current))
		current = parent
	}
}

func pathsContainEachOther(first string, second string) bool {
	return pathContains(first, second) || pathContains(second, first)
}

func pathContains(parent string, child string) bool {
	relative, err := filepath.Rel(parent, child)
	if err != nil {
		return false
	}
	return relative == "." || (relative != ".." && !strings.HasPrefix(relative, ".."+string(filepath.Separator)))
}

func readGroups(path string) ([]Group, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read skill groups: %w", err)
	}
	var document groupsFile
	if err := json.Unmarshal(data, &document); err != nil {
		return nil, fmt.Errorf("parse skill groups: %w", err)
	}
	if document.SchemaVersion != 1 || len(document.Groups) == 0 {
		return nil, errors.New("skill groups require schema version 1 and at least one group")
	}
	return document.Groups, nil
}

func readSkills(skillsRoot string, groups []Group, benchmarks map[string]benchmarkSeries) ([]Skill, error) {
	entries, err := os.ReadDir(skillsRoot)
	if err != nil {
		return nil, fmt.Errorf("read skills: %w", err)
	}
	groupMembership := make(map[string][]string)
	for _, group := range groups {
		for _, skill := range group.Skills {
			groupMembership[skill] = append(groupMembership[skill], group.ID)
		}
	}

	var skills []Skill
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		dir := filepath.Join(skillsRoot, entry.Name())
		frontmatter, err := readFrontmatter(filepath.Join(dir, "SKILL.md"))
		if errors.Is(err, fs.ErrNotExist) {
			continue
		}
		if err != nil {
			return nil, err
		}
		name := frontmatter["name"]
		description := frontmatter["description"]
		if name == "" || description == "" || name != entry.Name() {
			return nil, fmt.Errorf("invalid skill frontmatter in %s", dir)
		}
		displayName, shortDescription := readOpenAIMetadata(filepath.Join(dir, "agents", "openai.yaml"))
		if displayName == "" {
			displayName = titleFromName(name)
		}
		if shortDescription == "" {
			shortDescription = description
		}
		evals, err := readEvals(filepath.Join(dir, "evals", "evals.json"))
		if err != nil {
			return nil, err
		}
		skill := Skill{
			Name:             name,
			DisplayName:      displayName,
			ShortDescription: shortDescription,
			Description:      description,
			Groups:           append([]string(nil), groupMembership[name]...),
			Evals:            evals,
			Installed:        make(map[string]InstallState),
			SourcePath:       filepath.ToSlash(filepath.Join("skills", name)),
		}
		if series, ok := benchmarks[name]; ok {
			skill.BenchmarkRuns = len(series.Runs)
			if series.Latest != nil {
				copy := *series.Latest
				skill.Benchmark = &copy
			}
		}
		skills = append(skills, skill)
	}
	sort.Slice(skills, func(i, j int) bool { return skills[i].Name < skills[j].Name })
	return skills, nil
}

func readFrontmatter(path string) (map[string]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	values := make(map[string]string)
	scanner := bufio.NewScanner(file)
	lineNumber := 0
	inside := false
	for scanner.Scan() {
		lineNumber++
		line := scanner.Text()
		if lineNumber == 1 {
			if strings.TrimSpace(line) != "---" {
				return nil, fmt.Errorf("%s has no YAML frontmatter", path)
			}
			inside = true
			continue
		}
		if inside && strings.TrimSpace(line) == "---" {
			break
		}
		if !inside || strings.HasPrefix(strings.TrimSpace(line), "#") {
			continue
		}
		key, raw, ok := strings.Cut(line, ":")
		if !ok {
			continue
		}
		key = strings.TrimSpace(key)
		if key != "name" && key != "description" {
			continue
		}
		values[key] = trimYAMLString(raw)
	}
	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("scan %s: %w", path, err)
	}
	return values, nil
}

func readOpenAIMetadata(path string) (string, string) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", ""
	}
	var displayName, shortDescription string
	for _, line := range strings.Split(string(data), "\n") {
		key, raw, ok := strings.Cut(strings.TrimSpace(line), ":")
		if !ok {
			continue
		}
		switch key {
		case "display_name":
			displayName = trimYAMLString(raw)
		case "short_description":
			shortDescription = trimYAMLString(raw)
		}
	}
	return displayName, shortDescription
}

func trimYAMLString(value string) string {
	value = strings.TrimSpace(value)
	if len(value) >= 2 {
		first := value[0]
		last := value[len(value)-1]
		if (first == 34 && last == 34) || (first == 39 && last == 39) {
			return value[1 : len(value)-1]
		}
	}
	return value
}

func titleFromName(name string) string {
	parts := strings.Split(name, "-")
	for i := range parts {
		if parts[i] != "" {
			parts[i] = strings.ToUpper(parts[i][:1]) + parts[i][1:]
		}
	}
	return strings.Join(parts, " ")
}

func readEvals(path string) (EvalSummary, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return EvalSummary{}, fmt.Errorf("read evals %s: %w", path, err)
	}
	var document evalFile
	if err := json.Unmarshal(data, &document); err != nil {
		return EvalSummary{}, fmt.Errorf("parse evals %s: %w", path, err)
	}
	var summary EvalSummary
	for _, item := range document.Evals {
		if item.ShouldTrigger {
			summary.Positive++
			summary.Assertions += len(item.Assertions)
		} else {
			summary.NearMiss++
		}
	}
	return summary, nil
}

func readBenchmarkCatalog(path string) (map[string]benchmarkSeries, bool, error) {
	data, err := os.ReadFile(path)
	if errors.Is(err, fs.ErrNotExist) {
		return nil, false, nil
	}
	if err != nil {
		return nil, false, fmt.Errorf("read benchmark catalog: %w", err)
	}
	var document benchmarkCatalogFile
	if err := json.Unmarshal(data, &document); err != nil {
		return nil, false, fmt.Errorf("parse benchmark catalog: %w", err)
	}
	if document.SchemaVersion != 1 || document.Skills == nil {
		return nil, false, errors.New("benchmark catalog requires schema version 1 and a skills object")
	}
	result := make(map[string]benchmarkSeries, len(document.Skills))
	for name, entry := range document.Skills {
		if entry.Status != "saved" && entry.Status != "not-saved" {
			return nil, false, fmt.Errorf("benchmark catalog has invalid status for %s", name)
		}
		for _, run := range entry.Runs {
			if run.ID == "" || run.Source == "" || run.GeneratedAt == "" {
				return nil, false, fmt.Errorf("benchmark catalog has an incomplete run for %s", name)
			}
		}
		if entry.Status == "saved" {
			if entry.Latest == nil || len(entry.Runs) == 0 || entry.Latest.ID != entry.Runs[len(entry.Runs)-1].ID {
				return nil, false, fmt.Errorf("benchmark catalog latest run is inconsistent for %s", name)
			}
		} else if entry.Latest != nil || len(entry.Runs) != 0 {
			return nil, false, fmt.Errorf("benchmark catalog marks %s unsaved but includes runs", name)
		}
		result[name] = benchmarkSeries{Latest: entry.Latest, Runs: append([]Benchmark(nil), entry.Runs...)}
	}
	return result, true, nil
}

func readBenchmarks(root string) (map[string]benchmarkSeries, error) {
	result := make(map[string]benchmarkSeries)
	info, err := os.Stat(root)
	if errors.Is(err, fs.ErrNotExist) {
		return result, nil
	}
	if err != nil || !info.IsDir() {
		return nil, fmt.Errorf("benchmark root is invalid: %s", root)
	}
	err = filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() || entry.Name() != "benchmark.json" {
			return nil
		}
		data, readErr := os.ReadFile(path)
		if readErr != nil {
			return readErr
		}
		var document benchmarkFile
		if unmarshalErr := json.Unmarshal(data, &document); unmarshalErr != nil {
			return fmt.Errorf("parse benchmark %s: %w", path, unmarshalErr)
		}
		relative, _ := filepath.Rel(root, filepath.Dir(path))
		for name, value := range document.Skills {
			candidate := Benchmark{
				Source:          filepath.ToSlash(relative),
				GeneratedAt:     document.Configuration.GeneratedAt,
				Provider:        document.Configuration.Provider,
				Model:           document.Configuration.Model,
				ReasoningEffort: document.Configuration.ReasoningEffort,
				JudgeModel:      document.Configuration.JudgeModel,
				RoutingModel:    document.Configuration.RoutingModel,
				GitSHA:          document.Configuration.GitSHA,
				BaselineKind:    document.Configuration.Baseline.Kind,
				BaselineLabel:   document.Configuration.Baseline.Label,
				RunnerVersion:   document.Configuration.RunnerVersion,
				ContextMode:     document.Configuration.ContextMode,
				Cases:           value.Cases,
				Assertions:      value.Assertions,
				WithSkillRate:   value.WithSkillPassRate,
				BaselineRate:    value.BaselinePassRate,
				PassRateDelta:   value.PassRateDelta,
				Verdict:         value.Verdict,
				GatePassed:      value.GatePassed,
				WithSkillTokens: value.WithSkillTokens,
				BaselineTokens:  value.BaselineTokens,
				WithSkillTimeMS: value.WithSkillDurationMS,
				BaselineTimeMS:  value.BaselineDurationMS,
			}
			series := result[name]
			series.Runs = append(series.Runs, candidate)
			result[name] = series
		}
		return nil
	})
	if err != nil {
		return nil, fmt.Errorf("read benchmarks: %w", err)
	}
	for name, series := range result {
		sort.Slice(series.Runs, func(i, j int) bool {
			return series.Runs[i].GeneratedAt < series.Runs[j].GeneratedAt
		})
		latest := series.Runs[len(series.Runs)-1]
		series.Latest = &latest
		result[name] = series
	}
	return result, nil
}

func (r *Repository) Snapshot() Snapshot {
	r.mu.Lock()
	defer r.mu.Unlock()

	targets := make([]Target, 0, len(r.targets))
	for _, config := range r.targets {
		info, err := os.Stat(config.Path)
		targets = append(targets, Target{
			ID:      config.ID,
			Name:    config.Name,
			Path:    config.Path,
			Mounted: err == nil && info.IsDir(),
		})
	}
	skills := make([]Skill, len(r.skills))
	for i := range r.skills {
		skills[i] = r.skills[i]
		skills[i].Groups = append([]string(nil), r.skills[i].Groups...)
		skills[i].Installed = make(map[string]InstallState, len(r.targets))
		for _, target := range r.targets {
			skills[i].Installed[target.ID] = r.installState(target, skills[i].Name)
		}
	}
	groups := append([]Group(nil), r.groups...)
	return Snapshot{
		GeneratedAt: time.Now().UTC().Format(time.RFC3339),
		Groups:      groups,
		Skills:      skills,
		Targets:     targets,
	}
}

func (r *Repository) installState(target TargetConfig, skill string) InstallState {
	destination := filepath.Join(target.Path, skill)
	info, err := os.Lstat(destination)
	if errors.Is(err, fs.ErrNotExist) {
		return InstallState{State: "absent", Label: "Not installed"}
	}
	if err != nil {
		return InstallState{State: "error", Label: "Unreadable"}
	}
	if info.Mode()&os.ModeSymlink != 0 {
		link, readErr := os.Readlink(destination)
		if readErr == nil {
			if !filepath.IsAbs(link) {
				link = filepath.Join(filepath.Dir(destination), link)
			}
			if resolved, resolveErr := filepath.Abs(link); resolveErr == nil && filepath.Clean(resolved) == filepath.Join(r.skillsRoot, skill) {
				return InstallState{State: "managed-link", Managed: true, Label: "Managed link"}
			}
		}
		return InstallState{State: "unmanaged", Label: "External link"}
	}
	if !info.IsDir() {
		return InstallState{State: "unmanaged", Label: "Conflicting file"}
	}
	data, readErr := os.ReadFile(filepath.Join(destination, managedMarker))
	if readErr == nil {
		var marker struct {
			SchemaVersion int    `json:"schema_version"`
			Manager       string `json:"manager"`
			Skill         string `json:"skill"`
			Mode          string `json:"mode"`
		}
		if json.Unmarshal(data, &marker) == nil && marker.SchemaVersion == 1 && marker.Manager == "skill-mania" && marker.Skill == skill && marker.Mode == "copy" {
			return InstallState{State: "managed-copy", Managed: true, Label: "Managed copy"}
		}
	}
	return InstallState{State: "unmanaged", Label: "Unmanaged install"}
}
