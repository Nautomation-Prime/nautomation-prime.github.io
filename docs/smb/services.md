---
title: SMB Automation Packages
description: All fixed-price Cisco automation packages for small and medium businesses. Compare scope, pricing, and turnaround times to find the right fit.
tags:
  - SMB
  - Packages
  - Pricing
  - Fixed Price
  - Cisco Automation
---

## SMB Automation Packages — Compare & Choose

All packages are fixed-scope and fixed-price. No hourly billing. No open-ended engagements. You agree the scope upfront; we deliver to it.

---

## Package Overview

| Package | Best For | Turnaround | Price |
| :------- | :-------- | :--------- | :---- |
| [Automation Opportunity Assessment](#automation-opportunity-assessment) | Teams unsure where to start | 3–5 business days | From £99 |
| [Switch Audit & Compliance Pack](#switch-audit--compliance-pack) | Compliance checking across Cisco fleet | 1–2 weeks | £750 – £1,500 |
| [IOS-XE Upgrade Automation Pack](#ios-xe-upgrade-automation-pack) | Upgrading 10–200+ devices safely | 1–2 weeks | £1,200 – £2,500 |
| [Zero-Touch Provisioning Setup](#zero-touch-provisioning-setup) | Auto-configuring new access switches | 2–3 weeks | £1,500 – £3,000 |
| [Custom Script Build](#custom-script-build) | A specific task built to your requirements | 1–3 weeks | £800 – £2,000 |
| [Automation-as-a-Service](#automation-as-a-service) | Ongoing monthly automation | Recurring | £300 – £900/mo |

---

## Automation Opportunity Assessment

**The lowest-risk way to get started.**

You know your team spends too much time on manual tasks. But which ones are worth automating? And what's the realistic payback?

This assessment answers those questions before you commit to anything.

**What's Included:**

- A 45-minute remote scoping call with Christopher
- Analysis of your top 3 most time-consuming manual network processes
- Time-savings and ROI estimate for each
- Prioritised recommendation: which to automate first and why
- Written report delivered as a PDF within 3–5 business days

**What You Get Out of It:**

- A clear business case to take to your manager or budget holder
- Confidence about where automation will genuinely save time
- An honest assessment if automation is unlikely to help (we will say so)
- Direct path to commissioning the right package if you choose to proceed

**Pricing:**

| Scope | Price |
| :---- | :---- |
| Up to 3 processes assessed, written report | £99 |
| Up to 5 processes assessed, expanded report + 30-min follow-up call | £199 |
| Up to 5 processes + informal roadmap for the next 12 months | £299 |

[**Book an Assessment →**](./packages/automation-assessment.md){.md-button .md-button--primary}

---

## Switch Audit & Compliance Pack

**Stop manually checking devices against your security baseline.**

This pack delivers a production-ready Python script that connects to your Cisco fleet, checks every device against a configurable compliance baseline, and produces a clear report of deviations — automatically.

**What's Included:**

- A custom-scoped compliance baseline (you define what "correct" looks like)
- Python script connecting to your devices via SSH (Netmiko-based)
- Per-device compliance report: pass/fail per check, with exact deviation detail
- Executive summary output suitable for audit evidence
- Full source code, documented line-by-line
- 30-minute handover walkthrough

**What It Checks (examples — configurable to your requirements):**

- NTP server configuration
- Syslog server configuration
- AAA/RADIUS/TACACS+ settings
- SSH version and transport restrictions
- Password policy and local user accounts
- Banner messages
- Unused interface shutdown
- VTP mode and domain

**Typical Turnaround:** 1–2 weeks from scope agreement

**Pricing:**

| Fleet Size | Price |
| :--------- | :---- |
| Up to 25 devices | £750 |
| 26–100 devices | £1,100 |
| 101–250 devices | £1,500 |

[**Learn More →**](./packages/switch-audit-pack.md){.md-button .md-button--primary}

---

## IOS-XE Upgrade Automation Pack

**Upgrade your Cisco fleet safely — without spending a weekend doing it manually.**

This pack delivers a production-ready upgrade automation script that stages, validates, upgrades, and verifies your IOS-XE devices in parallel, with automatic rollback if anything goes wrong.

**What's Included:**

- Pre-upgrade health checks (CPU, memory, disk space, reachability)
- Parallel upgrade execution using Nornir (configurable concurrency)
- Image staging and MD5 verification before any device is rebooted
- Post-upgrade verification (version check, interface state, routing table)
- Automatic rollback trigger if post-upgrade checks fail
- Detailed run log per device with timestamps and outcomes
- Full source code, documented line-by-line
- 30-minute handover walkthrough

**Typical Turnaround:** 1–2 weeks from scope agreement

**Pricing:**

| Fleet Size | Price |
| :--------- | :---- |
| Up to 25 devices | £1,200 |
| 26–75 devices | £1,700 |
| 76–200 devices | £2,500 |

[**Learn More →**](./packages/ios-xe-upgrade-pack.md){.md-button .md-button--primary}

---

## Zero-Touch Provisioning Setup

**New access switches that configure themselves the moment they're plugged in.**

This pack designs and implements a Zero-Touch Provisioning (ZTP) solution for your environment — so when a new switch is racked, cabled, and powered on, it automatically downloads its configuration and comes up fully provisioned, without an engineer touching it.

**What's Included:**

- ZTP architecture design for your environment (DHCP scope, TFTP/HTTP server options)
- Python-based provisioning script hosted on your server or lightweight VM
- Device template library for your standard switch roles (access, distribution, etc.)
- Basic inventory integration (device registers itself on first boot)
- Test and validation on a lab device before production rollout
- Runbook for ongoing use by your operations team
- Full source code, documented line-by-line
- 45-minute handover walkthrough

**Typical Turnaround:** 2–3 weeks from scope agreement

**Pricing:**

| Scope | Price |
| :---- | :---- |
| Single site, single switch role template | £1,500 |
| Multi-role templates (e.g. access + distribution) | £2,200 |
| Multi-site with inventory integration | £3,000 |

[**Learn More →**](./packages/ztp-setup.md){.md-button .md-button--primary}

---

## Custom Script Build

**A specific automation task, built to a fixed scope, for a fixed price.**

Not every automation need fits a pre-built pack. If you have a specific, well-defined task you want automated — this is how we scope and deliver it.

**Examples of Custom Builds:**

- Bulk VLAN provisioning across your access layer
- Automated configuration backup to a Git repository
- Interface description auditing and correction
- CDP/LLDP neighbour discovery and topology report
- ACL deployment across a defined device group
- Port security configuration and audit
- Custom compliance check for a specific policy requirement

**How It Works:**

1. You describe the problem and what you want the script to do
2. We produce a fixed scope document (included free of charge)
3. You approve the scope and we agree a fixed price
4. We build, test, document, and deliver
5. Handover walkthrough included

**Pricing:**

| Complexity | Price |
| :---------- | :---- |
| Simple (single task, small fleet, standard output) | £800 – £1,200 |
| Moderate (multi-step logic, multiple device types, report output) | £1,200 – £1,700 |
| Complex (multi-stage workflow, validation loops, custom data handling) | £1,700 – £2,000 |

*Exact price confirmed in the scope document before work begins.*

[**Learn More →**](./packages/custom-script-build.md){.md-button .md-button--primary}

---

## Automation-as-a-Service

**Ongoing monthly automation — the tasks that need to run every day, every week, every month.**

Some automation isn't a one-off. Config backups, compliance audits, and inventory reports need to run on a schedule — reliably, automatically, without someone remembering to kick them off.

Automation-as-a-Service provides a managed, recurring automation capability for SMBs that don't have the in-house resource to run and maintain it themselves.

**Monthly Service Options:**

| Tier | What's Included | Monthly Price |
| :---- | :-------------- | :------------ |
| **Essentials** | Weekly config backups to Git, monthly compliance audit report | £300/mo |
| **Standard** | Daily config backups, weekly compliance audits, monthly inventory report | £500/mo |
| **Advanced** | Daily backups, weekly compliance audits, monthly inventory + change-diff report, quarterly review call | £750/mo |
| **Custom** | Tailored to your specific requirements | From £300/mo |

**What's Not Included:**

- Hosting infrastructure (a lightweight VM or cloud instance is required — we advise on setup)
- Access switch hardware

**Minimum Commitment:** 3 months

[**Learn More →**](./packages/automation-as-a-service.md){.md-button .md-button--primary}

---

## All Packages Include

Regardless of which package you choose:

- ✅ Fixed price agreed before work starts
- ✅ Written scope document for your approval
- ✅ Full source code ownership — no licences, no lock-in
- ✅ Production-grade error handling and logging
- ✅ Comprehensive inline documentation
- ✅ Handover walkthrough session
- ✅ 30 days of post-delivery support for questions and minor issues
- ✅ Professional Indemnity and Public Liability insurance
- ✅ GDPR-compliant delivery (UK-based)

---

## Ready to Talk?

Not sure which package fits your situation? [Send us an email](mailto:enquiries@nautomationprime.io) with a brief description of what you're trying to solve — we'll suggest the right starting point at no charge.

[**Email Us →**](mailto:enquiries@nautomationprime.io){.md-button .md-button--primary} [**Book an Assessment →**](./packages/automation-assessment.md){.md-button}
