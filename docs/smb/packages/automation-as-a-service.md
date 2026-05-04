---
title: Automation-as-a-Service
description: Monthly recurring network automation for SMBs. Config backups, compliance audits, and inventory reports — running automatically every day, every week, every month.
tags:
  - SMB
  - Automation-as-a-Service
  - Recurring
  - Managed Service
  - Config Backup
  - Compliance
---

## Automation-as-a-Service

### The Tasks That Need to Run Every Day — Without Someone Remembering to Start Them

Some automation isn't a one-off. Config backups need to run nightly. Compliance audits need to run weekly. Inventory reports need to be up to date before your next change window.

But running and maintaining scheduled automation reliably takes time and internal resource that most SMB teams don't have spare.

Automation-as-a-Service provides a managed, recurring automation capability — running on a lightweight server or VM in your own environment, delivering consistent outputs without manual intervention.

---

## What It Is

A monthly service where we:

1. **Deploy** the automation tooling to a server or VM you provide
2. **Configure** the scheduled tasks to run on your defined schedule
3. **Maintain** the tooling — updating device inventories, adjusting schedules, fixing issues as they arise
4. **Report** on what ran, what succeeded, and what needs attention each month

You get the automation running reliably. We manage the upkeep.

---

## Service Tiers

| Tier | What's Included | Monthly Price |
| :---- | :-------------- | :------------ |
| **Essentials** | Weekly config backups to Git, monthly compliance audit report | £300/mo |
| **Standard** | Daily config backups to Git, weekly compliance audit report, monthly inventory report | £500/mo |
| **Advanced** | Daily config backups, weekly compliance audits, monthly inventory + change-diff report, quarterly review call | £750/mo |
| **Custom** | Tailored to your specific requirements | From £300/mo |

---

## What Each Task Delivers

### Configuration Backups

**What it does:** Connects to every device in your inventory via SSH, pulls the running configuration, and commits it to a Git repository with a timestamped commit message.

**Why it matters:**

- A hardware failure or bad change can be recovered from in minutes if you have last night's config
- Git history gives you a complete change timeline — you can see exactly what changed, on which device, and when
- No more rebuilding from memory or an 18-month-old spreadsheet

**Output:** Git repository with per-device config files and full commit history

---

### Compliance Audit Reports

**What it does:** Checks every device in your inventory against your defined compliance baseline and produces a summary report of deviations.

**Why it matters:**

- Compliance drift accumulates silently — a weekly audit catches it before it becomes a problem
- Evidence of regular auditing is useful for internal governance and any external assessments
- Your team knows the current compliance posture without spending time checking manually

**Output:** HTML or plain-text compliance report, delivered to a shared folder or emailed to a nominated address

---

### Inventory Reports

**What it does:** Connects to all devices, collects hostname, model, serial number, IOS-XE version, uptime, and interface count, and produces a formatted inventory report.

**Why it matters:**

- Always-current inventory without manual spreadsheet updates
- Useful before change windows, procurement planning, or EoL reviews
- Highlights version discrepancies across the fleet at a glance

**Output:** CSV and/or HTML inventory report

---

### Change-Diff Reports *(Advanced tier only)*

**What it does:** Compares this week's configuration backups against last week's and produces a per-device diff report showing exactly what changed.

**Why it matters:**

- Unauthorised or undocumented changes become immediately visible
- Useful for post-change validation ("did that change go on the right devices?")
- Supports change governance without requiring an enterprise ITSM tool

**Output:** Per-device diff report alongside the standard compliance report

---

## What You Provide

- A lightweight Linux VM or Windows Server (4GB RAM, 2 vCPU is sufficient for most SMB fleets)
- Network access from that VM to all managed devices via SSH
- A Git repository (self-hosted Gitea, GitHub, GitLab, Azure DevOps — your choice)
- SSH credentials for the automation account

We advise on VM sizing and Git repository setup at no extra charge.

---

## What We Manage

- Initial deployment and configuration of all automation tooling on your server
- Schedule configuration (cron or Windows Task Scheduler)
- Inventory file updates as devices are added or removed
- Monthly service health check — confirming all tasks completed successfully in the past 30 days
- Minor script updates for compatibility as device software changes
- Email alerts if any task fails to run or produces unexpected results

---

## Pricing and Commitment

| Detail | |
| :------ | :- |
| **Minimum commitment** | 3 months |
| **Notice period for cancellation** | 30 days after minimum term |
| **Billing** | Monthly in advance |
| **Setup fee** | None — included in first month's fee |
| **Onboarding** | Deployment and initial test run typically completed within 5 business days of service start |

---

## Frequently Asked Questions

**Does this require cloud access or an internet connection for the automation to run?**

No. All automation runs within your own network on your own server. An internet connection is only needed if your Git repository is hosted externally (e.g. GitHub). A self-hosted Git option is available if you prefer fully air-gapped operation.

**What if we add new devices to our network mid-service?**

Inventory updates are included. Email us with the new device details and we'll update the inventory within 2 business days.

**What happens if a task fails?**

We monitor task completion as part of the monthly service check. If a task fails, we investigate and fix the cause. You'll be notified if manual intervention is required (e.g. a device has changed credentials or is unreachable).

**Can we see the source code of what's running?**

Yes. All automation tooling deployed under this service is fully documented and visible to you. You own the code at all times — if you cancel the service, the automation continues to run as-is on your server.

**Can we upgrade to a higher tier mid-contract?**

Yes. Tier upgrades take effect from the next billing cycle.

**Is this the same as a managed service provider (MSP) managing our network?**

No. We automate specific, defined tasks — we do not monitor your network, respond to incidents, or manage your infrastructure. This service is specifically for running recurring automation tasks reliably.

---

[**Enquire About Automation-as-a-Service →**](mailto:enquiries@nautomationprime.io?subject=Automation-as-a-Service%20Enquiry){.md-button .md-button--primary} [**View All Packages →**](../services.md){.md-button}
