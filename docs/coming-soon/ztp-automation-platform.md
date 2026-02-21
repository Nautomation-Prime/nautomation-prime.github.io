---
title: ZTP Automation Platform
description: End-to-end enterprise Cisco ZTP solution with Excel-driven config builder, Jinja2 templating, and Day 0/Day N workflows.
tags:
  - Coming Soon
  - ZTP
  - Provisioning
  - Cisco
  - Enterprise
---

# ZTP Automation Platform

!!! abstract "Project Status"
    **Current Phase:** :fontawesome-solid-hammer: **Build Phase**

    This platform is actively under development. Core architecture and workflows are being implemented, including the Excel-driven config builder, Jinja2 templating engine, Day 0/Day N provisioning logic, and device inventory database.

---

## Executive Summary

An end-to-end production-grade Cisco ZTP solution built in Python for enterprise rollouts. This is the fully managed, paid platform version of our upcoming free ZTP script, with a configuration builder, data validation, and lifecycle tracking.

---

## What It Delivers

- **Branded Excel intake** for device, site, and variable data
- **Config Builder upload** that maps spreadsheet fields into Jinja2 templates
- **Day 0 provisioning** to bring devices online and reachable
- **Day N configuration** generation and push after onboarding
- **Device inventory database** created at provisioning time for ongoing automation

---

## Service Model

This is a paid, enterprise-grade service with optional bespoke add-ons by request.

---

## Ideal For

- Large-scale rollouts with strict standardization requirements
- Teams needing repeatable, auditable provisioning workflows
- Organizations that want a managed ZTP platform, not just a script

---

## Optional Add-Ons and Roadmap Ideas

### PyATS validation packs (Day 0 and Day N)

Automated pre/post checks that prove the intended state exists after provisioning and post-change pushes. We capture validation evidence, pass/fail results, and human-readable summaries.

### Golden image compliance

Image staging, checksum verification, and upgrade readiness checks so every device lands on approved firmware. Includes drift reporting and optional auto-remediation paths.

### IPAM/CMDB integrations

Source-of-truth sync with systems like NetBox, Infoblox, or ServiceNow. Keeps inventory, addressing, and device metadata aligned with what is actually deployed.

### Pre-provisioning QA

Network readiness checks for DHCP/DNS reachability, port readiness, and site health before any device is onboarded.

### Change audit trail and governance

Approval workflows, evidence collection, and rollback planning so changes are measurable, reviewable, and repeatable.

---

## PRIME Framework Alignment

- **[Pinpoint](../prime-framework/pinpoint.md)** — Define ZTP scope, device profiles, and rollout boundaries
- **[Re-Engineer](../prime-framework/re-engineer.md)** — Improve templates, validation logic, and onboarding flow based on feedback
- **[Implement](../prime-framework/implement.md)** — Execute Day 0 provisioning and Day N configuration delivery
- **[Measure](../prime-framework/measure.md)** — Track success rates, validation outcomes, and time-to-provision metrics
- **[Empower](../prime-framework/empower.md)** — Provide reusable templates, documentation, and training for teams

---

## Transparency: Inputs, Outputs, and Ownership

We document exactly what the platform consumes, what it produces, and who owns each step.

- **Inputs:** Excel-based device, site, and variable data; approved templates; optional source-of-truth feeds
- **Outputs:** Day 0 bootstrap configs, Day N configs, validation evidence, and inventory updates
- **Ownership:** You own device data and templates; we implement the workflow and provide operational visibility
- **Auditability:** Every push is logged with timestamps, target devices, and validation results
- **Rollback:** Defined rollback points and recovery steps for failed changes

---

**Status:** :fontawesome-solid-hammer: Build Phase
