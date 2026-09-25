---
title: Capstone Project — Build a Config Deployment Pipeline
description: A seven-chapter capstone that combines YAML, Pydantic, Jinja2, Nornir, PyATS, structured logging and rollback into one production-shaped deployment pipeline.
tags:
  - Capstone
  - Tutorials
  - Project
  - Production
  - Network Automation
---

## Capstone Project: Build a Config Deployment Pipeline

## "Everything You've Learned, in One Codebase That Actually Ships"

Every tutorial up to this point taught one thing well. You can model intent in YAML, validate it with Pydantic, render it with Jinja2, deploy with Nornir, verify with PyATS, log in JSON and roll back when something breaks.

What you probably can't do yet is put them in a line and have them hold.

That's what this capstone is for. Over seven chapters you build **one project**, in **one repository**, that takes a YAML description of what a site should look like and turns it into a proven, audited change on real devices. Each chapter adds one layer and ends with something you can run.

---

## 🧭 What You're Building

`netpipe` — a small, honest deployment pipeline. Not a framework, not a product; roughly the size of tool a two-person automation team would actually write and maintain.

```
intent (YAML)
   ↓  chapter 2 — validate, or refuse to continue
typed models
   ↓  chapter 3 — render, diff, get a human to look
candidate config
   ↓  chapter 4 — credentials, reachability, pre-flight gates
cleared to deploy
   ↓  chapter 5 — push with Nornir, retry and audit via decorators
applied change
   ↓  chapter 6 — prove it with PyATS, independently
verified state
   ↓  chapter 7 — roll back on failure, write the evidence
audit record
```

Read that column of arrows again: each one is a gate. Nothing moves to the next stage unless the previous stage succeeded. That's the actual lesson of the capstone, and it's a structural one — no individual technique on this site teaches it, because it only exists in the joins.

---

## 📚 The Chapters

### [Chapter 1 — Intent and Repository Layout](./01-intent-and-repository-layout.md)

Set up the project skeleton and write the YAML that describes a site. Decide what belongs in data and what belongs in code — the decision every subsequent chapter depends on.

**You'll run:** a loader that prints your site back to you.
**Builds on:** [YAML Data Modelling](../intermediate/yaml-data-modeling-network-automation.md)

---

### [Chapter 2 — Validating Intent](./02-validating-intent.md)

Turn the YAML into typed Pydantic models with your naming standards, VLAN rules and design constraints encoded. Make bad intent impossible to deploy.

**You'll run:** `netpipe validate` — passing on good intent, refusing with a readable report on bad.
**Builds on:** [Pydantic Data Validation](../intermediate/pydantic-data-validation-network-automation.md), [JSON Data Handling](../intermediate/json-data-handling-network-automation.md)

---

### [Chapter 3 — Rendering Configuration](./03-rendering-configuration.md)

Generate candidate configs with Jinja2, diff them against what's currently on the device, and produce a change plan a human can review before anything is pushed.

**You'll run:** `netpipe plan` — a unified diff per device, and a summary of what would change.
**Builds on:** [Jinja2 Configuration Templates](../intermediate/jinja2-configuration-templates.md)

---

### [Chapter 4 — Credentials and Pre-Flight](./04-credentials-and-preflight.md)

Get secrets out of the codebase, then add the gates that run before any write: reachability, identity, config register, free flash, and no competing change in progress.

**You'll run:** `netpipe preflight` — a pass/fail table per device.
**Builds on:** [Credential Management](../intermediate/credential-management-network-automation.md), [Health Checks and Pre-Flight Validation](../intermediate/health-checks-pre-flight-validation.md)

---

### [Chapter 5 — Deploying with Nornir](./05-deploying-with-nornir.md)

Push the change in parallel, with retry, rate limiting and audit logging supplied by decorators. Batch the rollout so a bad template can't take a whole site with it.

**You'll run:** `netpipe deploy` — in batches, with a dry-run mode you'll use far more often.
**Builds on:** [Nornir Fundamentals](../intermediate/nornir-fundamentals.md), [Decorators in Network Automation](../intermediate/decorators-network-automation.md)

---

### [Chapter 6 — Proving the Change with PyATS](./06-proving-the-change-with-pyats.md)

Verify independently. Not by re-reading your own configuration lines, but by learning operational state with Genie and comparing it against a snapshot taken before the change.

**You'll run:** `netpipe verify` — a state diff, and a clear verdict.
**Builds on:** [PyATS Fundamentals](../intermediate/pyats-fundamentals.md), [PyATS Network Validation](../intermediate/pyats-network-validation.md)

---

### [Chapter 7 — Rollback and the Audit Record](./07-rollback-and-audit.md)

Wire failure to automatic rollback, and emit a structured JSON record of what was intended, what was done, what was proven and who approved it. Finish the pipeline.

**You'll run:** `netpipe run` — the whole thing, end to end, with an audit artefact at the finish.
**Builds on:** [Error Recovery and Rollback](../intermediate/error-recovery-rollback-network-automation.md), [Structured Logging](../intermediate/structured-logging-network-automation.md), [State Management and Idempotency](../intermediate/state-management-idempotency-network-automation.md)

---

## 📋 Prerequisites

This capstone assumes the intermediate track, particularly the data modelling quartet. You don't need to have finished every reliability tutorial — each chapter links back to the one it draws on, and you can read that page when you get there.

### Required Knowledge

- ✅ The data modelling quartet: [YAML](../intermediate/yaml-data-modeling-network-automation.md), [JSON](../intermediate/json-data-handling-network-automation.md), [Pydantic](../intermediate/pydantic-data-validation-network-automation.md), [Jinja2](../intermediate/jinja2-configuration-templates.md)
- ✅ [Nornir Fundamentals](../intermediate/nornir-fundamentals.md) — inventories and tasks
- ✅ [PyATS Fundamentals](../intermediate/pyats-fundamentals.md) — testbeds and Genie parsing
- ✅ Comfortable with Python packages, virtual environments and `argparse`

### Required Software

```bash
python -m venv netpipe_venv
source netpipe_venv/bin/activate
# Windows PowerShell: .\netpipe_venv\Scripts\Activate.ps1

pip install "pydantic>=2.0" pydantic-settings pyyaml jinja2 \
            nornir nornir-netmiko nornir-utils netmiko \
            pyats[library] rich
```

### Required Access

Two or more Cisco IOS-XE devices you are allowed to configure. **Use a lab.** CML, EVE-NG, GNS3 or a pair of spare switches on a bench — this project writes configuration, and chapters 5 to 7 are considerably more instructive when you can safely break something.

Every chapter also has a dry-run path that works with no devices at all, so you can read and build along without a lab and come back to the execution chapters later.

---

## 🏗️ Where You'll End Up

```
netpipe/
├── intent/
│   └── man1.yaml                 # what the site should be
├── netpipe/
│   ├── models.py                 # ch2 — the data contract
│   ├── settings.py               # ch4 — credentials and config
│   ├── render.py                 # ch3 — intent to candidate config
│   ├── diff.py                   # ch3 — candidate vs running
│   ├── preflight.py              # ch4 — the gates
│   ├── deploy.py                 # ch5 — the write phase
│   ├── verify.py                 # ch6 — independent proof
│   ├── rollback.py               # ch7 — undo
│   ├── audit.py                  # ch7 — the evidence
│   └── cli.py                    # the operator's front door
├── templates/
│   └── access_switch.j2
├── inventory/                    # Nornir
├── tests/
└── artefacts/                    # snapshots, diffs, audit records
```

Around 800 lines of Python by the end. Small enough to read in a sitting, structured enough to extend.

---

## 🎯 How to Work Through This

1. **Build it, don't read it.** Type the code. The chapters are written to be followed with a terminal open.
2. **Go in order.** Chapter 5 deploys what chapter 3 rendered from what chapter 2 validated. Skipping leaves you with missing imports.
3. **Run the dry-run paths first**, every time, even once you have a lab. That habit is half the point.
4. **Substitute your own network.** The examples use a two-switch access layer because it's small. Your VLANs, your naming standard and your templates will be different, and the pipeline shape won't change.

!!! tip "Already Have Scripts in Production?"
    You don't have to build `netpipe` to get value here. Read chapter 2 and chapter 6 and compare them against what your current scripts do at those two points — validation before, proof after. Those are the two stages most working automation is missing, and they're the two that decide whether a change is safe or merely finished.

---

<div class="np-reflection" markdown>
<p class="np-reflection-label">Between the Lines</p>
<p>Odysseus wanted to hear the Sirens and knew he could not be trusted to. So he had himself lashed to the mast, stopped his crew&rsquo;s ears with wax, and ordered in advance that no later order of his was to be obeyed. The plan works precisely because it does not rely on his judgement at the moment it matters.</p>
<p>A pipeline is mostly refusals: seven stages, and six exist to stop something &mdash; bad data, an unreviewed diff, an unreachable device, a failed push, an unproven outcome, a change nobody can account for afterwards. The stage doing the actual work is one line in the middle. That ratio feels wrong when you first build it, as though you have written a great deal of machinery to avoid doing very little. It stops feeling wrong the first night the refusals are what stand between you and an outage you would otherwise be explaining in the morning.</p>
</div>

---

## 📖 Related Reading

- **[Production-Grade Network Automation Principles](../../production-grade-network-automation-principles/index.md)** — The reasoning behind each gate in this pipeline
- **[Separating Read and Write Phases](../../production-grade-network-automation-principles/separating-read-and-write-phases.md)** — Why plan and deploy are different commands
- **[Building Audit-Ready Automation](../../production-grade-network-automation-principles/building-audit-ready-automation.md)** — What chapter 7 is really producing
- **[Deep Dive: Cisco Config Generator](../../deep-dives/cisco-config-generator.md)** — A production tool built on the same pattern, at full scale
- **[Expert Tutorials](../expert/index.md)** — Where to go once the pipeline works

---

> **Remember:** The individual techniques are the easy part. The engineering is in the joins — what each stage refuses to pass on.

[← Back to Tutorials](../index.md) | [Start Chapter 1 →](./01-intent-and-repository-layout.md)
