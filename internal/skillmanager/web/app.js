const catalogURL = "/api/catalog";
const actionsURL = "/api/actions";
const csrfToken = document.querySelector("meta[name=csrf-token]").content;

const elements = {
  summarySkills: document.querySelector("#summary-skills"),
  summaryGroups: document.querySelector("#summary-groups"),
  summaryBenchmarks: document.querySelector("#summary-benchmarks"),
  summaryTargets: document.querySelector("#summary-targets"),
  packageList: document.querySelector("#package-list"),
  skillsTitle: document.querySelector("#skills-title"),
  filterContext: document.querySelector("#filter-context"),
  search: document.querySelector("#skill-search"),
  target: document.querySelector("#target-filter"),
  state: document.querySelector("#state-filter"),
  selectVisible: document.querySelector("#select-visible"),
  skillList: document.querySelector("#skill-list"),
  evidencePanel: document.querySelector("#evidence-panel"),
  emptyInspector: document.querySelector("#empty-inspector"),
  inspector: document.querySelector("#skill-inspector"),
  selectionBar: document.querySelector("#selection-bar"),
  selectionCount: document.querySelector("#selection-count"),
  selectionTarget: document.querySelector("#selection-target"),
  clearSelection: document.querySelector("#clear-selection"),
  installSelected: document.querySelector("#install-selected"),
  removeSelected: document.querySelector("#remove-selected"),
  removeDialog: document.querySelector("#remove-dialog"),
  removeSummary: document.querySelector("#remove-summary"),
  removeList: document.querySelector("#remove-list"),
  toast: document.querySelector("#toast"),
};

let catalog = null;
let activeGroup = "all";
let activeSkill = null;
let busy = false;
let toastTimer = null;
const selected = new Set();

function create(tag, className, text) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined) {
    node.textContent = text;
  }
  return node;
}

function targetByID(id) {
  return catalog.targets.find((target) => target.id === id);
}

function targetState(skill, targetID = elements.target.value) {
  return skill.installed[targetID] || {
    state: "error",
    managed: false,
    label: "Target unavailable",
  };
}

function visibleSkills() {
  const query = elements.search.value.trim().toLocaleLowerCase();
  const stateFilter = elements.state.value;
  return catalog.skills.filter((skill) => {
    if (activeGroup !== "all" && !skill.groups.includes(activeGroup)) {
      return false;
    }
    if (query) {
      const groupNames = skill.groups.map((id) => {
        const group = catalog.groups.find((candidate) => candidate.id === id);
        return group ? group.name : id;
      });
      const searchable = [
        skill.name,
        skill.display_name,
        skill.short_description,
        skill.description,
        ...groupNames,
      ].join(" ").toLocaleLowerCase();
      if (!searchable.includes(query)) {
        return false;
      }
    }
    const install = targetState(skill);
    if (stateFilter === "installed" && install.state === "absent") {
      return false;
    }
    if (stateFilter === "managed" && !install.managed) {
      return false;
    }
    if (stateFilter === "absent" && install.state !== "absent") {
      return false;
    }
    if (stateFilter === "unmanaged" && install.state !== "unmanaged" && install.state !== "error") {
      return false;
    }
    return true;
  });
}

function formatDelta(value) {
  const points = Math.round(value * 100);
  return `${points > 0 ? "+" : ""}${points} pp`;
}

function formatRate(value) {
  return `${Math.round(value * 100)}%`;
}

function formatDate(value) {
  if (!value) {
    return "Date unavailable";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.valueOf())) {
    return value;
  }
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(parsed);
}

function statusChip(state) {
  const chip = create("span", "status-chip", state.label);
  chip.dataset.state = state.state;
  return chip;
}

function renderSummary() {
  elements.summarySkills.textContent = catalog.skills.length;
  elements.summaryGroups.textContent = catalog.groups.length;
  elements.summaryBenchmarks.textContent = catalog.skills.filter((skill) => skill.benchmark).length;
  const mounted = catalog.targets.filter((target) => target.mounted);
  if (mounted.length === catalog.targets.length) {
    elements.summaryTargets.textContent = `${mounted.length} writable targets ready`;
  } else if (mounted.length === 0) {
    elements.summaryTargets.textContent = "No installation targets are mounted";
  } else {
    elements.summaryTargets.textContent = `${mounted.length} of ${catalog.targets.length} targets ready`;
  }
}

function renderTargets() {
  const previous = elements.target.value;
  elements.target.replaceChildren();
  for (const target of catalog.targets) {
    const option = create("option", "", target.mounted ? target.name : `${target.name} — unavailable`);
    option.value = target.id;
    elements.target.append(option);
  }
  if (catalog.targets.some((target) => target.id === previous)) {
    elements.target.value = previous;
  }
}

function packageButton(id, name, description, count) {
  const button = create("button", "package-button");
  button.type = "button";
  button.dataset.group = id;
  button.setAttribute("aria-current", String(activeGroup === id));

  const title = create("span", "package-title");
  title.append(create("span", "", name));
  title.append(create("span", "package-count", String(count)));
  button.append(title, create("span", "package-description", description));
  button.addEventListener("click", () => {
    activeGroup = id;
    renderPackages();
    renderSkills();
  });
  return button;
}

function renderPackages() {
  const fragment = document.createDocumentFragment();
  fragment.append(packageButton(
    "all",
    "All skills",
    "The complete catalog, ready for individual or bulk selection.",
    catalog.skills.length,
  ));
  for (const group of catalog.groups) {
    fragment.append(packageButton(group.id, group.name, group.description, group.skills.length));
  }
  elements.packageList.replaceChildren(fragment);
}

function evidenceCell(skill) {
  const cell = create("div", "evidence-cell");
  const evalLine = create("span", "evidence-line");
  const evalCount = create("strong", "", String(skill.evals.positive));
  evalLine.append(evalCount, document.createTextNode(` positive · ${skill.evals.near_miss} near-miss`));
  cell.append(evalLine);

  const benchmarkLine = create("span", "evidence-line");
  if (skill.benchmark) {
    const delta = create(
      "strong",
      skill.benchmark.pass_rate_delta >= 0 ? "benchmark-positive" : "benchmark-warning",
      formatDelta(skill.benchmark.pass_rate_delta),
    );
    benchmarkLine.append(delta, document.createTextNode(` · ${skill.benchmark_runs} saved run${skill.benchmark_runs === 1 ? "" : "s"}`));
  } else {
    benchmarkLine.textContent = "No saved benchmark";
  }
  cell.append(benchmarkLine);
  return cell;
}

function skillRow(skill) {
  const row = create("article", "skill-row");
  if (selected.has(skill.name)) {
    row.classList.add("is-selected");
  }
  if (activeSkill === skill.name) {
    row.classList.add("is-active");
  }

  const checkbox = create("input");
  checkbox.type = "checkbox";
  checkbox.checked = selected.has(skill.name);
  checkbox.setAttribute("aria-label", `Select ${skill.display_name}`);
  checkbox.addEventListener("change", () => {
    if (checkbox.checked) {
      selected.add(skill.name);
    } else {
      selected.delete(skill.name);
    }
    renderSkills();
    renderSelection();
  });

  const open = create("button", "skill-copy");
  open.type = "button";
  open.setAttribute("aria-label", `Inspect ${skill.display_name}`);
  const name = create("div", "skill-name", skill.display_name);
  name.append(create("span", "skill-id", skill.name));
  open.append(name, create("p", "skill-description", skill.short_description));
  open.addEventListener("click", () => inspectSkill(skill.name));

  const status = create("div", "status-cell");
  status.append(statusChip(targetState(skill)));
  row.append(checkbox, open, evidenceCell(skill), status);
  return row;
}

function activeGroupDetails() {
  if (activeGroup === "all") {
    return {
      name: "All available skills",
      description: "Every folder with a valid SKILL.md",
    };
  }
  const group = catalog.groups.find((candidate) => candidate.id === activeGroup);
  return group || {name: "Skill package", description: "Selected workflow package"};
}

function renderSkills() {
  const skills = visibleSkills();
  const group = activeGroupDetails();
  elements.skillsTitle.textContent = group.name;
  elements.filterContext.textContent = `${skills.length} shown · ${group.description}`;
  elements.skillList.setAttribute("aria-busy", "false");

  if (skills.length === 0) {
    const empty = create("div", "empty-list");
    empty.append(
      create("h3", "", "No skills match these filters"),
      create("p", "", "Clear the search or choose a different package, target, or installation state."),
    );
    elements.skillList.replaceChildren(empty);
  } else {
    const fragment = document.createDocumentFragment();
    for (const skill of skills) {
      fragment.append(skillRow(skill));
    }
    elements.skillList.replaceChildren(fragment);
  }

  const allVisibleSelected = skills.length > 0 && skills.every((skill) => selected.has(skill.name));
  elements.selectVisible.textContent = allVisibleSelected ? "Clear visible" : "Select visible";
}

function inspectorSection(title) {
  const section = create("section", "inspector-section");
  section.append(create("h3", "", title));
  return section;
}

function renderInspector() {
  const skill = catalog.skills.find((candidate) => candidate.name === activeSkill);
  if (!skill) {
    elements.emptyInspector.hidden = false;
    elements.inspector.hidden = true;
    elements.evidencePanel.classList.remove("is-open");
    return;
  }

  const fragment = document.createDocumentFragment();
  const close = create("button", "inspector-close", "Close");
  close.type = "button";
  close.addEventListener("click", () => {
    elements.evidencePanel.classList.remove("is-open");
  });

  const header = create("header", "inspector-header");
  header.append(
    create("p", "eyebrow", skill.name),
    create("h2", "", skill.display_name),
    create("p", "inspector-description", skill.description),
  );

  const packages = inspectorSection("Package membership");
  const tagList = create("div", "tag-list");
  for (const groupID of skill.groups) {
    const group = catalog.groups.find((candidate) => candidate.id === groupID);
    tagList.append(create("span", "tag", group ? group.name : groupID));
  }
  packages.append(tagList);

  const evals = inspectorSection("Routing eval coverage");
  const metricGrid = create("div", "metric-grid");
  const metrics = [
    [skill.evals.positive, "positive prompts"],
    [skill.evals.near_miss, "near-miss prompts"],
    [skill.evals.assertions, "assertions"],
  ];
  for (const [value, label] of metrics) {
    const metric = create("div", "metric");
    metric.append(create("strong", "", String(value)), create("span", "", label));
    metricGrid.append(metric);
  }
  evals.append(metricGrid);

  const benchmark = inspectorSection("Latest saved benchmark");
  if (skill.benchmark) {
    const block = create("div", "benchmark-block");
    const head = create("div", "benchmark-head");
    head.append(
      create("strong", "", skill.benchmark.verdict || "Recorded result"),
      create(
        "span",
        `benchmark-delta ${skill.benchmark.pass_rate_delta >= 0 ? "benchmark-positive" : "benchmark-warning"}`,
        formatDelta(skill.benchmark.pass_rate_delta),
      ),
    );
    block.append(
      head,
      create(
        "p",
        "benchmark-meta",
        `${formatRate(skill.benchmark.with_skill_rate)} with skill vs ${formatRate(skill.benchmark.baseline_rate)} baseline · ${skill.benchmark.cases} cases · ${skill.benchmark.assertions} assertions`,
      ),
      create(
        "p",
        "benchmark-meta",
        `${formatDate(skill.benchmark.generated_at)} · ${skill.benchmark.source} · gate ${skill.benchmark.gate_passed ? "passed" : "not passed"}`,
      ),
    );
    const provenance = [
      skill.benchmark.provider,
      skill.benchmark.model,
      skill.benchmark.reasoning_effort ? `${skill.benchmark.reasoning_effort} reasoning` : "",
      skill.benchmark.baseline_kind ? `baseline ${skill.benchmark.baseline_kind}` : "",
    ].filter(Boolean).join(" · ");
    if (provenance) {
      block.append(create("p", "benchmark-meta", provenance));
    }
    benchmark.append(block);
  } else {
    benchmark.append(create(
      "p",
      "no-benchmark",
      "Routing eval definitions are present, but no paired model benchmark has been saved for this skill yet.",
    ));
  }

  const installs = inspectorSection("Installation state");
  const stateList = create("div", "state-list");
  for (const target of catalog.targets) {
    const row = create("div", "state-row");
    row.append(create("span", "", target.name), statusChip(targetState(skill, target.id)));
    stateList.append(row);
  }
  installs.append(stateList);

  const source = inspectorSection("Catalog source");
  source.append(create("p", "source-path mono", skill.source_path));

  fragment.append(close, header, packages, evals, benchmark, installs, source);
  elements.inspector.replaceChildren(fragment);
  elements.emptyInspector.hidden = true;
  elements.inspector.hidden = false;
}

function inspectSkill(name) {
  activeSkill = name;
  renderSkills();
  renderInspector();
  elements.evidencePanel.classList.add("is-open");
}

function currentTargetReady() {
  const target = targetByID(elements.target.value);
  return Boolean(target && target.mounted);
}

function renderSelection() {
  const count = selected.size;
  const target = targetByID(elements.target.value);
  elements.selectionBar.hidden = count === 0;
  elements.selectionCount.textContent = `${count} selected`;
  elements.selectionTarget.textContent = target ? `for ${target.name}` : "for unavailable target";
  elements.installSelected.disabled = busy || !currentTargetReady();
  elements.removeSelected.disabled = busy || !currentTargetReady() || managedSelection().length === 0;
  elements.clearSelection.disabled = busy;
}

function showToast(message, kind = "success") {
  window.clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.dataset.kind = kind;
  elements.toast.hidden = false;
  toastTimer = window.setTimeout(() => {
    elements.toast.hidden = true;
  }, 5200);
}

function managedSelection() {
  return catalog.skills.filter((skill) => selected.has(skill.name) && targetState(skill).managed);
}

async function performAction(action, names, confirm = false) {
  if (busy || names.length === 0) {
    return;
  }
  busy = true;
  document.body.setAttribute("aria-busy", "true");
  renderSelection();
  try {
    const response = await fetch(actionsURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
      },
      body: JSON.stringify({
        action,
        target: elements.target.value,
        skills: names,
        confirm,
      }),
    });
    const payload = await response.json();
    if (!response.ok && !payload.results) {
      throw new Error(payload.error || `Request failed with ${response.status}`);
    }
    const results = payload.results || [];
    const succeeded = results.filter((result) => result.status !== "error");
    const failed = results.filter((result) => result.status === "error");
    for (const result of succeeded) {
      selected.delete(result.skill);
    }
    await loadCatalog();
    if (failed.length) {
      const detail = failed.length === 1 ? failed[0].message : `${failed.length} items were protected or failed`;
      showToast(`${succeeded.length} completed. ${detail}`, "error");
    } else {
      showToast(`${succeeded.length} ${action === "install" ? "installed" : "removed"} successfully.`);
    }
  } catch (error) {
    showToast(error instanceof Error ? error.message : "The action could not be completed.", "error");
  } finally {
    busy = false;
    document.body.removeAttribute("aria-busy");
    renderSelection();
  }
}

function openRemoveDialog() {
  const managed = managedSelection();
  if (managed.length === 0) {
    showToast("None of the selected skills are managed by Skill Mania on this target.", "error");
    return;
  }
  const protectedCount = selected.size - managed.length;
  elements.removeSummary.textContent = protectedCount > 0
    ? `${managed.length} managed skills will be removed. ${protectedCount} unmanaged or absent selections will remain untouched.`
    : `${managed.length} managed skills will be removed from the selected target.`;
  const items = managed.map((skill) => create("li", "", skill.name));
  elements.removeList.replaceChildren(...items);
  elements.removeDialog.returnValue = "cancel";
  elements.removeDialog.showModal();
}

async function loadCatalog() {
  const response = await fetch(catalogURL, {headers: {Accept: "application/json"}});
  if (!response.ok) {
    throw new Error(`Catalog request failed with ${response.status}`);
  }
  catalog = await response.json();
  renderTargets();
  renderSummary();
  renderPackages();
  renderSkills();
  renderInspector();
  renderSelection();
}

elements.search.addEventListener("input", renderSkills);
elements.state.addEventListener("change", renderSkills);
elements.target.addEventListener("change", () => {
  renderSkills();
  renderInspector();
  renderSelection();
});
elements.selectVisible.addEventListener("click", () => {
  const skills = visibleSkills();
  const clear = skills.length > 0 && skills.every((skill) => selected.has(skill.name));
  for (const skill of skills) {
    if (clear) {
      selected.delete(skill.name);
    } else {
      selected.add(skill.name);
    }
  }
  renderSkills();
  renderSelection();
});
elements.clearSelection.addEventListener("click", () => {
  selected.clear();
  renderSkills();
  renderSelection();
});
elements.installSelected.addEventListener("click", () => {
  performAction("install", Array.from(selected));
});
elements.removeSelected.addEventListener("click", openRemoveDialog);
elements.removeDialog.addEventListener("close", () => {
  if (elements.removeDialog.returnValue === "confirm") {
    performAction("remove", managedSelection().map((skill) => skill.name), true);
  }
});

loadCatalog().catch((error) => {
  elements.skillList.setAttribute("aria-busy", "false");
  const empty = create("div", "empty-list");
  empty.append(
    create("h3", "", "Catalog unavailable"),
    create("p", "", error instanceof Error ? error.message : "The manager could not load the skill inventory."),
  );
  elements.skillList.replaceChildren(empty);
  showToast("The catalog could not be loaded.", "error");
});
