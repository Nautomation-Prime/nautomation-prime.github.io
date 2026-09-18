---
title: Automation Control Catalogue
description: Forty-six stable control identifiers for governed network automation, each with its requirement, the minimum evidence it needs, and where on this site the reasoning behind it is explained.
tags:
  - Standards
  - Governance
  - Controls
  - Audit
  - Enterprise
---

## Automation Control Catalogue

Everything else on this site explains *why* a control exists. This page gives each one a short, stable name so you can point at it.

That sounds like a small thing. It is not. The moment two teams, a security reviewer, and an auditor need to discuss the same requirement, prose stops working — "the bit about checking the device is the right device" is not something you can put in a design document, a waiver, or a change record and expect to mean the same thing six months later. A code does that job.

!!! tip "What a control code is for"
    A code is a **shorthand for a requirement, not a replacement for it.** `NP-CORE-02` is ten characters you can write in a service record. The reasoning behind it is a whole page, and the reviewer is expected to have read it.

---

## How the Catalogue Is Organised

Seven families, grouped by what the control protects rather than by which document introduced it:

| Family | Covers | Count |
|---|---|---|
| **NP-CORE** | Targeting and execution safety — what happens before anything is touched | 8 |
| **NP-CHG** | Change control — the additional bar for anything that writes | 6 |
| **NP-EVD** | Evidence and observability — what the run leaves behind | 5 |
| **NP-GOV** | Governance and lifecycle — ownership, classification, review, retirement | 7 |
| **NP-AI** | Governed AI — constraints on a model's authority | 6 |
| **NP-TOOL** | Tool boundary — how a capability is exposed to an agent or caller | 8 |
| **NP-PLAT** | Platform and delivery — how the thing is built, shipped, and run | 6 |

Not every control applies to every service. Applicability is decided by [risk class](../production-grade-network-automation-principles/enterprise-control-matrix.md#automation-risk-classification), and recording *why* a control does not apply is itself part of the [assessment method](./self-assessment.md).

---

## NP-CORE — Targeting and Execution Safety

These apply to everything, including read-only work. A report that queries the wrong device is still wrong.

| ID | Control | Requirement | Minimum evidence |
|---|---|---|---|
| **NP-CORE-01** | Source of truth resolution | Resolve every operational target through an approved authoritative source. A user-supplied identifier is a request to resolve, never a connection target | Resolved record with source and timestamp |
| **NP-CORE-02** | Target identity verification | Compare expected, controller, and live identity before any controlled action | Three-way comparison and the allow, hold, or reject decision |
| **NP-CORE-03** | Input validation | Treat all external input as untrusted. Validate type, range, format, and operational scope before opening a connection or changing state | Input schema with positive and negative tests |
| **NP-CORE-04** | Read-only default | Observation is the default. Change capability is invoked explicitly and never inferred from context | Capability classification and role configuration |
| **NP-CORE-05** | Pre-flight validation | Confirm prerequisites before acting, and abort when they fail | Pre-flight report with reason codes |
| **NP-CORE-06** | Scope limitation | Bound the set of targets a single run can affect, and expand that set deliberately | Scope definition, canary results, batch promotion approvals |
| **NP-CORE-07** | Idempotency | Read current state, compare against desired state, act only on the difference | Repeated-run and no-change-required tests |
| **NP-CORE-08** | Safe failure | Bounded timeouts, finite retries, resource cleanup, and fail-closed behaviour on uncertainty | Failure-path tests, timeout and retry configuration |

**Where the reasoning lives:** [Trust Boundaries Around Your Source of Truth](../production-grade-network-automation-principles/trust-boundaries-around-your-source-of-truth.md) (01), [Validating Device Identity](../production-grade-network-automation-principles/validating-device-identity-before-automation-runs.md) (02), [From Script to Tool](../governed-ai-network-operations/from-script-to-tool.md) (03), [Separating Read and Write Phases](../production-grade-network-automation-principles/separating-read-and-write-phases.md) (04), [Pre-Flight Checks](../production-grade-network-automation-principles/pre-flight-checks-failing-fast-before-making-changes.md) (05), [Scoping to Reduce Blast Radius](../production-grade-network-automation-principles/scoping-automation-to-reduce-blast-radius.md) (06), [Real-World Idempotency](../production-grade-network-automation-principles/real-world-idempotency-in-network-automation.md) (07), [Designing Automation That Can Safely Fail](../production-grade-network-automation-principles/designing-automation-that-can-safely-fail.md) (08).

---

## NP-CHG — Change Control

These become mandatory the moment a workflow can alter device state — [R3](../production-grade-network-automation-principles/enterprise-control-matrix.md#automation-risk-classification) and above.

| ID | Control | Requirement | Minimum evidence |
|---|---|---|---|
| **NP-CHG-01** | Drift classification | Classify drift before remediating it. Not every difference from baseline is a defect | Drift diff, assigned severity, recorded disposition |
| **NP-CHG-02** | Immutable change artifact | Every write executes from an artifact recorded before approval and unchanged after it | Artifact contents and integrity checksum |
| **NP-CHG-03** | Approval and authority | A ticket, a named approver at an authority level matching the risk class, an expiry, and a permitted window | Approval record linked to the artifact |
| **NP-CHG-04** | Pre-execution revalidation | Re-check identity, current state, checksum, approval validity, and scope immediately before execution — not at approval time | Revalidation log entry from the executing run |
| **NP-CHG-05** | Post-change verification | Verify the resulting state after every write. Verification is mandatory and has no bypass path | Verification output and final status |
| **NP-CHG-06** | Rollback or escalation | A recovery path is chosen and tested before the change runs, not designed during the incident | Rollback test evidence, or a documented escalation route where rollback is not possible |

**Where the reasoning lives:** [Detecting and Handling Configuration Drift Safely](../production-grade-network-automation-principles/detecting-and-handling-configuration-drift-safely.md) (01), [Remediation Packs](../production-grade-network-automation-principles/remediation-packs.md) (02, 04, 05), [Human-in-the-Loop Automation Design](../production-grade-network-automation-principles/human-in-the-loop-automation-design.md) (03), [Rollback Strategies](../production-grade-network-automation-principles/rollback-strategies-what-works-and-what-doesnt.md) (06).

---

## NP-EVD — Evidence and Observability

What the run leaves behind, and whether anyone can read it.

| ID | Control | Requirement | Minimum evidence |
|---|---|---|---|
| **NP-EVD-01** | Audit record | Requestor, action, target, approval, result, and verification are correlated into one traceable record | Audit sample from a real run |
| **NP-EVD-02** | Operational logging | Structured logs sufficient to support the service, with secrets and unnecessary sensitive configuration redacted | Log sample plus a redaction test |
| **NP-EVD-03** | Operator-friendly output | Run output states what was checked, what changed, what failed, and why, in terms a duty engineer can act on without reading the code | Run summary and reason-code distribution |
| **NP-EVD-04** | Provenance | Every operational claim carries its source and the timestamp that source was read | Output examples showing source attribution |
| **NP-EVD-05** | Observability | Health, success rate, failure rate, latency, and dependency health are exposed and alerted on | Dashboard definitions and alert tests |

Keep NP-EVD-01 and NP-EVD-02 logically separate. Audit answers *who did what, and was it allowed*. Operational logging answers *why did it break*. Conflating them produces a stream that is too noisy to audit and too sparse to debug.

**Where the reasoning lives:** [Building Audit-Ready Automation](../production-grade-network-automation-principles/building-audit-ready-automation.md) (01), [Structured Logging](../tutorials/intermediate/structured-logging-network-automation.md) (02), [Making Automation Output Operator-Friendly](../production-grade-network-automation-principles/making-automation-output-operator-friendly.md) (03, 04), [DevOps and Observability](../tutorials/expert/devops-observability-network-automation.md) (05).

---

## NP-GOV — Governance and Lifecycle

The controls that decide whether the service should still exist.

| ID | Control | Requirement | Minimum evidence |
|---|---|---|---|
| **NP-GOV-01** | Risk classification | A recorded risk class with the rationale behind it, reviewed when scope changes | Classification record and approver |
| **NP-GOV-02** | Three-owner model | Service, technical, and operational ownership are each named — as people or roles, not as a team | Named owners in the service record |
| **NP-GOV-03** | Service register entry | Registered before production acceptance, and maintained after material change | Register entry with mandatory fields complete |
| **NP-GOV-04** | Lifecycle gates | Applicable gates passed, with evidence retained at a depth proportionate to risk class | Gate decision records |
| **NP-GOV-05** | Documentation and handover | Purpose, execution flow, error conditions, recovery, and support route documented well enough to transfer | Repository documentation and runbook |
| **NP-GOV-06** | Exception management | Deviations are documented, approved at the right authority level, and time-bound | Exception register entry with expiry |
| **NP-GOV-07** | Recertification | Ownership, access, risk, dependencies, and continued value reviewed on a risk-based cadence | Service review output with decisions |

**Where the reasoning lives:** [Enterprise Control Matrix](../production-grade-network-automation-principles/enterprise-control-matrix.md) (01), [Automation Service Lifecycle](../production-grade-network-automation-principles/automation-service-lifecycle.md) (02, 03, 04, 05, 07), [Exception and Waiver Process](../production-grade-network-automation-principles/exception-and-waiver-process.md) (06).

---

## NP-AI — Governed AI

Constraints on what a model is permitted to be, regardless of how well it behaves in testing.

| ID | Control | Requirement | Minimum evidence |
|---|---|---|---|
| **NP-AI-01** | Approved interfaces only | The model reaches operational systems only through approved governed tools | Enabled-tool inventory, reviewed and dated |
| **NP-AI-02** | Human accountability | A named human owner remains accountable for what the agent does. The agent is never the accountable party | Ownership record |
| **NP-AI-03** | No arbitrary execution | No generic command, script, or API-proxy capability exists — enabled or otherwise | Tool schemas and rejection tests |
| **NP-AI-04** | Evidence before opinion | Observed facts are separated from recommendations. No invented state, tickets, approvals, or results | Sample transcripts and validation tests |
| **NP-AI-05** | Approval enforcement outside the model | The model cannot bypass, satisfy, or self-issue an approval requirement | Negative approval tests |
| **NP-AI-06** | AI risk class recorded | The agent's class is recorded and revisited whenever a tool is added or a schema widened | Classification in the service record |

**Where the reasoning lives:** [Governed AI for Network Operations](../governed-ai-network-operations/index.md) (01, 02, 04), [Why Your Agent Must Not Have an execute_command Tool](../governed-ai-network-operations/why-your-agent-must-not-have-execute-command.md) (03, 05), [AI Risk Classification](../governed-ai-network-operations/ai-risk-classification.md) (06).

---

## NP-TOOL — Tool Boundary

How a capability is exposed, whether the caller is an agent or a person.

| ID | Control | Requirement | Minimum evidence |
|---|---|---|---|
| **NP-TOOL-01** | Tool approval | Purpose, owner, risk class, and scope approved before the tool is enabled anywhere | Tool approval record |
| **NP-TOOL-02** | Narrow by construction | Each tool exposes one specific capability, not a configurable gateway to many | Tool catalogue review |
| **NP-TOOL-03** | Strict schemas | Typed inputs, enumerations rather than free text, length limits, and rejection of unknown parameters | Schema definitions and rejection tests |
| **NP-TOOL-04** | Scope enforcement in the service | Caller claims map to permitted tools, actions, and target scopes, enforced in code rather than in a prompt | Role-scope matrix and authorisation tests |
| **NP-TOOL-05** | Structured output contract | Status, correlation ID, tool version, resolved target, source timestamps, observed facts, warnings, and whether anything changed | Example output and contract tests |
| **NP-TOOL-06** | Categorised errors | Every failure carries a category that determines what the caller should do next | Error taxonomy and failure tests |
| **NP-TOOL-07** | Invocation audit | Complete invocation context and outcome recorded, including attempts to use tools that are not enabled | Audit sample including a denied attempt |
| **NP-TOOL-08** | Tool lifecycle | Draft, approved, enabled, deprecated, and retired states managed explicitly, with migration announced before removal | Tool catalogue with states and dates |

**Where the reasoning lives:** [Designing the Tool Catalogue](../governed-ai-network-operations/tool-catalogue-design.md) (01, 02, 08), [Tool Contracts and Failure Modes](../governed-ai-network-operations/tool-contracts-and-failure-modes.md) (03, 05, 06, 07), [From Script to Tool](../governed-ai-network-operations/from-script-to-tool.md) (04).

---

## NP-PLAT — Platform and Delivery

Deliberately generic. How you satisfy these depends heavily on what your organisation already runs, and this catalogue does not assume a platform.

| ID | Control | Requirement | Minimum evidence |
|---|---|---|---|
| **NP-PLAT-01** | Restricted runtime | Automation runs with least privilege, as a non-privileged identity, with only the network reach it needs | Runtime security configuration |
| **NP-PLAT-02** | Trusted artifacts | Images and packages are scanned, immutable, and traceable to a source you trust | Digest, scan result, provenance record |
| **NP-PLAT-03** | Runtime secret retrieval | Secrets are referenced by identifier and fetched at runtime. Never embedded in code, configuration, images, logs, or documentation | Secret-store references, repository and image scans |
| **NP-PLAT-04** | Dependency control | Dependencies declared, locked, scanned for known vulnerabilities, and pruned when unused | Lock file and dependency scan |
| **NP-PLAT-05** | Reproducible promotion | Build once, promote the same artifact through environments, keep environment configuration separate | Pipeline run and immutable artifact reference |
| **NP-PLAT-06** | Pipeline assurance | Formatting, linting, type checking, security scanning, and tests run before anything is promoted | Pipeline results |

**Where the reasoning lives:** [Secrets and Credentials in Enterprise Automation](../production-grade-network-automation-principles/secrets-and-credentials-in-enterprise-automation.md) and [Secure Credential Vaulting](../tutorials/expert/secure-credential-vaulting.md) (03), [Python Engineering Standard](./python-engineering-standard.md) (04, 06).

---

## Applicability by Risk Class

A starting map, not a rule. Classify the service first, then decide applicability control by control and record the reasoning either way.

| Risk class | Families that apply |
|---|---|
| **R0 — Informational** | NP-CORE, NP-EVD, NP-GOV, plus NP-PLAT where the service is deployed rather than run ad hoc |
| **R1 — Advisory** | R0 plus NP-CHG-01, and NP-TOOL where the output is consumed by another system |
| **R2 — Controlled execution** | R1 plus NP-TOOL in full |
| **R3 — Change automation** | R2 plus NP-CHG in full |
| **R4 — High-impact or autonomous** | Everything, plus formal risk acceptance and a documented kill control |
| **Any class, with an agent involved** | Add NP-AI in full, at the [AI risk class](../governed-ai-network-operations/ai-risk-classification.md) the agent holds |

---

## Maintenance Rules

The value of a catalogue is entirely in the stability of its identifiers. Four rules protect that:

- **Identifiers never change meaning.** Once published, `NP-CHG-04` means what it meant on the day it was published.
- **Retired identifiers are not reused.** A gap in the numbering is information; a recycled code is a trap for anyone reading an old assessment.
- **Materially new requirements get new identifiers,** even when they sit close to an existing one.
- **Clarifications may keep an identifier** where the intent genuinely has not changed. Rewording for readability is a clarification. Adding a condition is not.

---

## Using This in Your Own Documents

The catalogue is published under [CC-BY 4.0](../../legal/licensing.md), so you are free to adopt the identifiers directly, including commercially, with attribution. Two reasonable approaches:

**Adopt as-is.** Reference `NP-CORE-02` in your designs and cite this page. Cheapest option, and it means anyone joining your team can read the reasoning without you having to write it first.

**Fork the numbering.** Copy the families into your own catalogue under your own prefix, keeping a mapping column back to these identifiers. More work, but it lets you add organisation-specific controls without your numbering drifting away from a public source.

What does not work is adopting the codes without adopting the requirements. A design that cites `NP-CHG-05` while leaving verification optional is worse than one that cites nothing, because it claims an assurance that is not there.

---

## Continue

- Next: [Assessing Yourself Against These Controls](./self-assessment.md)
- Standards Index: [Automation Standards](./index.md)
- The reasoning behind the controls: [Production-Grade Network Automation Principles](../production-grade-network-automation-principles/index.md) · [Governed AI for Network Operations](../governed-ai-network-operations/index.md)
