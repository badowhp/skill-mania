# Verification Checklist

A control is verified by demonstrated failure of the attack and demonstrated success of legitimate use — never by the presence of the control alone.

## Deterministic Floor
1. Negative test: reproduce the exploit path against the fixed code and show it is refused (status, error, or log evidence).
2. Positive test: show the legitimate flow still succeeds with the same control in place.
3. Run the repository's static analysis and dependency audit on the changed surface (semgrep/CodeQL rules, `npm audit`/`pip-audit`/`govulncheck` or the stack's equivalent).
4. Secret scan the diff and any new configuration.
5. For authz fixes: test at least one horizontal case (peer's resource) and one vertical case (lower privilege hitting a higher-privilege action).

## Evidence Checklist
- The fix is at the trust boundary, not in the client or in input the attacker controls.
- Cache, retry, queue, and background paths that bypass the fixed entry point are enumerated and checked.
- Logging captures the refused attempt without recording secrets or tokens.
- Findings closed as false positives carry the reasoning and the test that would have caught a true positive.
- Anything unverifiable in this environment (production config, WAF, third-party IdP behavior) is a named residual risk with an owner, not a silent assumption.
