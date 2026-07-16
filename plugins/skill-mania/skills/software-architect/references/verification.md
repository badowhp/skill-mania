# Verification Checklist

Architecture output has no compiler, so verification means confronting the design with evidence that could reject it.

## Deterministic Floor
1. Compile or validate every produced contract artifact: OpenAPI/JSON Schema lint, protobuf/IDL compile, migration SQL syntax check against the target engine version.
2. Cross-check names: every service, topic, table, and endpoint the design references must exist in the current system evidence or be explicitly marked new.
3. Check number sanity: stated throughput, storage, and latency budgets against the measured baselines supplied; a budget with no baseline is an assumption to flag.

## Evidence Checklist
- Each boundary decision names the failure mode it accepts (consistency, latency, coupling) and why the alternative was rejected.
- Data ownership is single-writer per entity, or the exception has an explicit reconciliation path.
- The migration plan has a reversible first step and a point of no return that is named, not implied.
- Backward compatibility is stated per consumer: who breaks, when, and what the contract test that catches it looks like.
- The ADR records decision, status, context, consequences, and the revisit trigger; an ADR that cannot fail a future review is not a decision record.
- Open questions that block implementation are listed with the owner who can answer them, instead of being resolved by assumption.
