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

export function sanitizeUrl(value) {
  try {
    const parsed = new URL(value);
    parsed.username = "";
    parsed.password = "";
    parsed.hash = "";
    if (parsed.search) parsed.search = "?redacted";
    return parsed.toString();
  } catch {
    return "<invalid-url>";
  }
}

export function redactEvidenceText(value) {
  const text = String(value ?? "").slice(0, 20000);
  return text
    .replace(
      /-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----/gi,
      "<redacted-private-key>",
    )
    .replace(/\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b/g, "<redacted-openai-key>")
    .replace(/\bgh[pousr]_[A-Za-z0-9]{30,}\b/g, "<redacted-github-token>")
    .replace(/\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/g, "<redacted-aws-key>")
    .replace(/\bxox[baprs]-[A-Za-z0-9-]{20,}\b/g, "<redacted-slack-token>")
    .replace(/\bBearer\s+[^\s"'<>]+/gi, "Bearer <redacted>")
    .replace(
      /\b(api[_-]?key|access[_-]?token|password|secret)\b(\s*[=:]\s*)[^\s,;"'<>]+/gi,
      "$1$2<redacted>",
    )
    .replace(/https?:\/\/[^\s"'<>]+/gi, (url) => sanitizeUrl(url))
    .slice(0, 4000);
}
