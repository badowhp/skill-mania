# Enterprise AI Platform Architecture — Knowledge Base

Practices and procedures, current as of July 2026, for designing, automating, and
operating a secure, scalable, resilient enterprise AI platform across AWS, Databricks,
and on-premises environments, and for enabling development teams to build and run AI
solutions on it themselves.

## 1. Operating Model: Platform as a Product

The platform team is an enablement team, not a gatekeeper. Development teams are
customers; the product is a paved road — golden paths that make the secure, compliant,
observable way also the easiest way. Success is measured in adoption (teams shipping AI
features without platform tickets), time-to-first-deployment, and incident rate — not in
the number of controls. Start any platform initiative with a maturity assessment
(inventory of models, toolchains, data pipelines, governance gaps) before selecting
technology. Everything below serves that model: guardrails instead of gates, self-service
instead of request queues, templates instead of reviews.

## 2. Reference Architecture Across AWS, Databricks, On-Premises

**AWS foundation.** Multi-account landing zone (AWS Organizations plus Control Tower or
an equivalent Terraform-built structure): separate accounts per domain and stage, IAM
Identity Center for workforce identity, centralized networking (Transit Gateway,
PrivateLink endpoints for Bedrock/SageMaker/S3), and a data perimeter (SCPs plus VPC
endpoint policies) so data cannot leave governed paths. GenAI workloads run on Bedrock by
default (managed models, Guardrails, Knowledge Bases); custom training and serving on
SageMaker or EKS with Karpenter for GPU autoscaling and vLLM/Triton for high-throughput
inference. For agentic workloads, Bedrock AgentCore provides the managed production
layer — runtime, gateway, memory, identity, policy, and observability as modular
services, framework-agnostic (LangGraph, CrewAI, Strands).

**Databricks as lakehouse and ML backbone.** Unity Catalog is the single governance
plane: catalogs per domain, classification via tags, lineage and audit built in. MLflow 3
unifies experiment tracking, the model registry, GenAI tracing, scorers, and human
feedback. Agent Bricks covers governed agent development with state persisting in the
lakehouse. Workspaces are vended per domain via Terraform, bound to the central identity
provider, with serverless compute preferred and classic clusters policy-restricted.

**On-premises.** For data-gravity, sovereignty, or latency workloads: Kubernetes on GPU
nodes (or Slurm for batch training), vLLM/Triton serving behind the same API contract as
cloud inference, hybrid connectivity via Direct Connect/VPN, and one OIDC identity across
environments. On-prem clusters are GitOps targets like any other — no snowflake
operations.

**The unifying layer: a central model gateway.** One internal API (LiteLLM-style proxy or
equivalent) in front of Bedrock, Databricks serving, and on-prem vLLM. It carries model
allow-lists, quotas, cost attribution per team, audit logging, content and PII filters,
and provider failover. This is the highest-leverage platform component: every guardrail,
cost report, and migration lands here once instead of in every team's codebase.

**Agent-to-tool connectivity.** Treat MCP (Model Context Protocol) and agent-to-agent
communication as governed platform surfaces: a curated internal MCP server catalog,
version-pinned community servers, least-privilege and read-only credentials by default,
and explicit policy on which agents may call which tools and share which data. Tool
output is untrusted input — prompt-injection defense belongs at this layer.

## 3. Reference Architectures, Standards, and Decision Practice

- Publish architectures as code plus ADRs in a versioned architecture repository, not as
  slideware. Each reference architecture ships with a runnable Terraform example.
- Standards have three tiers: mandatory (security, identity, logging), default (the paved
  road — deviation needs an ADR), and recommended (patterns, libraries).
- Architecture review is lightweight: async, ADR-based, time-boxed; the platform team
  advises, the product team decides within the guardrails. Heavyweight boards kill
  adoption.
- Keep a decision log for platform-level choices (gateway, registry, evaluation stack)
  with revisit triggers, so standards evolve on evidence instead of anecdote.

## 4. Self-Service Platform Services (Internal Developer Platform)

- Backstage (or Port) as catalog and scaffolder: a team gets a new AI service via
  template — repository, CI/CD pipeline, model-gateway credentials, observability wiring,
  and a deployed hello-world in under an hour, without tickets.
- Vending machines for the heavy primitives: AWS account vending, Databricks workspace
  vending, GPU-namespace vending on shared clusters — all Terraform behind a simple
  request interface with policy checks inline.
- Platform APIs and Terraform modules are products with semver, changelogs, deprecation
  windows, and support channels. Breaking a consumer without a migration path is a
  platform incident.
- Scorecards make golden-path adoption visible (has evals, has cost tags, has runbook)
  without blocking anyone.

## 5. Automation: Terraform, GitOps, Infrastructure as Code

- Terraform module strategy: a private registry of versioned, tested modules (network,
  workspace, serving endpoint, gateway tenant); environments compose pinned module
  versions; remote state with locking; scheduled drift detection that alerts.
- Policy as code in the pipeline: OPA/Sentinel/Checkov gates on every plan — deny public
  exposure, unencrypted storage, untagged resources, and non-allow-listed model endpoints
  before apply, not in review comments.
- GitOps (Argo CD or Flux) for everything on Kubernetes, cloud and on-prem alike: the Git
  repository is the runtime truth, promotion is a pull request, rollback is a revert.
  Terraform owns cloud primitives; GitOps owns workloads; the boundary is explicit.
- Plan review discipline: destructive changes (replacements, IAM, network) surface
  automatically in the pull request rather than depending on reviewer attention.

## 6. Security, Compliance, and Governance for AI Workloads

- **Identity and least privilege:** workload identity everywhere (IRSA on EKS, service
  principals on Databricks, OIDC federation for CI — no long-lived keys); secrets in
  Vault/Secrets Manager, never in code or notebooks.
- **Data governance:** classification and lineage in Unity Catalog; training and RAG data
  access follows the same entitlements as the source data; PII redaction before indexing;
  customer-managed keys for regulated domains. Trustworthy AI output is primarily a data
  governance problem — certified assets, agreed semantics, accountable owners — before it
  is a model problem.
- **AI-specific guardrails at the gateway:** model allow-lists, content filters, prompt
  injection defenses, output filtering, and full request/response audit logs with a
  retention policy.
- **Agent governance:** agent identity distinct from user identity, scoped delegation
  (an agent acting for a user never exceeds that user's entitlements), tool-level
  authorization policy, and kill switches for autonomous loops.
- **Release gates:** no model, prompt, or agent reaches production without a passing
  evaluation suite and a model card; red-teaming for high-exposure applications.
- **Regulatory frame (EU, status July 2026):** GPAI obligations have applied since
  August 2025, with enforcement starting 2 August 2026; AI Act transparency rules take
  effect in August 2026. Under the Digital Omnibus provisional agreement of May 2026
  (pending formal adoption), Annex III high-risk-system obligations are deferred to
  2 December 2027 and Annex I embedded-AI obligations to August 2028 — track adoption
  before relying on the deferral. Build risk classification into the intake template of
  every AI use case, and let the platform generate the technical documentation, logging,
  and human-oversight evidence rather than each team hand-writing it. GDPR for personal
  data, NIS2 for operational resilience, ISO/IEC 42001 as the AI-management-system anchor
  for audits.

## 7. MLOps, LLMOps, and AgentOps with CI/CD

- **Model lifecycle:** experiment tracking → registry → staged deployment
  (shadow → canary → full) with automated rollback on SLO or quality regression.
- **LLMOps additions:** prompts and agent configurations are versioned, governed
  artifacts with rollback; every change runs an offline evaluation suite (golden
  datasets and deterministic assertions as the floor, LLM-as-judge above it); RAG
  pipelines get retrieval-quality evaluations separate from generation evaluations;
  regression gates live in CI, not in manual review.
- **AgentOps:** trace every agent step (MLflow 3 tracing, AgentCore observability, or
  Langfuse), evaluate multi-step trajectories — correctness, adherence, safety, latency,
  cost — not only final answers, and capture human feedback as first-class evaluation
  data.
- **CI/CD:** trunk-based, build-once-promote-many, OIDC to cloud, pinned third-party
  actions, environment gates for production — the same delivery discipline as any
  software, plus the evaluation gate.

## 8. Monitoring and Observability

- OpenTelemetry end to end, including the GenAI semantic conventions: every inference
  carries trace ID, model, token counts, cost, and latency; agent chains are traced per
  step.
- Dashboards pair system SLOs (availability, latency) with quality signals (evaluation
  scores, guardrail trigger rates, drift, hallucination and bias monitors).
- Alerts page on user-impacting burn rates and ticket on cost anomalies; every alert
  names an owner and a runbook.
- Telemetry is itself governed: attribute allowlists, cardinality budgets, and no
  prompts-with-PII in logs unless explicitly classified and retained accordingly.

## 9. Scalability, Availability, Cost, Operational Excellence

- GPU capacity is the scarce resource: reservations for baseline, spot for batch,
  autoscaling (Karpenter-style), and per-team quotas enforced at the gateway and the
  scheduler.
- Cost levers in effect order: route to the smallest model that passes evaluations,
  prompt and semantic caching, batch endpoints for offline work, right-sized context
  windows — then hardware. FinOps needs allocation first: every request tagged to team
  and use case at the gateway; showback monthly, chargeback when mature; unit economics
  (cost per request or per feature) on the platform dashboard.
- Availability: multi-AZ serving by default, cross-region failover for the gateway and
  top-tier models, load shedding and graceful degradation (fallback models) instead of
  hard failure, and disaster recovery that has actually been rehearsed.
- Operational excellence: platform SLOs published to consumers, blameless RCAs, error
  budgets governing the feature-versus-reliability tradeoff.

## 10. Reusable Components, Templates, Accelerators

- Accelerator catalog: RAG service starter (ingestion, chunking, vector search, and an
  evaluation harness included), agent service template (tool wiring, tracing, guardrails
  pre-integrated), batch-inference blueprint, fine-tuning pipeline, and a standalone
  evaluation harness.
- Each accelerator = template repository + Terraform module + CI pipeline + docs +
  example evaluations; versioned, with owners and a deprecation policy. An accelerator
  without evaluations and observability built in standardizes the wrong thing.
- Measure accelerator health by usage and fork divergence: heavily patched templates mean
  the template is wrong — fold the patches back.

## 11. Enablement and Consulting Practice

- Architecture office hours and embedded sprints beat review queues; the goal is that the
  second team needs less help than the first.
- Every consultation that surfaces a gap becomes a platform backlog item or an ADR —
  advice that is not encoded into the paved road is repeated forever.
- Internal champions and short workshops (how to pass the evaluation gate, how to read
  the cost dashboard) spread capability; documentation is written for the reader with a
  deadline, not for completeness.

## 12. Platform Readiness Checklist

- [ ] Landing zone with data perimeter; workload identity everywhere; no long-lived keys
- [ ] Central model gateway with allow-lists, quotas, audit logging, cost attribution
- [ ] Unity Catalog (or equivalent) as the single data-governance plane with lineage
- [ ] Terraform module registry with policy-as-code gates; GitOps for all runtimes
- [ ] Self-service scaffolding: new AI service deployed in under an hour without tickets
- [ ] Evaluation gate in CI for every model, prompt, and agent change
- [ ] Per-step agent tracing with cost and quality signals on one dashboard
- [ ] AI use-case intake with risk classification mapped to the current EU AI Act
      timeline; platform-generated compliance evidence
- [ ] Governed MCP/tool catalog with least-privilege, version-pinned connectors
- [ ] Rehearsed failover and restore; published platform SLOs and error budgets

## Related Material In This Repository

`software-architect` covers boundary and ADR work, `senior-devops-engineer` (with
`references/validation.md`) the Terraform/GitOps/Kubernetes implementation discipline,
`security-engineer` guardrail and threat-model work, `testing-engineer` and
`implementation-verifier` the evaluation-gate mindset, and `docs/mcp-servers.md` the
governed, least-privilege MCP connector pattern this knowledge base recommends.
