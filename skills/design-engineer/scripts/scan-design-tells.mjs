#!/usr/bin/env node
import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, extname, relative, resolve } from "node:path";
import { argv, exit } from "node:process";

const severityRank = {
  off: 99,
  low: 1,
  medium: 2,
  high: 3,
};

function usage() {
  console.log(`Usage: scan-design-tells.mjs [options] [path]

Options:
  --json                 Print JSON findings.
  --fail-on <severity>   Exit 1 when findings at or above severity are present.
                         One of: off, low, medium, high. Default: off.
  --max-findings <n>     Stop after n findings. Default: no limit.
  --design-md <path>     Token traceability: flag literal CSS colors that do not
                         appear in approved declarations in the token source.
  -h, --help             Show this help.

Inline ignore: design-tell-ignore: <check-id>[, ...] -- <reason>
`);
}

function parseArgs(args) {
  const options = {
    json: false,
    failOn: "off",
    maxFindings: Number.POSITIVE_INFINITY,
    designMd: null,
    path: ".",
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--json") {
      options.json = true;
      continue;
    }
    if (arg === "-h" || arg === "--help") {
      usage();
      exit(0);
    }
    if (arg === "--fail-on") {
      options.failOn = args[index + 1];
      index += 1;
      continue;
    }
    if (arg.startsWith("--fail-on=")) {
      options.failOn = arg.slice("--fail-on=".length);
      continue;
    }
    if (arg === "--max-findings") {
      options.maxFindings = Number.parseInt(args[index + 1], 10);
      index += 1;
      continue;
    }
    if (arg.startsWith("--max-findings=")) {
      options.maxFindings = Number.parseInt(arg.slice("--max-findings=".length), 10);
      continue;
    }
    if (arg === "--design-md") {
      const value = args[index + 1];
      if (!value || value.startsWith("-")) {
        console.error("--design-md requires a path");
        exit(2);
      }
      options.designMd = value;
      index += 1;
      continue;
    }
    if (arg.startsWith("--design-md=")) {
      const value = arg.slice("--design-md=".length).trim();
      if (!value) {
        console.error("--design-md requires a path");
        exit(2);
      }
      options.designMd = value;
      continue;
    }
    if (arg.startsWith("-")) {
      console.error(`unknown option: ${arg}`);
      exit(2);
    }
    options.path = arg;
  }

  if (!(options.failOn in severityRank)) {
    console.error(`invalid --fail-on value: ${options.failOn}`);
    exit(2);
  }
  if (
    options.maxFindings !== Number.POSITIVE_INFINITY &&
    (!Number.isFinite(options.maxFindings) || options.maxFindings < 1)
  ) {
    console.error("--max-findings must be a positive integer");
    exit(2);
  }

  return options;
}

const options = parseArgs(argv.slice(2));
const root = resolve(options.path);
const allowedExt = new Set([
  ".astro",
  ".cjs",
  ".css",
  ".cts",
  ".htm",
  ".html",
  ".js",
  ".jsx",
  ".less",
  ".mdx",
  ".mjs",
  ".mts",
  ".sass",
  ".scss",
  ".svelte",
  ".svg",
  ".ts",
  ".tsx",
  ".vue",
]);
const ignoredDirs = new Set([
  ".git",
  ".next",
  ".nuxt",
  "build",
  "coverage",
  "dist",
  "node_modules",
  "out",
]);

const checks = [
  {
    id: "purple-gradient",
    severity: "medium",
    pattern: /(from|to|via)-(purple|violet|indigo|fuchsia)-|linear-gradient\([^)]*(purple|violet|indigo|fuchsia)/i,
    message: "purple/violet/indigo gradient or accent",
    remediation: "Use product, brand, or data semantics to justify color choices.",
  },
  {
    id: "gradient-text",
    severity: "medium",
    pattern: /\b(bg-clip-text|text-transparent)\b|background-clip:\s*text/i,
    message: "gradient or clipped text treatment",
    remediation: "Use plain readable text unless the brand system explicitly calls for this treatment.",
  },
  {
    id: "viewport-scaled-type",
    severity: "medium",
    pattern: /text-\[[^\]]*(vw|svw|lvw|dvw)[^\]]*\]|font-size:\s*(clamp\([^;]*(vw|svw|lvw|dvw)|[0-9.]+vw)/i,
    message: "font size scales directly with viewport width",
    remediation: "Use fixed type scales with responsive layout constraints instead of viewport-scaled text.",
  },
  {
    id: "oversized-radius",
    severity: "low",
    pattern: /rounded-(2xl|3xl|full)\b|border-radius:\s*(2[4-9]|[3-9][0-9])px/i,
    message: "large radius or pill styling",
    remediation: "Check radius against the component role and design-system scale.",
  },
  {
    id: "default-neutral",
    severity: "low",
    pattern: /\b(bg|text|border|ring)-(slate|zinc|neutral|gray)-[0-9]{2,3}\b/,
    message: "Tailwind neutral default ramp",
    remediation: "Verify neutral tokens create intentional hierarchy and contrast.",
  },
  {
    id: "cream-default",
    severity: "low",
    pattern: /\b(bg|from|to|via)-(amber|yellow|orange|stone)-50\b|background(?:-color)?:\s*(#fff7|#fef3|#fdf6|cream|beige)/i,
    message: "warm cream/beige default palette",
    remediation: "Anchor warm palettes to a real brand, material, place, or product reference.",
  },
  {
    id: "default-display-serif",
    severity: "low",
    pattern: /\bfont-serif\b|Instrument Serif|Fraunces|Playfair|Cormorant|Spectral|DM Serif/i,
    message: "common AI/default display serif",
    remediation: "Use display type only when it fits the product voice and reading context.",
  },
  {
    id: "generic-copy",
    severity: "medium",
    pattern: /\b(transform your|supercharge|unleash|effortlessly|reimagined|seamless experience|all-in-one|next-generation)\b/i,
    message: "generic AI marketing copy",
    remediation: "Replace with product-specific job, object, constraint, or outcome.",
  },
  {
    id: "emoji-icon",
    severity: "medium",
    pattern: /[🎉🚀✨🔥💡✅⭐📈🛠️]/u,
    message: "emoji used as UI icon or decoration",
    remediation: "Prefer the app's icon system or an intentional illustration style.",
  },
  {
    id: "shadcn-card",
    severity: "low",
    pattern: /\b(Card|CardHeader|CardContent|CardTitle|CardDescription)\b/,
    message: "shadcn card component usage; verify it is themed",
    remediation: "Use domain-specific layouts when card scaffolding is only decorative.",
  },
  {
    id: "side-accent-border",
    severity: "low",
    pattern: /\bborder-(l|r|left|right)-([2-9]|[1-9][0-9])\b|border-(left|right)\s*:\s*([2-9]|[1-9][0-9])px/i,
    message: "thick side accent border",
    remediation: "Use side accents only when they encode product state, category, or hierarchy.",
  },
  {
    id: "viewport-height-hero",
    severity: "medium",
    pattern: /\b(h-screen|min-h-screen)\b|height:\s*100(vh|dvh|svh|lvh)\b|min-height:\s*100(vh|dvh|svh|lvh)\b/i,
    message: "full-viewport hero or section height",
    remediation: "Ensure the first viewport is useful and leaves the next section or workflow discoverable.",
  },
  {
    id: "custom-cursor",
    severity: "medium",
    pattern: /cursor:\s*(url\(|none)\b|\bcursor-none\b/i,
    message: "custom or hidden cursor",
    remediation: "Keep native cursor behavior unless the interaction model has a strong reason and accessible fallback.",
  },
  {
    id: "scroll-listener",
    severity: "medium",
    pattern: /addEventListener\(\s*["']scroll["']/,
    message: "custom scroll listener",
    remediation: "Use scroll effects sparingly and verify performance, reduced motion, and mobile behavior.",
  },
  {
    id: "transition-all",
    severity: "low",
    pattern: /\btransition-all\b|transition:\s*all\b/i,
    message: "transition-all animation",
    remediation: "Animate only the properties that should move, and check reduced-motion behavior.",
  },
  {
    id: "bouncy-motion",
    severity: "low",
    pattern: /\b(easeOutBounce|ease-in-back|ease-out-back|elastic|bounce)\b/i,
    message: "bouncy or novelty motion easing",
    remediation: "Use motion that fits the product register and does not distract from task completion.",
  },
  {
    id: "default-shadow",
    severity: "low",
    pattern: /\bshadow-(sm|md|lg|xl|2xl)\b/,
    message: "framework-default shadow scale",
    remediation:
      "On brand surfaces define bespoke elevation in DESIGN.md; on product surfaces confirm it matches the design-system elevation scale.",
  },
  {
    id: "generic-easing",
    severity: "low",
    pattern: /\bease-in-out\b|\bease-linear\b|transition-timing-function:\s*(ease(-in-out)?|linear)\b/i,
    message: "framework-default easing",
    remediation:
      "Choose easing per motion role (enter, exit, move) from DESIGN.md; unchosen defaults read as generated on brand surfaces.",
  },
  {
    id: "section-number-eyebrow",
    severity: "low",
    pattern: /\b(00[1-9]|0[1-9])\s*(\/|\.|-)|\b(no\.?\s*0[1-9])\b/i,
    message: "numbered section eyebrow",
    remediation: "Use section numbering only when it helps navigation, sequence, or editorial structure.",
  },
  {
    id: "placeholder-persona",
    severity: "low",
    pattern: /\b(John Doe|Jane Doe|Acme|Nexus|SmartFlow|Cloudly)\b/i,
    message: "placeholder persona or fake brand name",
    remediation: "Replace placeholders with real product entities, representative data, or explicit sample labels.",
  },
  {
    id: "fake-screenshot",
    severity: "medium",
    pattern: /\b(fake screenshot|mock dashboard|placeholder screenshot|lorem dashboard)\b/i,
    message: "fake or placeholder product screenshot",
    remediation: "Use a real screen, generated product-specific mock, or the actual state users need to inspect.",
  },
];

function* walk(target) {
  const stats = statSync(target);
  if (stats.isFile()) {
    if (allowedExt.has(extname(target))) yield target;
    return;
  }
  if (!stats.isDirectory()) return;

  for (const entry of readdirSync(target, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!ignoredDirs.has(entry.name)) {
        yield* walk(resolve(target, entry.name));
      }
      continue;
    }
    if (!entry.isFile()) continue;
    const path = resolve(target, entry.name);
    if (allowedExt.has(extname(path))) yield path;
  }
}

function normalizeHex(raw) {
  let value = raw.toLowerCase();
  if (value.length === 4 || value.length === 5) {
    value = "#" + [...value.slice(1)].map((ch) => ch + ch).join("");
  }
  return value;
}

const colorFunctionPattern =
  /\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color(?:-mix)?|light-dark)\s*\(/gi;
const hexColorPattern = /#[0-9a-fA-F]{3,8}\b/g;

function extractColorLiterals(text) {
  const literals = [];
  const functionRanges = [];

  for (const match of text.matchAll(colorFunctionPattern)) {
    const start = match.index;
    if (functionRanges.some(([rangeStart, rangeEnd]) => start > rangeStart && start < rangeEnd)) {
      continue;
    }

    const open = text.indexOf("(", start);
    let depth = 0;
    let quote = null;
    let end = -1;
    for (let index = open; index < text.length; index += 1) {
      const char = text[index];
      if (quote) {
        if (char === quote && text[index - 1] !== "\\") quote = null;
        continue;
      }
      if (char === '"' || char === "'") {
        quote = char;
        continue;
      }
      if (char === "(") depth += 1;
      if (char === ")") {
        depth -= 1;
        if (depth === 0) {
          end = index + 1;
          break;
        }
      }
    }

    if (end === -1) continue;
    literals.push({ raw: text.slice(start, end), start, end });
    functionRanges.push([start, end]);
  }

  for (const match of text.matchAll(hexColorPattern)) {
    const start = match.index;
    if (functionRanges.some(([rangeStart, rangeEnd]) => start >= rangeStart && start < rangeEnd)) {
      continue;
    }
    literals.push({ raw: match[0], start, end: start + match[0].length });
  }

  return literals.sort((left, right) => left.start - right.start);
}

function normalizeColor(raw) {
  const value = raw.trim().toLowerCase();
  if (value.startsWith("#")) return normalizeHex(value);

  const open = value.indexOf("(");
  let name = value.slice(0, open).trim();
  let content = value.slice(open + 1, -1).trim().replace(/\s+/g, " ");
  if (name === "rgba") name = "rgb";
  if (name === "hsla") name = "hsl";
  if ((name === "rgb" || name === "hsl") && content.includes(",")) {
    const parts = content.split(",").map((part) => part.trim());
    content =
      parts.length === 4
        ? `${parts.slice(0, 3).join(" ")}/${parts[3]}`
        : parts.join(" ");
  }
  content = content
    .replace(/\s*,\s*/g, ",")
    .replace(/\s*\/\s*/g, "/")
    .replace(/\(\s+/g, "(")
    .replace(/\s+\)/g, ")")
    .replace(/(^|[,\s/(])(-?)0+\.(\d+)/g, "$1$2.$3");
  return `${name}(${content})`;
}

const negativeHeadingPattern =
  /\b(?:avoid|deprecated|retired|forbidden|prohibited|disallowed|anti[- ]references?|don['’]ts?|do not use|never use|not approved)\b/i;
const hardNegativeTokenPattern =
  /\b(?:deprecated|retired|forbidden|prohibited|disallowed|anti[- ]references?|not approved|example only|reference only)\b/i;
const negativeTokenPrefixPattern = /\b(?:avoid|do not use|don['’]t use|never use)\b/i;

function markdownHeading(line) {
  const match = line.match(/^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
  if (!match) return null;
  return { level: match[1].length, title: match[2] };
}

function isColorSectionTitle(title) {
  return /\b(?:colou?rs?|palette|swatches?)\b/i.test(title);
}

function isColorBlockLabel(line) {
  return /^(?:\*\*)?(?:colou?rs?(?:\s+(?:tokens?|sampled|palette))?|palette|swatches?)(?:\*\*)?:\s*$/i.test(
    line.trim()
  );
}

function isOtherBlockLabel(line) {
  return /^[A-Za-z][^:#]{0,80}:\s*$/.test(line.trim());
}

function isExplicitTokenAssignment(line, firstLiteralStart) {
  const prefix = line.slice(0, firstLiteralStart);
  return /^\s*(?:[-*+]\s+)?[`'"]?(?:--|\$|@)?[a-z][\w.-]*(?:\s+[a-z][\w.-]*){0,4}[`'"]?\s*[:=]/i.test(
    prefix
  );
}

function isListOrTableEntry(line) {
  return /^\s*(?:[-*+]\s+|\d+[.)]\s+|\|)/.test(line);
}

function hasNegativeTokenContext(line, firstLiteralStart) {
  return (
    hardNegativeTokenPattern.test(line) ||
    negativeTokenPrefixPattern.test(line.slice(0, firstLiteralStart))
  );
}

function extractDesignColorTokens(text) {
  const tokens = new Set();
  let colorHeadingLevel = null;
  let negativeHeadingLevel = null;
  let colorLabelBlock = false;

  for (const line of text.split(/\r?\n/)) {
    const heading = markdownHeading(line);
    if (heading) {
      colorLabelBlock = false;
      if (negativeHeadingLevel !== null && heading.level <= negativeHeadingLevel) {
        negativeHeadingLevel = null;
      }
      if (colorHeadingLevel !== null && heading.level <= colorHeadingLevel) {
        colorHeadingLevel = null;
      }

      const negative = negativeHeadingPattern.test(heading.title);
      if (negative) negativeHeadingLevel = heading.level;
      if (isColorSectionTitle(heading.title) && !negative) {
        colorHeadingLevel = heading.level;
      }
      continue;
    }

    const trimmed = line.trim();
    if (!trimmed) {
      colorLabelBlock = false;
      continue;
    }
    if (isColorBlockLabel(line)) {
      colorLabelBlock = true;
      continue;
    }
    if (colorLabelBlock && isOtherBlockLabel(line)) colorLabelBlock = false;

    const literals = extractColorLiterals(line);
    if (!literals.length || negativeHeadingLevel !== null) continue;
    const explicitAssignment = isExplicitTokenAssignment(line, literals[0].start);
    const approvedContext =
      explicitAssignment ||
      ((colorHeadingLevel !== null || colorLabelBlock) && isListOrTableEntry(line));
    if (!approvedContext || hasNegativeTokenContext(line, literals[0].start)) continue;
    for (const literal of literals) tokens.add(normalizeColor(literal.raw));
  }

  return tokens;
}

let designTokens = null;
if (options.designMd) {
  let designText;
  try {
    designText = readFileSync(resolve(options.designMd), "utf8");
  } catch {
    console.error(`design file not found: ${options.designMd}`);
    exit(2);
  }
  designTokens = extractDesignColorTokens(designText);
}

const suppressibleCheckIds = new Set([
  ...checks.map((check) => check.id),
  "untraced-color",
]);

function lineScanContext(line) {
  const marker = "design-tell-ignore";
  const markerIndex = line.indexOf(marker);
  if (markerIndex === -1) return { text: line, ignoredIds: new Set() };

  const ignoredIds = new Set();
  const suffix = line.slice(markerIndex + marker.length);
  const match = suffix.match(/^\s*:\s*(.*)$/);
  if (match) {
    const idList = match[1].split(/\s+--\s+/, 1)[0];
    for (const candidate of idList.toLowerCase().split(/[\s,]+/)) {
      if (suppressibleCheckIds.has(candidate)) ignoredIds.add(candidate);
    }
  }
  return { text: line.slice(0, markerIndex), ignoredIds };
}

const findings = [];
let rootStats;
try {
  rootStats = statSync(root);
} catch {
  console.error(`path not found: ${root}`);
  exit(2);
}
const reportRoot = rootStats.isDirectory() ? root : dirname(root);

for (const file of walk(root)) {
  const text = readFileSync(file, "utf8");
  const lines = text.split(/\r?\n/);
  for (const [index, line] of lines.entries()) {
    const scanContext = lineScanContext(line);
    if (designTokens && !scanContext.ignoredIds.has("untraced-color")) {
      for (const literal of extractColorLiterals(scanContext.text)) {
        if (designTokens.has(normalizeColor(literal.raw))) continue;
        findings.push({
          file: relative(reportRoot, file),
          line: index + 1,
          id: "untraced-color",
          severity: "medium",
          message: `color ${literal.raw} does not trace to the design token source`,
          remediation:
            "Every literal color must come from an approved token declaration; add the semantic token first or reuse an existing one.",
        });
        if (findings.length >= options.maxFindings) break;
      }
      if (findings.length >= options.maxFindings) break;
    }
    for (const check of checks) {
      if (scanContext.ignoredIds.has(check.id)) continue;
      if (check.pattern.test(scanContext.text)) {
        findings.push({
          file: relative(reportRoot, file),
          line: index + 1,
          id: check.id,
          severity: check.severity,
          message: check.message,
          remediation: check.remediation,
        });
        if (findings.length >= options.maxFindings) break;
      }
    }
    if (findings.length >= options.maxFindings) break;
  }
  if (findings.length >= options.maxFindings) break;
}

const failingFindings = findings.filter(
  (finding) => severityRank[finding.severity] >= severityRank[options.failOn]
);

if (options.json) {
  console.log(
    JSON.stringify(
      {
        root,
        failOn: options.failOn,
        findings,
        failingFindings: failingFindings.length,
      },
      null,
      2
    )
  );
  exit(failingFindings.length ? 1 : 0);
}

if (!findings.length) {
  console.log("No common design tells found.");
  exit(0);
}

for (const finding of findings) {
  console.log(
    `${finding.file}:${finding.line} ${finding.severity} ${finding.id} - ${finding.message}`
  );
  console.log(`  fix: ${finding.remediation}`);
}

console.log(`\n${findings.length} finding(s). ${failingFindings.length} meet --fail-on=${options.failOn}.`);
exit(failingFindings.length ? 1 : 0);
