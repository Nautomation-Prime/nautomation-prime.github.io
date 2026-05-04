---
title: IOS-XE Upgrade Automation Pack
description: Safe, parallelised IOS-XE upgrades across your Cisco fleet. Pre-flight checks, staged execution, automatic rollback — without spending a weekend doing it manually.
tags:
  - SMB
  - IOS-XE
  - Upgrade
  - Cisco
  - Fleet Management
---

## IOS-XE Upgrade Automation Pack

### Upgrade Your Cisco Fleet Safely — Without Spending a Weekend Doing It Manually

Upgrading IOS-XE manually across 20, 50, or 100+ devices means hours of repetitive, high-risk work. One missed pre-check, one wrong image, one interrupted transfer — and you're troubleshooting at midnight.

This pack delivers a production-ready upgrade automation script that handles pre-flight checks, parallel image staging, controlled upgrades, and post-upgrade verification — with automatic rollback if anything goes wrong.

---

## What You Get

**A complete, safe IOS-XE upgrade automation tool, built for your fleet:**

- **Pre-upgrade health checks** — CPU, memory, disk space, reachability, current software version
- **Image staging with MD5 verification** — image is transferred and verified before any device is rebooted
- **Parallel execution** — Nornir-based concurrency (you control how many devices upgrade simultaneously)
- **Post-upgrade verification** — version check, interface state, routing table, management reachability
- **Automatic rollback trigger** — if post-upgrade checks fail, the script flags the device for manual review and halts further upgrades to that batch
- **Detailed run log** — per-device timestamps, step outcomes, and error messages
- **Full source code** — documented line-by-line; no black-box binaries
- **30-minute handover walkthrough** — your team understands how to run, configure, and interpret the output

---

## How the Upgrade Process Works

The script follows a strict, safety-first sequence for each device:

```
1. Pre-flight checks
   ├── Ping reachability
   ├── SSH connectivity
   ├── Current IOS-XE version (skip if already on target)
   ├── Available disk space
   └── CPU and memory within safe thresholds

2. Image staging
   ├── Transfer target image to device flash
   └── MD5 hash verification (abort if mismatch)

3. Upgrade trigger
   ├── Set boot variable to target image
   ├── Save running configuration
   └── Reload device

4. Post-upgrade verification (after reconnect)
   ├── SSH reachability confirmed
   ├── IOS-XE version matches target
   ├── All previously-up interfaces are up
   └── Default route / routing table sanity check

5. Outcome recording
   ├── PASS → device marked complete in run log
   └── FAIL → device flagged, further upgrades paused for that batch
```

---

## Concurrency and Safety Controls

You control the risk level:

| Concurrency Setting | Effect |
| :------------------ | :----- |
| 1 (sequential) | One device at a time — slowest but lowest blast radius |
| 3–5 (recommended) | Small batches — good balance of speed and safety |
| 10+ (fast) | Parallel batches — suitable for access layer with low individual risk |

Recommended approach: upgrade core and distribution devices sequentially (1–2 at a time), access layer in small batches (3–5).

---

## Pricing

| Fleet Size | Price |
| :--------- | :---- |
| Up to 25 devices | £1,200 |
| 26–75 devices | £1,700 |
| 76–200 devices | £2,500 |

Price is fixed at the time of scope agreement. Fleet size is the number of devices in scope for the upgrade script.

---

## Technical Prerequisites

- Python 3.9+ on a management workstation or jump host with SSH access to all target devices
- Management network access to all devices being upgraded
- Target IOS-XE image accessible from the management host (SCP or TFTP to device)
- Read/write credentials (privilege 15 or equivalent) for upgrade execution
- Device inventory list (hostname or IP, platform type, current and target version)

---

## Turnaround

**1–2 weeks** from scope agreement.

Typical timeline:

1. **Scope review (Day 1–2)** — confirm device types, platforms, target image, credential handling approach
2. **Development and unit testing (Day 3–7)** — script built and tested against representative device types
3. **Lab / staging validation (Day 8–10)** — tested against your environment before production use
4. **Delivery and handover (Day 10–14)**

---

## Frequently Asked Questions

**What if a device fails to come back after upgrade?**

The script's post-upgrade checks detect this. If SSH reachability fails within the timeout window, the device is flagged in the run log as requiring manual intervention. Remaining batch devices are paused. The script does not attempt to fix a failed device — that's by design.

**Can it roll back to the previous image automatically?**

Automatic rollback depends on your platform and whether the original image is still on flash. The script can be scoped to trigger a reload with the previous boot variable if the post-upgrade checks fail — this is an optional scope addition discussed during planning.

**Does it support stacked switches?**

Yes, Catalyst stacks and StackWise configurations are supported. The pre-flight and post-upgrade checks account for stack member state.

**Can I run it in dry-run mode first?**

Yes. The script includes a `--dry-run` flag that executes all pre-flight checks and reports what would happen — without transferring any image or triggering any reload.

**What Cisco platforms are supported?**

The script supports IOS-XE platforms (Catalyst 9000 series, ISR, CSR/ASR). IOS (non-XE), NX-OS, and IOS-XR can be scoped as additions — [contact us](mailto:enquiries@nautomationprime.io) to discuss.

**What about credential security?**

Credentials are never hardcoded. The script reads credentials from environment variables or an encrypted vault file at runtime. Full guidance on credential handling is included in the documentation.

---

[**Enquire About This Pack →**](mailto:enquiries@nautomationprime.io?subject=IOS-XE%20Upgrade%20Automation%20Pack){.md-button .md-button--primary} [**View All Packages →**](../services.md){.md-button}
