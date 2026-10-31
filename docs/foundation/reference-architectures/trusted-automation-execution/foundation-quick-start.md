---
title: Foundation Quick-Start
description: Trusted Automation Execution for a small team — six steps, in order, to a working Foundation-profile deployment, each with a test that tells you it is done, and an honest account of what you will own afterwards.
image: assets/social/trusted-automation-execution.png
image_alt: "Trusted Automation Execution: a reference architecture from the Nautomation Prime Academy"
tags:
  - Reference Architecture
  - Zero Trust
  - Security
  - Getting Started
  - Small Teams
---

## Foundation Quick-Start

The rest of this section describes the whole architecture. This page is for a team that wants to start, and does not have a platform team, a policy engine, or a budget for new products.

It takes you to the [Foundation profile](./adoption-profiles.md#profile-a-foundation): a hardened runner in front of your automation, a default-deny policy, secrets released only after a decision, and evidence of every run. Foundation is a real control and a real improvement on implicit trust. It is not High-Assurance, and the [adoption profiles](./adoption-profiles.md) explain the difference.

!!! tip "What you need before you start"
    One Linux host you can harden and dedicate to running automation. A Git repository for the policy and the workloads. Somewhere to keep secrets that is not a file next to the script — even a local secrets store is a start. A lab, or devices you can practise on. And a few privileged scripts you already run, because those are what you are about to put behind a decision.

---

## The Six Steps

Each step lists what to do, the test that tells you it is done, and the [modules](./architecture.md#the-module-catalogue) it puts in place. Do them in order: each one relies on the one before.

### 1. Find your privileged automation

List every place automation uses a privileged credential: every script, scheduled job, pipeline variable, and shared service account. For each, record its owner, what it can reach, and its [risk class](../../production-grade-network-automation-principles/enterprise-control-matrix.md#automation-risk-classification).

Then pick where to start. Choose one read-only workload, R0 or R1, for the first pass. It lets you build the whole path without the risk of a change, and it will still catch real problems.

**Done when:** every privileged credential your automation uses appears on the list, with an owner, and you have chosen the first workload.

**Modules:** none yet. This is phase 0 of the [adoption roadmap](./adoption-profiles.md#adoption-roadmap), and the step most teams skip. It usually turns up more than anyone expected.

### 2. Give the workload an identity it cannot fake

Write a manifest for the workload: its name, version, risk class, the capabilities it needs, the platforms it supports, and — for any operation that changes something — whether rollback is safe for it. Record the workload's SHA-256 digest. Store the manifest's expected values and the digest somewhere the workload, and the people who run it, cannot write.

**Done when:** changing one character of the workload changes its digest, and you can show that the expected digest lives outside anything the workload can modify.

**Modules:** artefact trust (6), at its simplest. The manifest and digest also stand in for a dedicated workload identity (10), which is acceptable at this profile and listed as a gap.

### 3. Put a runner and a default-deny policy in front

Write a small runner that is the only way the workload is ever executed. It reads the request, checks the workload's digest against the expected one, evaluates a policy file, and starts the workload only on an allow. The policy file lives in Git, is reviewed like code, and denies anything it does not explicitly permit. Missing evidence means deny.

Give every request a Job ID when the runner accepts it. Use the [canonical request](./interface-contracts.md#2-canonical-request) and [decision](./interface-contracts.md#3-decision) contracts as the shape of what the runner reads and decides, even though everything happens on one host. It is what lets you replace the runner later without rewriting the rest.

**Done when:** the runner refuses a modified workload, an unknown workload, a capability the manifest does not declare, and a target that is not allowed, and each refusal records a reason.

**Modules:** request / trigger (1), intent normalisation (3), the trust gateway (7), and the controlled execution environment (9), all inside one runner on one host. That is what Foundation looks like. The modules still exist; they are just small.

### 4. Release secrets only after an allow

Take every credential out of the workload, its configuration files, and its environment. Put them in the secrets store. Change the runner so that it retrieves the credential only after the policy has said yes, and hands it to the workload in memory. Then rotate every credential the workload used to hold, because the old copies still exist somewhere.

**Done when:** a search of the workload, its configuration, and the runner host finds no credential; and with the secrets store unavailable, the run fails safe instead of falling back to anything.

**Modules:** the secret broker (11). The "fails safe" test is the one that matters. A fallback added "for resilience" quietly turns the whole design back into the old one.

### 5. Fence the network and the targets

Configure the runner host's firewall so it can reach only the management addresses of the allow-listed targets, and the few services it needs. Keep the target allow-list in a protected file in Git, standing in for a source of truth. On the devices, limit the automation account to the commands its role needs: local device RBAC, recorded as a compensating control because there is no AAA platform yet. Restrict device management access to the runner's address.

**Done when:** the workload cannot connect to an address outside the allow-list even when it tries directly, and the automation account cannot run a command outside its role.

**Modules:** source of truth (4) as an allow-list, the network boundary (12), device authorisation (13) as a compensating control, and target systems (15). Both checks are physical. A mistake in the policy file no longer means access to everything.

### 6. Record, validate, and decide the outcome

Make every run write a structured evidence record under its Job ID, using the [evidence event](./interface-contracts.md#8-evidence-event) fields, and copy it somewhere off the runner host that the workload cannot reach. Write a separate validation script, running read-only with its own credential, that checks the result and returns PASS, FAIL, DRIFT, UNKNOWN, or PARTIAL. Have the runner record an explicit terminal [outcome](./interface-contracts.md#7-outcome) for every run, including denied ones and ones that never started.

**Done when:** a run that exits successfully but leaves the wrong state is recorded as failed, and you can reconstruct any run — who asked, what was decided, what ran, what was found — from its Job ID alone.

**Modules:** the target adapter (14), which at this profile is the workload's own connection code; independent validation (16); outcome handling (17); and observability and evidence (18).

---

## Prove It

Six steps give you the shape. A test suite gives you the proof.

Write the thirteen cases from the [proof of concept's test matrix](./proof-of-concept.md#demonstration-and-test-matrix) as automated tests: the one that must be allowed, and the twelve that must be refused or blocked. Run them on every change to the runner, the policy, or a workload.

**You are at Foundation when all thirteen pass.** Until then, you have a runner that has been shown allowing things, which is not the same as a boundary.

---

## What You Now Own

Be honest with yourself about this part. Foundation is not something you install. It is a small amount of software and configuration that you now operate:

- **The runner,** which is the most trusted code you have. Review changes to it more carefully than changes to any workload, and keep its tests passing.
- **The policy file and the digest list.** Anyone who can edit them can approve their own workload. Protect them like credentials: changes through Git, reviewed by someone other than the author.
- **The runner host.** Its security is the security of everything it runs. Patch it, restrict who can log in, and rebuild it rather than letting it drift.
- **The evidence copy.** If it lives where the runner can delete it, it is a convenience, not evidence.

None of this is large. All of it is yours.

---

## Traps to Avoid

| Trap | Why it undoes the work |
|---|---|
| **A fallback credential "for resilience"** | From that day, the secrets store is optional and the design is a suggestion |
| **Editing the policy on the runner host** | It skips review, and leaves the Git copy wrong. The next deploy reverts it, or worse, does not |
| **The runner becoming a shared admin box** | Every person with a shell on it can bypass everything it enforces |
| **Skipping validation for read-only work** | A read can still go wrong, and a read is still privileged access |
| **Adding workloads before the tests pass** | Each new workload is one more thing trusted by a boundary nobody has proved |

---

## What Comes Next

When Foundation is working and its tests pass, three upgrades buy the most. They take you to the [Integrated profile](./adoption-profiles.md#profile-b-integrated):

1. **Signing.** Replace the stored digest with a signed release, so approving a workload no longer depends on protecting a file.
2. **Enterprise identity and a central secrets platform.** Requests come from real identities, and secrets stop living on the runner host.
3. **An approval workflow** for anything R3 and above, bound to the workload version and the targets.

The [adoption roadmap](./adoption-profiles.md#adoption-roadmap) covers the full path beyond that. The trust model does not change along the way. Only the strength of each module does.

---

## Continue

- Previous: [Adoption Profiles](./adoption-profiles.md)
- Next: [Operating Model](./operating-model.md)
- Section index: [Trusted Automation Execution](./index.md)
