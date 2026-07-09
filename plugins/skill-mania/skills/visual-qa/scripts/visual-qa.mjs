#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { basename, resolve } from "node:path";
import { argv, exit } from "node:process";

const defaultViewports = [
  { name: "desktop", width: 1440, height: 1100 },
  { name: "mobile", width: 390, height: 900 },
];
const failModes = new Set(["none", "runtime", "overflow", "all"]);

function usage() {
  console.log(`Usage: visual-qa.mjs --url <url> --output <directory> [options]

Options:
  --path <path>              Append a path to the base URL. Repeatable.
  --viewport <name=WxH>      Add or replace a viewport. Repeatable.
  --wait-for <event>         Playwright load event. Default: networkidle.
  --fail-on <mode>           none, runtime, overflow, or all. Default: none.
  --dry-run                  Print the resolved plan without opening a browser.
  --json                     Print the final report as JSON.
  -h, --help                 Show this help.

Requires an existing local playwright or @playwright/test dependency. The script never installs packages.`);
}

function fail(message, code = 2) {
  console.error(message);
  exit(code);
}

function parseViewport(raw) {
  const match = /^([a-z0-9][a-z0-9-]*)=(\d{2,5})x(\d{2,5})$/i.exec(raw);
  if (!match) fail(`invalid --viewport value: ${raw}`);
  return { name: match[1], width: Number(match[2]), height: Number(match[3]) };
}

function parseArgs(args) {
  const options = {
    url: "",
    output: "",
    paths: [],
    viewports: [...defaultViewports],
    waitFor: "networkidle",
    failOn: "none",
    dryRun: false,
    json: false,
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "-h" || arg === "--help") {
      usage();
      exit(0);
    }
    if (arg === "--url") options.url = args[++index] || "";
    else if (arg === "--output") options.output = args[++index] || "";
    else if (arg === "--path") options.paths.push(args[++index] || "");
    else if (arg === "--viewport") {
      const viewport = parseViewport(args[++index] || "");
      options.viewports = options.viewports.filter(({ name }) => name !== viewport.name);
      options.viewports.push(viewport);
    } else if (arg === "--wait-for") options.waitFor = args[++index] || "";
    else if (arg === "--fail-on") options.failOn = args[++index] || "";
    else if (arg === "--dry-run") options.dryRun = true;
    else if (arg === "--json") options.json = true;
    else fail(`unknown option: ${arg}`);
  }

  if (!options.url) fail("--url is required");
  if (!options.output) fail("--output is required");
  try {
    new URL(options.url);
  } catch {
    fail(`invalid --url: ${options.url}`);
  }
  if (!["commit", "domcontentloaded", "load", "networkidle"].includes(options.waitFor)) {
    fail(`invalid --wait-for value: ${options.waitFor}`);
  }
  if (!failModes.has(options.failOn)) fail(`invalid --fail-on value: ${options.failOn}`);
  if (options.paths.some((path) => !path || !path.startsWith("/"))) {
    fail("--path values must start with /");
  }
  return options;
}

function routesFor(options) {
  const paths = options.paths.length ? options.paths : [""];
  return paths.map((path) => new URL(path, options.url).toString());
}

function safeName(value) {
  return basename(value || "index").replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "") || "index";
}

function routeName(route) {
  const pathname = new URL(route).pathname;
  return safeName(pathname.replaceAll("/", "-"));
}

function loadPlaywright() {
  const requireFromProject = createRequire(resolve(process.cwd(), "visual-qa-runner.cjs"));
  for (const packageName of ["playwright", "@playwright/test"]) {
    try {
      return requireFromProject(packageName);
    } catch (error) {
      if (error?.code !== "MODULE_NOT_FOUND") throw error;
    }
  }
  fail("visual-qa needs an existing local playwright or @playwright/test dependency", 1);
}

function shouldFail(report, mode) {
  const runtime = report.pages.some((page) => page.consoleErrors.length || page.failedRequests.length);
  const overflow = report.pages.some((page) => page.horizontalOverflow);
  return mode === "all" ? runtime || overflow : mode === "runtime" ? runtime : mode === "overflow" ? overflow : false;
}

async function capture(options) {
  const playwright = loadPlaywright();
  const chromium = playwright.chromium;
  if (!chromium) fail("Playwright was found but does not expose chromium", 1);

  const output = resolve(options.output);
  mkdirSync(output, { recursive: true });
  const report = {
    url: options.url,
    routes: routesFor(options),
    viewports: options.viewports,
    waitFor: options.waitFor,
    pages: [],
  };
  const browser = await chromium.launch();

  try {
    for (const route of report.routes) {
      for (const viewport of options.viewports) {
        const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
        const page = await context.newPage();
        const consoleErrors = [];
        const failedRequests = [];
        page.on("console", (message) => {
          if (message.type() === "error") consoleErrors.push(message.text());
        });
        page.on("requestfailed", (request) => {
          failedRequests.push({ url: request.url(), error: request.failure()?.errorText || "unknown" });
        });

        const screenshot = `${routeName(route)}-${viewport.name}.png`;
        const entry = { route, viewport, screenshot, consoleErrors, failedRequests };
        try {
          await page.goto(route, { waitUntil: options.waitFor, timeout: 30000 });
          await page.screenshot({ path: resolve(output, screenshot), fullPage: true });
          const inspection = await page.evaluate(() => {
            const root = document.documentElement;
            const body = document.body;
            return {
              title: document.title,
              hasPrimaryContent: Boolean(document.querySelector("main, [role='main']")),
              horizontalOverflow: Math.max(root.scrollWidth, body?.scrollWidth || 0) > window.innerWidth + 1,
            };
          });
          await page.keyboard.press("Tab");
          entry.focusedElement = await page.evaluate(() => {
            const element = document.activeElement;
            if (!element || element === document.body) return null;
            const style = getComputedStyle(element);
            return { tag: element.tagName.toLowerCase(), visible: style.visibility !== "hidden" && style.display !== "none" };
          });
          Object.assign(entry, inspection);
        } catch (error) {
          entry.error = error instanceof Error ? error.message : String(error);
        } finally {
          report.pages.push(entry);
          await context.close();
        }
      }
    }
  } finally {
    await browser.close();
  }

  writeFileSync(resolve(output, "report.json"), `${JSON.stringify(report, null, 2)}\n`);
  return report;
}

const options = parseArgs(argv.slice(2));
const plan = { ...options, routes: routesFor(options), output: resolve(options.output) };
if (options.dryRun) {
  console.log(JSON.stringify(plan, null, 2));
  exit(0);
}

try {
  const report = await capture(options);
  if (options.json) console.log(JSON.stringify(report, null, 2));
  else console.log(`Captured ${report.pages.length} viewport(s) in ${resolve(options.output)}`);
  exit(shouldFail(report, options.failOn) ? 1 : 0);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  exit(1);
}
