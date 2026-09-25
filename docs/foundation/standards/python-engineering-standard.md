---
title: Python Engineering Standard
description: The engineering bar for production network automation in Python — the quality pyramid, automated gates, prohibited practices, review expectations, and what done actually means.
tags:
  - Standards
  - Python
  - Engineering
  - Code Quality
  - Enterprise
---

## Python Engineering Standard

There are twenty-five tutorials on this site covering how to write network automation in Python. This page is the other half: what the finished thing has to be before it belongs in production.

It exists because "it works" is where most network automation stops. The script runs, the output looks right, it goes on a scheduler, and that is the last engineering decision anyone makes about it. Two years later it is load-bearing, undocumented, and understood by one person who is on annual leave.

!!! quote "The test this standard is built around"
    **Another suitably skilled engineer can understand, test, deploy, operate, and extend the solution without depending on the person who wrote it.**

Everything below is downstream of that sentence. If a requirement here does not serve it, it is ceremony and you should drop it.

<div class="np-reflection" markdown>
<p class="np-reflection-label">Between the Lines</p>
<p>Cincinnatus is remembered for the part that looks like nothing. Handed absolute power over Rome, he finished the campaign in a fortnight, gave the power back, and returned to his plough. What was admired was not that he had proved indispensable. It was that he took care not to be.</p>
<p>There is a quieter reading of the sentence above. An engineer nobody else can replace is an engineer who cannot be ill, cannot take a holiday without a laptop, and cannot leave. Writing things down so somebody else can pick them up gets filed under professionalism, which undersells it. It is also how you stop being the single point of failure in your own life.</p>
</div>

---

## Scope

This applies to anything that runs against infrastructure and is depended on by someone other than its author: scripts, services, APIs, workers, scheduled jobs, compliance tooling, and the tools behind a [governed agent](../governed-ai-network-operations/index.md).

It does not apply to genuine one-offs and exploration. The line is not size or sophistication — it is whether anyone else relies on it. A forty-line script on a scheduler is in scope. A four-hundred-line investigation you ran once and deleted is not.

The moment an experiment is shared, scheduled, connected to production, or depended upon by someone else, it crosses the line. That is also the point at which it needs a [register entry](../production-grade-network-automation-principles/automation-service-lifecycle.md#what-has-to-be-registered).

---

## The Quality Pyramid

Five levels, in order. Each depends on the one below it, and skipping a level does not work — you cannot make something safe that is not reliable, and observability on top of an unsafe design just gives you a better view of the incident.

| Level | Property | The question it answers |
|---|---|---|
| **5 — Transferable** | Other engineers can support and change it | Can this outlive its author? |
| **4 — Observable** | Logs, metrics, and audit evidence explain its behaviour | Can we tell what it did, and why? |
| **3 — Safe** | Inputs, targets, scope, and approvals are validated | Can it do damage it was not asked to do? |
| **2 — Reliable** | Expected failures and dependency problems are handled | Does it behave predictably when things go wrong? |
| **1 — Functional** | It performs the intended task correctly | Does it work? |

Most automation in most organisations sits at level 1 or 2. The jump that matters commercially is 2 to 3; the jump that matters organisationally is 4 to 5.

---

## Core Engineering Principles

Ten, and they are deliberately short enough to remember:

- **Read-only by default.** Change capability is explicit, never a side effect.
- **Validate before execution.** Cheap checks first, and fail before the connection opens.
- **Verify after execution.** A write you did not confirm is a write you hope happened.
- **Fail safely and predictably.** Bounded, diagnosable, and closed on uncertainty.
- **Design for repeatability.** Running it twice should be safe and boring.
- **Minimise privilege.** Every identity gets what its job needs and nothing adjacent.
- **Protect sensitive information.** In transit, at rest, in logs, in output, in errors.
- **Produce audit evidence.** As a designed output, not a side effect of logging.
- **Separate configuration from code.** Policy and environment are data.
- **Write for maintainers first.** The computer will run anything. A person has to change it.

---

## Project Structure

A predictable shape makes review, testing, and handover cheaper. The specifics matter less than the consistency.

**Required:**

- Production source separated from test code
- Declared and locked dependencies
- Documentation alongside the code, not in a wiki that drifts
- Configuration schemas separate from configuration values
- An explicit entry point — execution is something you invoke, not something that happens on import

**Prohibited:**

- **Import-time operational actions.** Connecting to a device, reading a secret, or calling an API at module import makes the code untestable and unreusable, and it is the single most common reason a script cannot become a [tool](../governed-ai-network-operations/from-script-to-tool.md).
- **Hidden environment dependencies.** If it only runs on one machine, it is not deployable.
- **Personal paths or credentials** anywhere in the tree.
- **Large monolithic scripts.** Reusable logic belongs in modules; a 2,000-line `main()` is a maintenance liability regardless of how well it works.

Where project size justifies it, separate domain logic, integration adapters, configuration, policy, and presentation. Where it does not, do not invent structure for its own sake — a small, clear, single-module tool is better than a badly-motivated package hierarchy.

---

## Automated Quality Gates

Run these in the pipeline, not on someone's laptop. The tools named are defaults, not requirements — equivalents are fine, provided the gate is enforced and its result is visible.

| Gate | Default tool | Expected result |
|---|---|---|
| **Formatting** | Black | No formatting differences |
| **Linting** | Ruff | No unresolved blocking finding |
| **Type checking** | MyPy | Material errors resolved, or formally accepted with rationale |
| **Security scanning** | Bandit | No unacceptable critical finding |
| **Tests** | PyTest | Required suite passes |
| **Coverage** | Coverage.py | Project threshold met, and critical paths covered specifically |
| **Dependency scanning** | Any approved SCA tool | No unacceptable critical vulnerability |

Coverage deserves a note. A percentage threshold on its own is a weak control — it is satisfiable by testing the easy paths. The requirement that matters is the second half: **critical paths covered specifically.** Target resolution, scope enforcement, write paths, and failure handling need tests regardless of what the overall number says.

This is [NP-PLAT-06](./control-catalogue.md#np-plat-platform-and-delivery) in the control catalogue.

---

## Coding Standards

- Follow recognised Python style conventions, enforced by automated formatting rather than review comments
- Meaningful names for modules, classes, functions, and variables
- Type hints on public interfaces and material business logic
- Docstrings on public modules, classes, and functions
- Simple, readable control flow in preference to clever or compressed code
- Structured, specific exceptions rather than broad catch-all handling
- Minimal duplication and no hidden side effects

**Prohibited:**

- **Silent exception swallowing.** A bare `except: pass` around a device interaction converts a failure into a wrong answer.
- **Unexplained magic values.** A timeout of `47` needs a comment or a name.
- **Unbounded loops or retries.** Every retry needs a limit; every wait needs a timeout.
- **Arbitrary code or shell execution.** Constructing a command from input and running it is the pattern the entire [tool boundary](../governed-ai-network-operations/why-your-agent-must-not-have-execute-command.md) argument exists to prevent, and it is no safer when a human supplies the input.

---

## Input, Targeting, and Change

These are covered in depth elsewhere; what follows is the engineering obligation in each case.

| Area | Obligation | Explained in |
|---|---|---|
| **Input validation** | Treat everything external as untrusted — user input, API requests, files, configuration, AI requests. Validate type, required fields, allowed values, length, format, and operational scope before connecting or changing state. Use typed models at boundaries. Reject unknown parameters on anything security-sensitive | [NP-CORE-03](./control-catalogue.md#np-core-targeting-and-execution-safety) |
| **Target verification** | A hostname is not proof. Resolve through an approved source of truth, compare identifiers, collect live identity before direct action, and fail safely when identity cannot be established | [Validating Device Identity](../production-grade-network-automation-principles/validating-device-identity-before-automation-runs.md) |
| **Read operations** | Still governed. Authenticate, authorise, validate scope, apply rate limits and timeouts, return source timestamps, redact what the caller does not need | [Separating Read and Write Phases](../production-grade-network-automation-principles/separating-read-and-write-phases.md) |
| **Change operations** | Read current state, define desired state, confirm eligibility and approval, act from an approved artifact, change only what is required, verify the result, and provide rollback or escalation | [Remediation Packs](../production-grade-network-automation-principles/remediation-packs.md) |
| **Idempotency** | Read, compare, act only on the difference, verify, and report no-change-required as a first-class outcome rather than as silence | [Real-World Idempotency](../production-grade-network-automation-principles/real-world-idempotency-in-network-automation.md) |

---

## Error and Connection Handling

Automation must fail in a way that can be diagnosed from the evidence it leaves.

- Detect errors early, at the cheapest point
- Distinguish validation, authentication, authorisation, target, dependency, and verification errors — they call for different responses
- Set connection *and* read timeouts, always
- Use finite retry limits with exponential backoff, and only where a retry is genuinely safe
- Clean up sessions and resources on every path, including the failure paths
- Support cancellation for anything long-running
- Return meaningful errors that do not leak sensitive detail

Retries deserve particular care in network automation, because the operation you are retrying may have partially succeeded. A retry is safe when the operation is idempotent and you have verified it did not take effect. Otherwise it is a second change.

Further reading: [Error Recovery and Rollback](../tutorials/intermediate/error-recovery-rollback-network-automation.md), [Circuit Breakers and Backpressure](../tutorials/expert/circuit-breakers-backpressure-network-automation.md).

---

## Logging, Audit, and Observability

Three distinct outputs with three distinct audiences. Keeping them separate is what makes each of them usable.

| Output | Contents | Audience |
|---|---|---|
| **Operational log** | Timestamp, severity, workflow, outcome, duration, correlation ID | The engineer debugging it at 2am |
| **Audit record** | Requestor, action, target, approval, result, verification evidence | Whoever has to prove it was allowed |
| **Metrics** | Request rate, success, failure, latency, dependency health | Whoever notices it degrading before users do |

Sensitive information goes in none of them. Monitoring should alert on repeated failures, security denials, and — easily forgotten — **failure to generate audit evidence**, which is itself a control failure.

Further reading: [Structured Logging](../tutorials/intermediate/structured-logging-network-automation.md), [Building Audit-Ready Automation](../production-grade-network-automation-principles/building-audit-ready-automation.md).

---

## Testing

Production automation does not rely on manual testing. Five kinds, and the last two are the ones teams skip.

| Type | Covers |
|---|---|
| **Unit** | Logic, validation, policy evaluation, data models |
| **Integration** | Inventory, controllers, APIs, identity, secret services |
| **Security** | Input abuse, authorisation, scope enforcement, secret protection |
| **Resilience** | Timeout, retry, partial failure, recovery |
| **End-to-end** | Complete request, action, verification, and audit flow |

Security and resilience tests are where the difference between "it works" and "it is safe" actually shows up. A test suite that only proves the happy path proves the least interesting thing about the service.

Further reading: [Testing Network Automation](../tutorials/intermediate/testing-network-automation.md).

---

## Dependencies and Deployment

Dependencies are part of the product:

- Declare and lock runtime and development dependencies
- Use approved package sources
- Scan for known vulnerabilities on a schedule, not once
- Remove unused dependencies
- Define and maintain the Python versions you support
- Record justified version or vulnerability exceptions as [exceptions](../production-grade-network-automation-principles/exception-and-waiver-process.md), with expiry

Deployment:

- Build once, promote the same artifact through environments
- Keep environment-specific configuration outside the artifact
- Record the deployed version and the rollback artifact
- Avoid manual deployment wherever practical

---

## Pull Request Expectations

What a reviewer is actually checking. If a PR cannot satisfy these in the description and the diff, it is not ready.

- Purpose, scope, and risk are clear
- Code is readable and appropriately typed
- Inputs and targets are validated
- Tests cover success *and* failure paths
- No secrets introduced, and no sensitive data added to logs
- Timeouts, retries, and cleanup are bounded
- Documentation and control mappings are updated
- Backward compatibility, release, and rollback have been considered

The reviewer's job is not to find typos. It is to answer one question: *if this breaks at 3am, can the person on call understand it?*

---

## Prohibited Practices

Consolidated, because these are the ones that turn up in incident reviews:

- Hard-coded or embedded credentials
- Unvalidated external input
- Silent exception handling
- Arbitrary command execution
- Unbounded retries or infinite execution loops
- Undocumented bypasses or hidden configuration
- Sensitive data in logs or output
- Deployment of untested changes
- Production changes without appropriate control

---

## Definition of Done

Not "the code is merged". A service is done when:

- Requirements and acceptance criteria are met
- Documentation and knowledge transfer are complete
- Tests and security assurance have passed
- Logging, observability, and audit are implemented and verified
- Ownership, support route, recovery, and rollback exist and are recorded
- The applicable reviews are complete

Where any of these cannot be met, that is an [exception](../production-grade-network-automation-principles/exception-and-waiver-process.md) — with the waived requirement named, the rationale and risk recorded, compensating controls in place, an owner, an approver, and an expiry date.

Not a to-do item. Those get lost; exceptions get reviewed.

---

## Continue

- Previous: [Assessing Yourself Against These Controls](./self-assessment.md)
- Next: [Governed Automation Reference Architecture](./reference-architecture.md)
- Standards Index: [Automation Standards](./index.md)
- Learn the material: [Tutorials](../tutorials/index.md) · [Production-Grade Network Automation Principles](../production-grade-network-automation-principles/index.md)
