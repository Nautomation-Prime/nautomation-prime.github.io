---
title: Custom Script Build
description: A specific network automation task, built to a fixed scope and fixed price. Production-grade Python, fully documented, with full source code ownership.
tags:
  - SMB
  - Custom Script
  - Bespoke Automation
  - Python
  - Cisco
---

## Custom Script Build

### Your Specific Problem, Solved to a Fixed Scope

Not every automation need fits a pre-defined pack. If you have a specific, well-defined task you need automating — and the existing packages don't cover it — this is how we scope and deliver it.

A Custom Script Build is a fixed-scope, fixed-price bespoke automation engagement. You describe the problem; we scope it, price it, build it, document it, and deliver it.

---

## How It Works

**Step 1 — Describe Your Problem**

Send us a brief description of what you're trying to automate. It doesn't need to be technical. "We currently spend 2 hours manually configuring VLANs across 30 switches every time a new department is added" is sufficient.

[Email us →](mailto:enquiries@nautomationprime.io)

**Step 2 — Free Scope Document**

We produce a written scope document at no charge. This defines exactly:

- What the script does and doesn't do
- What inputs it accepts (e.g. a CSV file, command-line arguments)
- What outputs it produces (e.g. a report, a log file, direct device configuration)
- What platforms and device types it targets
- Any assumptions or dependencies

You review and approve the scope before any development begins.

**Step 3 — Fixed Price Agreed**

Once the scope is agreed, we confirm a fixed price. No hourly billing. No "it depends". The price does not change unless the scope changes — and scope changes require a new written agreement.

**Step 4 — Build, Test, and Deliver**

We build the script following the [PRIME Philosophy](../../prime-framework/philosophy.md): production-grade error handling, comprehensive inline documentation, proper credential management, and structured logging. You receive the full source code.

**Step 5 — Handover Walkthrough**

A remote session where we walk through what the script does, how to run it, how to interpret its output, and how to make simple modifications if needed.

---

## Examples of Custom Builds

To give you a sense of what falls within this scope:

| Example Task | Complexity | Typical Price |
| :------------ | :--------- | :------------ |
| Bulk VLAN provisioning across access layer | Moderate | £1,200–£1,700 |
| Automated config backup to Git repository | Simple | £800–£1,200 |
| Interface description audit and correction | Simple | £800–£1,000 |
| CDP/LLDP neighbour discovery report | Simple–Moderate | £900–£1,400 |
| ACL deployment across a defined device group | Moderate | £1,200–£1,700 |
| Port security configuration and audit | Moderate | £1,200–£1,700 |
| Custom compliance check for a specific policy | Simple–Moderate | £900–£1,500 |
| Multi-step provisioning workflow (e.g. new VLAN + SVI + ACL) | Complex | £1,700–£2,000 |
| Automated inventory report to Excel/CSV | Simple | £800–£1,100 |
| SNMP polling and threshold alerting | Moderate | £1,200–£1,700 |

*These are indicative ranges. Exact price is confirmed in the scope document.*

---

## Pricing

| Complexity | Price Range |
| :---------- | :---------- |
| **Simple** — Single task, small fleet, standard CLI output or report | £800 – £1,200 |
| **Moderate** — Multi-step logic, multiple device types, formatted report output | £1,200 – £1,700 |
| **Complex** — Multi-stage workflow, validation loops, conditional branching, custom data handling | £1,700 – £2,000 |

**What affects complexity?**

- Number of distinct steps in the workflow
- Number of device platforms (IOS-XE only vs. mixed IOS/IOS-XE/NX-OS)
- Error handling requirements (simple vs. conditional retry/rollback logic)
- Output format requirements (plain text vs. HTML report vs. CSV vs. API call)
- Integration with external systems (Git, ITSM, email, SNMP manager)

---

## What Every Custom Build Includes

Regardless of complexity tier, every delivery includes:

- ✅ Written scope document (approved before development starts)
- ✅ Production-grade error handling and exception management
- ✅ Structured logging with timestamps and per-device outcomes
- ✅ Secure credential handling (no hardcoded passwords; environment variables or vault file)
- ✅ Comprehensive inline documentation (every function, every significant block explained)
- ✅ README with installation, configuration, and usage instructions
- ✅ Full source code ownership — no licence fees, no lock-in
- ✅ 30-minute handover walkthrough
- ✅ 30 days post-delivery support for questions and minor issues

---

## Technical Prerequisites

Requirements vary by task and are confirmed during scoping. Typical prerequisites:

- Python 3.9+ on a management workstation or jump host
- SSH/API access to target devices from that host
- Credentials with appropriate privilege level for the task
- Device inventory (hostnames or IPs)

---

## Turnaround

**1–3 weeks** from scope agreement, depending on complexity.

- Simple tasks: typically 5–7 business days
- Moderate tasks: typically 8–12 business days
- Complex tasks: typically 12–15 business days

---

## Frequently Asked Questions

**What if my requirements aren't clear enough to scope?**

That's fine — the scoping process is where we work it out together. The [Automation Opportunity Assessment](./automation-assessment.md) can help if you're unsure whether your problem is automatable, or which process to tackle first.

**What if I need changes after delivery?**

The 30-day post-delivery support covers questions and minor issues (e.g. a device type behaving differently than expected in testing). Functional changes or new requirements after delivery are scoped as a new engagement.

**Can you build something that integrates with our ticketing system or CMDB?**

Yes, if the system has an API. Common integrations include ServiceNow, Jira, and CSV-based CMDBs. Confirm the integration target during scoping — this typically adds to the complexity tier.

**What if I already have a partially-written script that needs finishing or fixing?**

That's a valid starting point. Send us what you have, describe what it should do, and we'll scope the work needed to bring it to production quality.

---

[**Request a Scope Discussion →**](mailto:enquiries@nautomationprime.io?subject=Custom%20Script%20Build%20Enquiry){.md-button .md-button--primary} [**View All Packages →**](../services.md){.md-button}
