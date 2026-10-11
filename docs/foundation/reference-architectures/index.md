---
title: Reference Architectures
description: Designs rather than tutorials — target-state architectures for governed network automation, with the reasoning behind every boundary and an honest path from a small proof of concept to the full model.
tags:
  - Reference Architecture
  - Architecture
  - Security
  - Enterprise
---

## Reference Architectures

The tutorials on this site teach you to build something. The principle tracks argue a position. The standards give you something to cite.

The pages in this section do a fourth job. Each describes a **design**: a complete target state, the reason every boundary sits where it does, and how to get there from wherever you are now without pretending the first step is the destination.

A reference architecture is not a product and not a recipe. You will not finish one of these pages with working code. You should finish it able to look at your own automation estate and say, specifically, which parts of the design are missing and what each gap allows.

---

## What Is Here

<div class="grid cards" markdown>

-   ### Trusted Automation Execution

    Zero Trust principles applied to privileged automation. Your automation has valid credentials — this asks whether you should trust the automation itself, and puts an independent decision in front of every privileged run.

    [Read the architecture](./trusted-automation-execution/index.md)

-   ### Governed Automation Reference Architecture

    The estate-level view: seven layers with explicit responsibilities, four integration patterns, and how to record a deliberate deviation. It lives with the [Automation Standards](../standards/index.md), because it is what a solution design is reviewed against.

    [Read the architecture](../standards/reference-architecture.md)

</div>

---

## How the Two Fit Together

They answer different questions at different altitudes.

| | Governed Automation Reference Architecture | Trusted Automation Execution |
|---|---|---|
| **Question** | Which layer is responsible for what? | Should *this* run be allowed to exercise *this* authority, now? |
| **Altitude** | The whole automation estate | The moment privileged automation executes |
| **Subject** | Services, layers, integration patterns | The requester, the workload, the artefact, and the privilege it is given |
| **Typical use** | Reviewing a solution design | Designing the boundary in front of a runner, a pipeline, or an agent |

The second sits inside the first. In the governed architecture, the governed service layer decides, orchestration executes, and security services issue the credentials. Trusted Automation Execution is a close-up of that hand-off: what evidence has to exist, and in what order, before a credential reaches the code that will use it.

---

## How These Relate to the Rest of the Foundation

| If you want to… | Go to |
|---|---|
| Learn to write the automation itself | [Tutorials](../tutorials/index.md) |
| Understand why a specific control matters | [Production-Grade Network Automation Principles](../production-grade-network-automation-principles/index.md) |
| See what changes when an AI agent is the requester | [Governed AI for Network Operations](../governed-ai-network-operations/index.md) |
| Cite a requirement, or assess yourself against it | [Automation Standards](../standards/index.md) |

Like the rest of the Foundation, these pages are published in full under [CC-BY 4.0](../../legal/licensing.md). Adopt the designs, adapt them, or argue with them in your own documents, with attribution.

---

## Continue

- Start here: [Trusted Automation Execution](./trusted-automation-execution/index.md)
- Foundation home: [Nautomation Prime Foundation](../index.md)
