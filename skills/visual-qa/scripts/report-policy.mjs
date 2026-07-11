#!/usr/bin/env node

export function shouldFail(report, mode) {
  const runtime = report.pages.some(
    (page) =>
      Boolean(page.error) ||
      Boolean(page.consoleErrors?.length) ||
      Boolean(page.pageErrors?.length) ||
      Boolean(page.failedRequests?.length),
  );
  const overflow = report.pages.some((page) => Boolean(page.horizontalOverflow));
  if (mode === "all") return runtime || overflow;
  if (mode === "runtime") return runtime;
  if (mode === "overflow") return overflow;
  return false;
}
