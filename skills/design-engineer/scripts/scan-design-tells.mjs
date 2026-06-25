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
  -h, --help             Show this help.
`);
}

function parseArgs(args) {
  const options = {
    json: false,
    failOn: "off",
    maxFindings: Number.POSITIVE_INFINITY,
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
  ".css",
  ".html",
  ".js",
  ".jsx",
  ".mdx",
  ".svelte",
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
    for (const check of checks) {
      if (check.pattern.test(line)) {
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
