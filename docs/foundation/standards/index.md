---
title: Automation Standards
description: The reference-grade half of the Foundation — a coded control catalogue, an assessment method, the Python engineering bar, and a vendor-neutral reference architecture.
tags:
  - Standards
  - Governance
  - Controls
  - Architecture
  - Enterprise
---

## Automation Standards

The two principle tracks on this site are written to be **read**. They argue a position, work through failure modes, and try to change how you think about a problem.

These four pages are written to be **referenced**. They are the material you point at in a design document, cite in a waiver, or hand to a security reviewer who has no intention of reading fourteen essays first.

Same content, different job.

---

## What Is Here

<div class="grid cards" markdown>

-   ### Automation Control Catalogue

    Forty-six stable identifiers across seven families, each with its requirement, the minimum evidence it needs, and a link to the page that explains the reasoning.

    [Read the catalogue](./control-catalogue.md)

-   ### Assessing Yourself Against These Controls

    The method — scope, applicability, evidence quality tests, five outcomes, severity, and what closure actually requires. Free and complete.

    [Read the method](./self-assessment.md)

-   ### Python Engineering Standard

    The bar production automation has to clear: the quality pyramid, automated gates, prohibited practices, review expectations, and a definition of done that is not "merged".

    [Read the standard](./python-engineering-standard.md)

-   ### Governed Automation Reference Architecture

    A vendor-neutral target state — seven layers with explicit responsibilities, the four integration patterns, and how to record a deliberate deviation.

    [Read the architecture](./reference-architecture.md)

</div>

---

## How These Relate to the Rest of the Foundation

| If you want to… | Go to |
|---|---|
| Understand *why* a control exists | [Production-Grade Network Automation Principles](../production-grade-network-automation-principles/index.md) |
| Understand what changes when an AI agent is involved | [Governed AI for Network Operations](../governed-ai-network-operations/index.md) |
| Cite a requirement in a document | [Control Catalogue](./control-catalogue.md) |
| Find out where you actually stand | [Self-Assessment](./self-assessment.md) |
| Set the engineering bar for a team | [Python Engineering Standard](./python-engineering-standard.md) |
| Review a solution design | [Reference Architecture](./reference-architecture.md) |
| Learn to write the code in the first place | [Tutorials](../tutorials/index.md) |

The dependency runs one way: the standards pages assume you have read, or can go and read, the reasoning in the tracks. A control code without its argument is just an assertion, and assertions are the thing this site is trying to replace.

---

## A Note on Adoption

These are published in full, under [CC-BY 4.0](../../legal/licensing.md), because a standard nobody can read is not a standard — it is a consulting dependency. You are free to adopt the control identifiers, fork the numbering, or lift the assessment method into your own process, commercially, with attribution.

What we would ask is that you adopt the requirements along with the codes. A design that cites a control while quietly leaving it optional is worse than one that cites nothing at all, because it claims an assurance that is not there.

---

## Getting Help With This

Everything here is free and complete, and most teams can apply it without outside help. Where it is useful to have someone else do it — an independent assessment, findings written up in a form your security and change governance functions will accept, or a control set adapted to an estate that does not fit the defaults — that work is described on the [Services](../../services.md) page, and the [Automation Opportunity Assessment](../../smb/packages/automation-assessment.md) is the smaller-estate version.

---

## Continue

- Start here: [Automation Control Catalogue](./control-catalogue.md)
- Foundation home: [Nautomation Prime Foundation](../index.md)
