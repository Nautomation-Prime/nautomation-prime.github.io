---
title: Switch Audit & Compliance Pack
description: Automated Cisco compliance auditing for SMBs. A production-ready Python script that checks every device in your fleet against your security baseline and reports deviations — automatically.
tags:
  - SMB
  - Compliance
  - Audit
  - Cisco
  - Network Security
---

## Switch Audit & Compliance Pack

### Stop Manually Checking Devices Against Your Baseline

Compliance audits are important. They're also time-consuming, inconsistent when done manually, and often delayed until a problem forces the issue.

This pack delivers a production-ready Python script that connects to your entire Cisco fleet, checks every device against your configurable security baseline, and produces a clear deviation report — in minutes, not days.

---

## What You Get

**A complete, documented compliance auditing tool, built for your environment:**

- **Custom compliance baseline** — you define what "correct" looks like. We implement it.
- **Python audit script** — connects to all your devices via SSH, runs all checks in parallel
- **Per-device report** — pass/fail per check, with the exact deviation found
- **Fleet summary report** — percentage compliance across your estate, suitable for audit evidence
- **Full source code** — documented line-by-line; no black-box binaries
- **30-minute handover walkthrough** — your team understands how to run it and read the output

---

## What It Checks

The compliance baseline is configurable to your requirements. Common checks include:

**System Configuration:**

- NTP server addresses (correct servers configured, no unauthorised additions)
- Syslog server configuration (correct destinations, correct severity)
- Hostname and domain naming conventions
- Time zone configuration

**Authentication & Access Control:**

- AAA configuration (RADIUS/TACACS+ servers, fallback policy)
- Local user accounts (approved accounts only, no unexpected additions)
- SSH version (SSHv2 enforced, SSHv1 disabled)
- Allowed management protocols (Telnet disabled, HTTPS enforced where applicable)
- Console and VTY line timeout configuration

**Security Hardening:**

- Login banners (correct banner text, unauthorised access warning present)
- Service password-encryption
- No service finger, no service tcp-small-servers
- CDP/LLDP exposure controls
- Unused interface shutdown

**Switching & VLAN:**

- VTP mode and domain name
- Spanning tree mode and portfast/BPDU guard on access ports
- VLAN pruning alignment

*Custom checks can be added to your baseline during scoping.*

---

## Example Output

```
Device: SW-CORE-01 (10.1.0.1)
============================================================
[PASS] NTP servers: 10.0.0.1, 10.0.0.2
[PASS] Syslog server: 10.0.0.50
[FAIL] SSH version: SSHv1 transport enabled — expected: SSHv2 only
[PASS] AAA authentication login default
[FAIL] VTY line timeout: 60 minutes — expected: 10 minutes or less
[PASS] Login banner: present
[PASS] Service password-encryption: enabled
[FAIL] CDP: enabled on Gi0/1 (uplink) — expected: disabled on all edge ports

Compliance Score: 5/8 checks passed (62.5%)
```

```
Fleet Summary
============================================================
Total devices checked: 47
Fully compliant:        31 (66%)
Minor deviations:       12 (26%)
Critical deviations:     4  (8%)

Top deviation: VTY timeout > 10 min — found on 14 devices
```

---

## Pricing

| Fleet Size | Price |
| :--------- | :---- |
| Up to 25 devices | £750 |
| 26–100 devices | £1,100 |
| 101–250 devices | £1,500 |

Price is fixed at the time of scope agreement. Fleet size is the number of devices the script will target.

**What determines fleet tier?**  
The number of devices the script is scoped to audit. You don't need to pay for the full enterprise tier if you only want to audit a subset of your network.

---

## Technical Prerequisites

To deploy this tool, your environment needs:

- Python 3.9+ on a management workstation or jump host with network access to all target devices
- SSH access to all target Cisco devices from that host
- Credentials for an account with `show` command access (read-only is sufficient)
- A device inventory list (hostname or IP, platform type)

No agent installation on network devices. No persistent server required. Runs on demand or scheduled via cron/Task Scheduler.

---

## Turnaround

**1–2 weeks** from scope agreement.

The majority of this time is spent on:

1. Reviewing your existing baseline policies (or helping you define them)
2. Building and testing the script against your device types
3. Validation run against a subset of your fleet before full delivery

---

## Frequently Asked Questions

**Can it run on a schedule automatically?**

Yes. While the core delivery is an on-demand script, we can advise on scheduling via Windows Task Scheduler, cron (Linux), or a lightweight CI/CD trigger. Automated scheduling is included in [Automation-as-a-Service](./automation-as-a-service.md).

**Does it make any configuration changes?**

No. This is a read-only audit tool. It uses SSH to run `show` commands only. No configuration changes are made.

**What if I don't have a documented baseline yet?**

We can work with you to define one during scoping. Many SMBs don't have a formal baseline — the assessment process helps create one. If you're very unsure where to start, the [Automation Opportunity Assessment](./automation-assessment.md) is a good first step.

**Can it cover Catalyst switches and routers?**

Yes. The tool uses Netmiko and supports IOS, IOS-XE, NX-OS, and IOS-XR device types. Mixed-platform environments are supported.

**What format is the report?**

By default, the script outputs a formatted plain-text or HTML report. Optional CSV/JSON output for import into ticketing or ITSM tools can be added during scoping.

---

[**Enquire About This Pack →**](mailto:enquiries@nautomationprime.io?subject=Switch%20Audit%20%26%20Compliance%20Pack){.md-button .md-button--primary} [**View All Packages →**](../services.md){.md-button}
