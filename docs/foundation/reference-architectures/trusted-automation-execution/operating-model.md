---
title: Operating Model
description: Running Trusted Automation Execution across teams — who owns each module, how workloads are onboarded, recertified, and retired, policy as code, running the gateway at scale, the metrics that show it working, and the exercises that prove it.
image: assets/social/trusted-automation-execution.png
image_alt: "Trusted Automation Execution: a reference architecture from the Nautomation Prime Academy"
tags:
  - Reference Architecture
  - Zero Trust
  - Governance
  - Operations
  - Enterprise
---

## Operating Model

In a small team, one person can own every module. In a large organisation, the modules belong to different teams — identity, security, platform, network, change — and that is where adoption usually stalls. Not on the technology, but on the question nobody answered: *whose is this?*

This page is the organisational half of the architecture. It assigns ownership, defines how a workload enters and leaves the system, treats policy as code, describes running the gateway at scale, and says what to measure.

!!! tip "The rule behind all of it"
    **Every module has exactly one accountable team.** A module with no owner is a finding. A module with two owners usually has none.

---

## Who Owns What

A typical split. Your team names will differ; the rule that each module has one accountable owner should not.

| Module | Accountable | Contributes |
|---|---|---|
| **1. Request / trigger** | Automation platform team | Service management team, for ITSM intake |
| **2. Requester identity** | Identity team | Security, for authentication requirements |
| **3. Intent normalisation** | Automation platform team | Workload owners, for operation definitions |
| **4. Source of truth** | The source-of-truth owners (network data, IPAM, CMDB) | Network engineering |
| **5. Change governance** | Change management | Security, for risk-based approval rules |
| **6. Artefact trust** | DevSecOps or the build platform team | Workload owners, for tests and dependency hygiene |
| **7. Trust gateway** | Automation platform team, for the gateway | Security, for policy approval (see [policy as code](#policy-as-code)) |
| **8. Orchestration** | Automation platform team | Workload owners, for workflows |
| **9. Controlled execution environment** | Platform or cloud team | Security, for baselines and runtime detection |
| **10. Workload identity** | Identity team | Platform team, for federation |
| **11. Secret / PKI broker** | Security, or the secrets platform team | Automation platform team, for just-in-time integration |
| **12. Network boundary** | Network security | Platform team, for execution-environment rules |
| **13. Device AAA** | Network engineering, or the AAA platform team | Security, for command-set review |
| **14. Target adapter** | Automation platform team, for the framework | Network engineering, for platform-specific adapters |
| **15. Target systems** | Network engineering | Platform and DDI owners, for non-network targets |
| **16. Independent validation** | Automation platform team, for the framework | Workload owners, for the checks themselves |
| **17. Outcome handling** | Automation platform team | Change management and incident management |
| **18. Observability and evidence** | Security operations | Automation platform team, for the event library |

Two roles cut across the table.

- **Workload owners** own their workloads end to end: the manifest, the operation declarations and rollback decisions, the validation checks, the tests, and recertification. They do not own the modules their workload passes through.
- **The automation platform team** owns the components no product provides — the request service, the gateway, the adapter framework, the execution controller, and the evidence library. That makes it the team holding the most trusted code in the organisation, and it should be staffed and reviewed accordingly.

---

## A Workload's Life

### Onboarding

A workload is onboarded once, deliberately, and every later run depends on that record being right.

| Step | What happens | Owner |
|---|---|---|
| **1. Register** | The workload is recorded as a service: owner, purpose, risk class, target profile, and the profile it will run at | Workload owner |
| **2. Declare** | The manifest and every operation declaration, including parameters, pre-flight checks, safeguards, and whether rollback is safe | Workload owner |
| **3. Build** | The release goes through the controlled build: tests, scans, signing, provenance | Workload owner, on the build platform |
| **4. Grant** | A policy change granting the workload its capability and target scope, reviewed and approved under [policy as code](#policy-as-code) | Workload owner proposes; security approves |
| **5. Provision** | Workload identity, device AAA identity and command set, secret references, and network rules are created — each scoped to this workload | Identity, network, security, and platform owners |
| **6. Prove** | Contract tests and the workload's own tests, including the prohibited paths, pass in a non-production environment | Workload owner |
| **7. Release** | First production run under observation, against a small scope | Workload owner, with change management |

**A workload is live when its grant, its identities, its network rules, and its evidence all trace back to one registration record.** Anything that does not is either a leftover or a back door.

### Recertification

Trust decays. A workload is recertified on a cycle set by its risk class, more often for R3 and R4 than for read-only work, and whenever one of these happens:

- its owner changes or leaves
- a new major version is released
- AAA accounting shows granted commands it never uses, so its grant can shrink
- it is involved in an incident, a denial pattern, or a break-glass event
- a dependency it relies on is deprecated or found vulnerable

Recertification confirms the owner, the risk class, the grant, and the identities, and removes anything no longer needed. A workload that cannot be recertified is suspended, not left running on its old approval.

### Retirement

Retiring a workload is the reverse of onboarding, and it is the step most often skipped. Remove its policy grant, revoke its workload and AAA identities, delete its secret references and network rules, and quarantine its artefacts. Keep its evidence for the retention period. The [Automation Service Lifecycle](../../production-grade-network-automation-principles/automation-service-lifecycle.md) covers the wider lifecycle this fits into.

---

## Policy as Code

Policy is the most powerful configuration in the system: a policy change can grant any workload anything. It is therefore treated as code, with stricter rules than most code.

| Practice | What it means |
|---|---|
| **Separation of duties** | Workload owners propose grants. Security approves them. The author of a change never approves it, and the gateway team cannot grant its own workloads |
| **Every grant has tests** | Each grant ships with an allow test and the deny tests around it: the capability it does not include, the target just outside its scope, the version it does not cover |
| **A golden decision suite** | A fixed set of requests with known correct decisions, run against every policy change. A change that alters a decision nobody meant to alter fails the build |
| **Shadow evaluation** | A new policy version is first evaluated alongside the current one, without enforcing, and every difference in decision is reviewed before it goes live |
| **Signed, versioned releases** | Policy is published as signed bundles. Every decision records the version that made it, so any past decision can be explained with the policy as it stood |
| **Restricting is fast; granting is reviewed** | Deny-lists, revocations, and emergency stops have a fast, pre-approved path. New or wider grants never do |

The last row is the one that matters most in an incident. Withdrawing trust should take minutes. Extending it should take review.

---

## Running the Gateway at Scale

At Foundation, the gateway is a runner on one host. At enterprise scale, it is a production service that every privileged run in the organisation depends on.

| Concern | Approach |
|---|---|
| **Availability** | A stateless decision tier, scaled horizontally, with job state in a replicated store. Engineer it for the availability the automation behind it needs: if automation is part of incident response, the gateway is as critical as the systems it repairs |
| **Degraded behaviour** | Fail closed. When a dependency is down, privileged runs stop, and the [break-glass route](./architecture.md#10-keep-trust-withdrawable) — designed and exercised in advance — is the only way through |
| **Rate limits** | Per requester, per workload, and per agent, so a runaway pipeline or agent cannot flood the gateway, or the targets behind it |
| **Multi-tenancy** | Policy divided into domains per team, with delegation boundaries: one team can grant its own workloads against its own targets, and cannot grant anything against another team's |
| **Evidence pipeline** | A bounded local buffer with back-pressure. For read-only work, events can queue briefly. For changes, if evidence cannot be committed, the run does not start |
| **Its own supply chain** | The gateway is built, signed, and released with the strictest controls in the organisation, and changes to it require the same separation of duties as policy |
| **Its own administration** | A separate administrative plane, behind privileged access management, logged and reviewed. A gateway administrator in their everyday role cannot grant themselves anything |

---

## What to Measure

Metrics that show whether the architecture is working, not just whether it is running.

| Metric | What it tells you | Healthy signal |
|---|---|---|
| **Coverage** | The share of privileged automation that runs through the gateway | Every R3 and R4 workload; known, shrinking exceptions for the rest |
| **Bypasses found** | Privileged access to targets that did not come through the gateway, found through AAA accounting or network logs | Zero, investigated every time |
| **Workloads by profile against risk class** | Whether each workload runs at the profile its risk calls for | Gaps are recorded exceptions with owners and expiry dates, and they age out |
| **Denials by reason code** | What the gateway is refusing, and why | Stable and explainable. A spike means misconfiguration or an attack, and both need attention |
| **Escalations** | How many requests need a human decision, and how long that takes | Decisions within the window; few expiring unanswered |
| **UNKNOWN validation rate** | How often the validator cannot see the result | Low, and falling. A rising rate is a validator coverage problem |
| **Time to revoke** | How long it takes to stop a workload, publisher, or requester, measured in exercises | Minutes, not hours |
| **Break-glass use** | How often the emergency route is used, and how quickly each use is reviewed | Rare, and every use reviewed |
| **Unused capabilities** | Granted commands or operations a workload never uses, from AAA accounting | Falling, as grants are trimmed at recertification |
| **Evidence completeness** | The share of runs that can be reconstructed end to end from their Job ID | All of them |
| **Time to onboard** | How long a new workload takes to go live | Short enough that nobody is tempted to work around it |

The last metric is easy to forget and important. If onboarding takes months, people build automation outside the system, and the coverage metric starts to fall for reasons nobody reports.

---

## Exercises

A control that has never been exercised is a hope. Run these on a regular cadence, in a non-production environment first, and record the results as evidence.

| Exercise | What it proves |
|---|---|
| **Revocation drill** | A workload, a publisher, and a requester can each be withdrawn within the target time, and in-flight runs stop |
| **Break-glass drill** | The emergency route works, is logged, and triggers review, and normal operation resumes cleanly afterwards |
| **Policy service outage** | Privileged runs fail closed, and nothing falls back to a standing credential |
| **Secrets platform outage** | Runs fail safe before execution, with a clear outcome |
| **Evidence sink outage** | High-risk runs stop; read-only runs buffer within their limit and then stop |
| **Validator blindness** | An unreachable target produces UNKNOWN, and UNKNOWN produces the right outcome rather than a pass |
| **Confirmed-commit revert** | On each platform and software release, a deliberate timeout reverts the change completely |

These are the [failure behaviours](./threat-and-failure-model.md#failure-behaviour), turned into something you can show an auditor.

---

## Organisational Traps

| Trap | What happens | The counter |
|---|---|---|
| **The platform team becomes the bottleneck** | Every new workload waits on one team, and people route around it | Self-service onboarding against clear contracts; the platform team reviews, not builds |
| **Policy sprawl** | Hundreds of one-off grants nobody understands | Grant patterns per workload type, and recertification that removes what is unused |
| **Approval fatigue** | Approvers rubber-stamp, because everything needs approval | Standard changes for small, reversible operations, so human attention goes where risk is |
| **Exceptions without expiry** | Temporary gaps become permanent architecture | Every exception has an owner and an expiry date, and the metric above tracks their age |
| **Shadow automation** | Scripts with their own credentials appear outside the system | Bypass detection from AAA and network logs, and onboarding fast enough that nobody needs to |

---

## Continue

- Previous: [Foundation Quick-Start](./foundation-quick-start.md)
- Next: [Worked Example: Azure and Cisco](./worked-example-azure-cisco.md)
- Section index: [Trusted Automation Execution](./index.md)
